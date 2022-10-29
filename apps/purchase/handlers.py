from __future__ import annotations

import datetime
import decimal
import logging
from contextlib import suppress
from pathlib import Path

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, WebAppInfo, Message
from glQiwiApi.qiwi.clients.p2p.types import Bill
from glQiwiApi.qiwi.exceptions import QiwiAPIError

import gls
import settings
from utils import template
from utils.feedback import send_feedback, send_waiting
from utils.input_file_types import BufferedInputFile
from ..search import models as search_models
from ..orders import models as order_models
from ..coupons import models as coupon_models
from ..operator import models as operator_models
from . import callbacks, image_generation

TEMPLATES = Path('apps/purchase/templates')
logger = logging.getLogger(__name__)


async def buy_handler(query: CallbackQuery, callback_data: callbacks.BuySubscriptionCallback, state: FSMContext):
    wm = await send_waiting('⏳ Генерируем счёт...', query.message.chat.id)

    subscription = search_models.Subscription.get(callback_data.sub_id)

    # Coupon stuff
    data = await state.get_data()

    coupon: coupon_models.Coupon | None = None
    coupon_discount = decimal.Decimal(0)

    if coupon_code := data.get('coupon'):
        coupon = coupon_models.Coupon.get_free(coupon_code)
        coupon_discount = subscription.price * decimal.Decimal(coupon.discount / 100)

    commission = max(
        decimal.Decimal(30),
        (subscription.price - coupon_discount) * decimal.Decimal(settings.QIWI_COMMISSION)
    )

    total = subscription.price - coupon_discount - commission

    service = subscription.get_service()

    expire_date = datetime.datetime.now() + datetime.timedelta(seconds=settings.BILL_TIMEOUT_SEC)
    async with gls.qiwi:
        try:
            bill = await gls.qiwi.create_p2p_bill(
                amount=round(total, 2),
                pay_source_filter=settings.QIWI_PAY_METHODS,
                expire_at=expire_date
            )
        except QiwiAPIError as error:
            logger.error(error)
            await wm.delete()
            await query.answer()
            await send_feedback('Ошибка QIWI API, пожалуйста, обратитесь в поддержку', query.message.chat.id)
            return

    render_list = template.render(TEMPLATES / 'bill.xml', {
        'buy_button': {'web_app': WebAppInfo(url=bill.pay_url)},
        'done_button': {'callback_data': callbacks.CheckBillCallback(
            bill_id=bill.id,
            sub_id=subscription.id,
            coupon=coupon.code if coupon else None
        ).pack()},
        'bill': bill,
        'subscription': subscription.name,
        'service': service.name,
        'waiting': False,
        'expired': False
    })

    render = render_list.first()

    bill_items = [(f'Подписка {service.name.upper()} {subscription.name}', subscription.price)]
    if coupon is not None:
        bill_items.append((f'Купон "{coupon.code}" на -{coupon.discount}%', -coupon_discount))
    bill_items.append(('Компенсация комиссии qiwi', -commission))

    render.photo = BufferedInputFile(
        image_generation.render_bill(bill_items, total),
        'bill.png'
    )

    await wm.delete()
    message = await render.send(query.message.chat.id)
    await gls.bot.pin_chat_message(
        query.message.chat.id,
        message.message_id
    )

    await query.answer()


async def check_bill_handler(query: CallbackQuery, callback_data: callbacks.CheckBillCallback, state: FSMContext):
    wm = await send_waiting('⏳ Проверяем счёт...', query.message.chat.id)

    try:
        bill = await gls.qiwi.get_bill_by_id(callback_data.bill_id)
    except QiwiAPIError as error:
        logger.error(error)
        await wm.delete()
        await query.answer()
        await send_feedback(f'Ошибка QIWI API (bill_id: {callback_data.bill_id}), '
                            f'пожалуйста, обратитесь в поддержку',
                            query.message.chat.id)
        return

    if bill.status.value == 'EXPIRED':
        await wm.delete()

        await gls.bot.unpin_chat_message(query.message.chat.id, query.message.message_id)
        await query.message.delete()

        await query.answer()
        await send_feedback('Срок действия счёта истёк', query.message.chat.id)
        return

    if bill.status.value == 'PAID' or settings.DEBUG:
        await bill_paid_handler(query, callback_data, state, bill, wm)
        return

    service_name, subscription_name = search_models.Subscription.get_full_name_parts(callback_data.sub_id)
    render = template.render(TEMPLATES / 'bill.xml', {
        # Buttons are not matter here, cuz we remove keyboard later
        'buy_button': {'callback_data': '...'},
        'done_button': {'callback_data': '...'},

        'bill': bill,
        'subscription': subscription_name,
        'service': service_name,
        'waiting': bill.status.value == 'WAITING',
        'expired': bill.status.value == 'EXPIRED'
    }).first()
    render.keyboard = query.message.reply_markup

    await wm.delete()
    await render.edit(query.message)

    await query.answer()


async def bill_paid_handler(query: CallbackQuery,
                            callback_data: callbacks.CheckBillCallback,
                            state: FSMContext,
                            bill: Bill,
                            wm: Message):
    data = await state.get_data()
    data.setdefault('lock', [])

    if callback_data.sub_id in data['lock']:
        return

    data['lock'].append(callback_data.sub_id)
    await state.set_data(data)

    order = order_models.Order.place(
        callback_data.sub_id,
        decimal.Decimal(round(bill.amount.value, 2)),
        query.from_user.id,
        callback_data.coupon
    )

    if callback_data.coupon:
        coupon_models.Coupon.update_expired(callback_data.coupon)

    keyboard = query.message.reply_markup
    keyboard.inline_keyboard[0].pop(1)
    keyboard.inline_keyboard[0][0].text = 'Об оплате'
    await gls.bot.edit_message_reply_markup(
        query.message.chat.id,
        query.message.message_id,
        reply_markup=keyboard
    )

    subscription = search_models.Subscription.get(order.subscription)
    service = search_models.Service.get(subscription.service)
    position_in_queue = order_models.Order.get_position_in_queue(order.id)
    render = template.render(TEMPLATES / 'success.xml', {
        'order': order,
        'service': service.name,
        'subscription': subscription.name,
        'position_in_queue': position_in_queue
    }).first()

    render.video = service.bought

    await wm.delete()
    message = await render.send(query.message.chat.id)
    await gls.bot.pin_chat_message(
        query.message.chat.id,
        message.message_id
    )

    data['lock'].remove(callback_data.sub_id)
    await state.set_data(data)

    with suppress(TelegramBadRequest):  # May throw an error if query is expired
        await query.answer()

    render = template.render(TEMPLATES / 'notification.xml', {
        'order': order,
        'service': service.name,
        'subscription': subscription.name,
        'position_in_queue': position_in_queue
    })
    for employee in operator_models.Employee.get_to_notify():
        with suppress(TelegramBadRequest):
            await render.send(employee)


async def piq_update_handler(query: CallbackQuery, callback_data: callbacks.PosInQueueCallback):
    order = order_models.Order.get(callback_data.order_id)
    service, subscription = search_models.Subscription.get_full_name_parts(order.subscription)
    position_in_queue = order_models.Order.get_position_in_queue(order.id)
    await template.render(TEMPLATES / 'success.xml', {
        'order': order,
        'service': service,
        'subscription': subscription,
        'position_in_queue': position_in_queue
    }).first().edit(query.message)
    await query.answer()

    await send_feedback('Позиция в очереди обновлена', query.message.chat.id)
