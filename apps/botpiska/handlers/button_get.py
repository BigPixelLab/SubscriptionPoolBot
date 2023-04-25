""" ... """
from __future__ import annotations

import functools

import aiogram.types
import peewee
from glQiwiApi.qiwi.exceptions import QiwiAPIError
from glQiwiApi.qiwi.clients.p2p import types as qiwi_types

import gls
import pilgram
import response_system as rs
from response_system import Response
import settings
import template
from .. import images
from ..methods import BILL_STATUSES
from ..models import Bill, Order, Client, Employee, Subscription
from apps.coupons.models import Coupon


async def get_for_self_button_handler(_, user: aiogram.types.User):
    """ Открывает заказ, который после будет обработан оператором """
    return await get_for_self(user)


async def get_as_gift_button_handler(_, user: aiogram.types.User):
    """
    Отправляет сообщение со сгенерированной подарочной картой.
    Для этого генерируется купон со скидкой 100% на выбранную
    подписку.
    Купон при покупке зарегистрирует пользователя как реферала,
    также не позволит передарить подписку.
    """
    return await get_as_gift(user)


# ВСПОМОГАТЕЛЬНОЕ ---------------------------------------------------

BILL_GET_ERROR = (
    'Ошибка получения счёта, пожалуйста, '
    'обратитесь в поддержку'
)


async def _order_wrapper(function, user: aiogram.types.User) -> list[Response]:
    """ Производит предварительные действия перед обработкой
        получения заказа """

    # Получение счёта из базы и соответствующего ему счёта qiwi
    try:
        bill = Bill.get_by_id(user.id)
    except peewee.DoesNotExist:
        return rs.feedback(BILL_GET_ERROR)

    try:
        qiwi_bill = await gls.qiwi.get_bill_by_id(bill.qiwi_id)
    except QiwiAPIError:
        return rs.feedback(BILL_GET_ERROR)

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
        return rs.delete(bill.message_id, feedback=status_message)

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


@_order_handler
async def get_for_self(client: Client, bill: Bill, qiwi_bill: qiwi_types.Bill) -> list[Response]:
    """ Часть логики, относящаяся к покупке подписки для себя """

    order = Order(
        client=client,
        subscription=bill.subscription_id,
        coupon=bill.coupon_id,
        paid_amount=qiwi_bill.amount.value,
        open_at=rs.global_time.get()
    )
    order.save()

    subscription = bill.subscription
    return (
        rs.message(
            template.render(subscription.order_template, {
                'subscription': subscription,
                'order': order
            }),
            # Важная часть, т.к. в сообщении со счётом находится кнопка "Для себя"
            delete_original=True,
        ) +
        rs.notify(
            template.render('apps/order_processing/templates/op-message-order-new.xml', {
                'order': order
            }),
            Employee.get_to_notify_on_purchase(),
            bot=gls.operator_bot
        )
    )


@_order_handler
async def get_as_gift(client: Client, bill: Bill, _: qiwi_types.Bill) -> list[Response]:
    """ Часть логики, относящаяся к покупке подписки в подарок """

    subscription: Subscription = bill.subscription
    gift_coupon = Coupon.from_type(
        subscription.gift_coupon_type_id,
        sets_referral=client.chat_id,
        now=rs.global_time.get()
    )

    gift_card_image = pilgram.PilImageInputFile(
        images.render_gift_card_image(f't.me/botpiska_bot?start={gift_coupon.code}'),
        filename='GIFT.png'
    )

    bill.delete_instance()
    return rs.message(
        template.render('apps/botpiska/templates/message-gift.xml', {
            'gift-card-image': gift_card_image,
            'subscription': subscription,
            'coupon': gift_coupon
        }),
        delete_original=True
    )


__all__ = (
    'get_for_self_button_handler',
    'get_as_gift_button_handler'
)
