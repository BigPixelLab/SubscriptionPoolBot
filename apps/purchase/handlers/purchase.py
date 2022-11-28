from __future__ import annotations

import datetime
from contextlib import suppress
from decimal import Decimal
from pathlib import Path

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, WebAppInfo
from glQiwiApi.qiwi.exceptions import QiwiAPIError

import gls
import settings
import resources
from utils import template
from utils.feedback import send_feedback, send_waiting
from apps.user_account import models as user_models
from apps.coupons import models as coupon_models
from apps.search import models as search_models
from utils.input_file_types import BufferedInputFile
from .. import callbacks, image_generation

TEMPLATES = Path('apps/purchase/templates')


async def purchase_handler(
        query: CallbackQuery,
        callback_data: callbacks.BuySubscriptionCallback,
        state: FSMContext
):
    """ ... """
    await query.answer()
    await send_bill_message(
        query.message.chat.id,
        query.from_user.id,
        callback_data.sub_id,
        state
    )


async def service_terms_handler(query: CallbackQuery, callback_data: callbacks.TermsCallback):
    await template.render(resources.resolve(callback_data.service_term).path, {
        'terms': callback_data.service_term
    }).send(query.message.chat.id, silence_errors=False)
    await query.answer()


async def delete_term_message_handler(query: CallbackQuery):
    await query.message.delete()


async def send_bill_message(
        chat_id: int,
        user_id: int,
        subscription_id: int,
        state: FSMContext
):
    """ ... """

    waiting_message = await send_waiting(
        '⏳ Генерируем счёт...',
        chat_id
    )

    # Разбираемся с ранее выставленными счетами.
    # Удаляем неоплаченные и просим довести до
    # конца те, по которым уже пришли деньги.
    # Таким образом, в момент у каждого пользователя
    # может быть открыт всего один счёт.

    if (bill_info := user_models.User.get_last_bill_info(user_id)) and bill_info[0] is not None:
        bill_id, bill_message_id = bill_info

        try:
            bill = await gls.qiwi.get_bill_by_id(bill_id)
        except QiwiAPIError:
            await waiting_message.delete()
            await qiwi_api_error_feedback(chat_id, bill_id)
            return

        if bill.status.value == 'PAID':
            await waiting_message.delete()
            await must_complete_purchase_feedback(chat_id)
            return

        try:
            await gls.qiwi.reject_p2p_bill(bill_id)
        except QiwiAPIError:
            await waiting_message.delete()

        # Не убираем резервацию купона здесь, потому что
        # при генерации счёта, если купон активирован -
        # он всё равно затрётся другим. При отмене
        # активации купона командой, резервация должна
        # сниматься тоже командой

        with suppress(TelegramBadRequest):
            await gls.bot.delete_message(chat_id, bill_message_id)

    # Генерируем новый счёт

    subscription = search_models.Subscription.get(subscription_id)
    service = subscription.get_service()

    userdata = await state.get_data()
    coupon: coupon_models.Coupon | None = None

    # Купон активированный пользователем необязательно
    # может быть в базе, он больше воспринимается
    # как предложение, поэтому такое название
    if suggested_coupon := userdata.get('coupon'):
        # Обновляет информацию об истечении срока годности купона
        # резервирует купон, если есть свободный и возвращает его.
        # Старая резервация при этом затирается.
        coupon = coupon_models.Coupon.get_not_expired(suggested_coupon, user_id)

    # Купон есть, но не действует на данную подписку
    if coupon and coupon.subscription and coupon.subscription != subscription_id:
        coupon_models.Coupon.free_reservation(user_id)
        coupon = None

    # Формирование элементов счёта ##############
    total_price = subscription.price
    bill_items = [(
        f'Подписка {service.name.upper()} {subscription.name}',
        subscription.price
    )]

    if coupon:
        discount = -(total_price * Decimal(coupon.discount / 100))
        total_price += discount
        bill_items.append((
            f'Купон "{coupon.code}" на -{coupon.discount}%',
            discount
        ))

    commission = -(total_price * Decimal(settings.QIWI_COMMISSION))
    total_price -= commission
    bill_items.append((
        'Компенсация комиссии qiwi',
        commission
    ))
    # Конец формирования элементов счёта ########

    expire_at = (
        datetime.datetime.now() +
        datetime.timedelta(seconds=settings.BILL_TIMEOUT_SEC)
    )

    try:
        bill = await gls.qiwi.create_p2p_bill(
            amount=round(total_price, 2),
            pay_source_filter=settings.QIWI_PAY_METHODS,
            expire_at=expire_at
        )
    except QiwiAPIError:
        await waiting_message.delete()
        await qiwi_bill_create_error(chat_id)
        return

    check_callback = callbacks.CheckBillCallback(
        coupon=coupon.code if coupon else None,
        sub_id=subscription.id,
        bill_id=bill.id
    )

    terms_callback = callbacks.TermsCallback(
        service_term=service.term
    )

    render = template.render(TEMPLATES / 'bill.xml', {
        'subscription': subscription.name,
        'service': service.name,
        'bill': bill,

        'waiting': False,
        'minimized': False,  # True после оплаты

        'buy_button': {'web_app': WebAppInfo(url=bill.pay_url)},
        'terms_button': {'callback_data': terms_callback.pack()},
        'done_button': {'callback_data': check_callback.pack()}
    }).first()

    bill_image = image_generation.render_bill(bill_items, total_price)
    render.photo = BufferedInputFile(bill_image, 'bill.png')

    await waiting_message.delete()
    message = await render.send(chat_id)

    # Установка данных о последнем сгенерированном счёте
    user_models.User.set_bill_info(user_id, bill.id, message.message_id)


# MISC STUFF ##################################################################

async def qiwi_api_error_feedback(chat_id, bill_id):
    await send_feedback(
        f'Ошибка QIWI API (bill_id: {bill_id}), '
        f'пожалуйста, обратитесь в поддержку',
        chat_id
    )


async def qiwi_bill_create_error(chat_id):
    await send_feedback(
        'Ошибка создания счёта, пожалуйста, '
        'обратитесь в поддержку',
        chat_id
    )


async def must_complete_purchase_feedback(chat_id):
    await send_feedback(
        'У вас имеется не закрытый оплаченный счёт. '
        'Чтобы сгенерировать новый, сначала '
        'завершите предыдущую покупку нажатием на '
        'кнопку "Готово"',
        chat_id
    )
