import functools
from dataclasses import dataclass

import aiogram.types
import peewee
from glQiwiApi.qiwi.clients.p2p import types as qiwi_types
from glQiwiApi.qiwi.exceptions import QiwiAPIError

import gls
import pilgram
import response_system as rs
import response_system_extensions as rse
import settings
from apps.botpiska import images
from apps.botpiska.models import Bill, Client, Order, Subscription
from apps.botpiska.services import Service
from apps.coupons.models import Coupon
from libs.events import trigger_embedded_events, Event
from response_system import Response
from utils import do_nothing


async def _order_wrapper(function, user: aiogram.types.User) -> Response:
    """ Производит предварительные действия перед обработкой
        получения заказа """

    # Получение счёта из базы и соответствующего ему счёта qiwi
    try:
        bill = Bill.get_by_id(user.id)
        qiwi_bill = await gls.qiwi.get_bill_by_id(bill.qiwi_id)

    except (peewee.DoesNotExist, QiwiAPIError):
        return rs.feedback(
            'Ошибка получения счёта, пожалуйста, '
            'обратитесь в поддержку'
        )

    # Получение статуса счёта (в DEBUG режиме всегда 'PAID')
    status = settings.DEBUG and 'PAID' or bill.status.value
    # Счёт не оплачен - предупреждаем, что нужно оплатить, чтобы продолжить
    if status == 'WAITING':
        status_message = BILL_STATUSES['WAITING']
        return rs.feedback(status_message)

    # Счёт отменён или его срок истёк - удаляем
    elif status != 'PAID':
        bill.delete_instance()

        status_message = BILL_STATUSES[status]
        return rs.delete(bill.message_id, on_error=do_nothing) + \
            rs.feedback(status_message)

    # Регистрируем пользователя, если не зарегистрирован и
    # устанавливаем его как реферала
    coupon = bill.coupon
    client = Client.get_or_register(
        user.id,
        referral=coupon.sets_referral_id if coupon else None,
        force_referral=True
    )

    return await function(client, bill, qiwi_bill)


def _order_handler(function):
    """ Декоратор, оборачивающий функцию в get_order_wrapper """
    return functools.partial(_order_wrapper, function)


@dataclass
class SelfOrderEvent(Event):
    subscription: Subscription
    order: Order
    bill: Bill


@_order_handler
async def buy_for_user(client: Client, bill: Bill, qiwi_bill: qiwi_types.Bill) -> Response:
    """ Часть логики, относящаяся к покупке подписки для себя """
    order = Order.create(
        client=client,
        subscription=bill.subscription_id,
        coupon=bill.coupon_id,
        paid_amount=qiwi_bill.amount.value,
        created_at=rs.global_time.get()
    )
    client = Client.get(chat_id=client)
    client.award_points(qiwi_bill.amount.value * settings.SEASON_BONUS_PERCENTAGE)

    subscription: Subscription = bill.subscription
    service = Service.get_by_id(subscription.service_id)

    event = SelfOrderEvent(subscription, order, bill)
    await trigger_embedded_events('SELF_ORDERED', event)

    bill.delete_instance()
    return (
        rs.delete(on_error=do_nothing)
        + rse.tmpl_send(service.order_template, {
            'subscription': subscription,
            'order': order
        })
        + rse.tmpl_notify_employee('apps/order_processing/templates/op-message-order-new.xml', {
            'order': order
        })
    )


@_order_handler
async def buy_as_gift_by_user(client: Client, bill: Bill, qiwi_bill: qiwi_types.Bill) -> Response:
    """ Часть логики, относящаяся к покупке подписки в подарок """

    subscription: Subscription = bill.subscription
    gift_coupon = Coupon.from_type(
        subscription.gift_coupon_type_id,
        sets_referral=client.chat_id,
        now=rs.global_time.get()
    )

    gift_card_image = pilgram.PilImageInputFile(
        images.render_gift_card_image(f't.me/{settings.BOT_NAME}?start={gift_coupon.code}'),
        filename='GIFT.png'
    )
    client = Client.get(chat_id=client)
    client.award_points(qiwi_bill.amount.value * settings.SEASON_BONUS_PERCENTAGE)

    bill.delete_instance()
    return (
        rs.delete(on_error=do_nothing)
        + rse.tmpl_send('apps/botpiska/templates/message-gift.xml', {
            'gift-card-image': gift_card_image,
            'subscription': subscription,
            'coupon': gift_coupon,
        })
    )


BILL_STATUSES = {
    'WAITING': (
        'Счёт не оплачен. Оплатите его по кнопке "Оплатить" '
        'и попробуйте снова.'
    ),
    'REJECTED': (
        'Счёт более недействителен, сгенерируйте новый.'
    ),
    'EXPIRED': (
        'Срок действия счёта истёк, сгенерируйте новый.'
    )
}


__all__ = (
    'SelfOrderEvent',
    'buy_for_user',
    'buy_as_gift_by_user'
)
