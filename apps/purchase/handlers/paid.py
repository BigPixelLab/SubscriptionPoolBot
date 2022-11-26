from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, WebAppInfo, CallbackQuery
from glQiwiApi.qiwi.clients.p2p.types import Bill

import gls
import resources
from utils import template
from apps.search import models as search_models
from apps.orders import models as order_models
from apps.event import models as event_models
from apps.coupons import models as coupon_models
from apps.operator import models as operator_models
from apps.user_account import models as user_models
from utils.feedback import send_feedback
from .. import callbacks

TEMPLATES = Path('apps/purchase/templates')


async def bill_is_paid_handler(
        chat_id: int,
        user_id: int,
        message: Message,
        subscription_id: int,
        coupon: str,
        bill: Bill,
        state: FSMContext
):
    """ ... """

    # Используем lock на основе state, чтобы
    # в случае если кнопка "Готово" нажата
    # много раз, заказ добавился максимум 1

    userdata = await state.get_data()
    userdata.setdefault('lock', [])

    if subscription_id in userdata['lock']:
        return

    userdata['lock'].append(subscription_id)
    await state.set_data(userdata)

    # Всё что ниже гарантированно выполнится
    # ровно 1 раз, для данного заказа

    # Минимизируем сообщение со счётом (также удаляет
    # кнопку "Готово", что очень важно, ибо после того
    # как будет снят lock, повторное нажатие вызовет
    # этот метод ещё раз)
    subscription = search_models.Subscription.get(subscription_id)
    service = subscription.get_service()

    await template.render(TEMPLATES / 'bill.xml', {
        'subscription': subscription,
        'service': service,
        'bill': bill,
        'minimized': True,
        'buy_button': {'web_app': WebAppInfo(url=bill.pay_url)},
    }).first().edit(message)

    # Открываем заказ

    order = order_models.Order.place(
        subscription_id,
        Decimal(bill.amount.value),
        user_id,
        coupon
    )

    # Генерация купона для события "1+1 Spotify"
    one_plus_one_spotify_coupon: str | None = None
    if not coupon and service.name == 'spotify' \
            and event_models.Event.is_going_now('one_plus_one_spotify'):
        one_plus_one_spotify_coupon = coupon_models.Coupon.generate(
            discount=100,
            subscription=subscription_id,
            referer=user_id,
            is_one_time=True
        )

    position_in_queue = None
    if subscription.is_code_required:
        position_in_queue = order_models.Order.get_position_in_queue(
            order.id, service.name
        )

    render = template.render(TEMPLATES / 'success.xml', {
        'order': order,
        'service': service.name,
        'subscription': subscription.name,

        # not None для подписок, требующих очередь
        'position_in_queue': position_in_queue,

        'minimized': False,  # True после обновления, если закрыт

        'one_plus_one_spotify_coupon': one_plus_one_spotify_coupon
    }).first()
    render.video = resources.get(
        service.bought,
        key=gls.bot.id
    )

    message = await render.send(chat_id)
    await gls.bot.pin_chat_message(chat_id, message.message_id)

    # Используем купон, и удаляем его из userdata
    user_models.User.after_purchase(user_id)
    userdata['coupon'] = None

    # Снимаем lock
    userdata['lock'].remove(subscription_id)
    await state.set_data(userdata)

    # Отправляем оповещения операторам

    render = template.render(TEMPLATES / 'notification.xml', {
        'order': order,
        'service': service.name,
        'subscription': subscription.name,
        'position_in_queue': position_in_queue
    })

    for employee in operator_models.Employee.get_to_notify():
        await render.send(employee)


async def position_in_queue_update_handler(
        query: CallbackQuery,
        callback_data: callbacks.PosInQueueCallback
):
    order = order_models.Order.get(callback_data.order_id)
    subscription = search_models.Subscription.get(order.subscription)
    service = subscription.get_service()

    position_in_queue = None
    if subscription.is_code_required and order.closed_at is None:
        position_in_queue = order_models.Order.get_position_in_queue(order.id, service.name)

    await template.render(TEMPLATES / 'success.xml', {
        'order': order,
        'service': service,
        'subscription': subscription,

        # not None для подписок, требующих очередь
        'position_in_queue': position_in_queue,

        'minimized': order.closed_at is not None,

        'one_plus_one_spotify_coupon': None
    }).first().edit(query.message)

    await query.answer(
        f'Вы #{position_in_queue} в очереди'
        if position_in_queue else
        ''
    )
    await send_feedback(
        'Позиция в очереди обновлена',
        query.message.chat.id
    )
