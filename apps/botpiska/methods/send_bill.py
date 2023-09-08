""" ... """
from __future__ import annotations

import aiogram

import gls
import pilgram
import response_system as rs
import response_system_extensions as rse
import settings
from apps.botpiska import images
from apps.botpiska import methods as botpiska_methods
from apps.botpiska.methods.create_qiwi_bill import create_qiwi_bill
from apps.botpiska.models import Subscription, Bill, Client
from apps.coupons import methods as coupons_methods
from response_system import Response


async def send_bill(
        user: aiogram.types.User,
        subscription: Subscription
) -> Response:
    """
    Генерирует и отправляет сообщение со счётом указанному пользователю.

    :param user: Пользователь, которому будет отправлен счёт (для
        пользователя будет удалён ранее сгенерированный счёт).
    :param subscription: Подписка, которую покупает пользователь.
        Используется для определения суммы выставляемого счёта
    :return: Последовательность Response-объектов, отправляющих счёт
        или предупреждения
    """

    client, _ = Client.get_or_register(user.id)

    # Выводим соглашение, если оно ещё не было выведено для пользователя
    if not client.terms_message_id:
        async def set_client_terms_message_id(message: aiogram.types.Message):
            await gls.bot.pin_chat_message(message.chat.id, message.message_id, disable_notification=True)
            client.terms_message_id = message.message_id
            client.save()

        rs.respond(rse.tmpl_send(
            'apps/botpiska/templates/message-terms.xml', {},
            on_success=lambda x: set_client_terms_message_id(x[0]),
            priority=1
        ))

    # Разбираемся с ранее выставленными счетами
    rs.respond(await botpiska_methods.delete_bill(user))

    coupon = None

    try:
        # Получаем активированный купон (сразу с CouponType)
        coupon = await coupons_methods.get_suggested_coupon(user.id, subscription.id)

    except coupons_methods.CouponNotFound:
        pass

    except coupons_methods.CouponProhibited as error:
        rs.respond(rs.feedback(
            f'Использующийся купон "{error.coupon.code}", вероятно, создан '
            'вами и предназначается для других пользователей, счёт '
            'выставлен без его учёта'
        ))

    except coupons_methods.CouponExpired as error:
        rs.respond(rs.feedback(
            f'Срок действия использующегося купона "{error.coupon.code}" иссяк '
            f'{error.coupon.created_at + error.coupon.type.lifespan:%d.%m}, счёт выставлен без его учёта'
        ))

    except coupons_methods.CouponExceededUsage as error:
        rs.respond(rs.feedback(
            f'Превышено число использований купона "{error.coupon.code}" '
            f'({error.coupon.max_usages} использований), счёт выставлен '
            'без его учёта'
        ))

    except coupons_methods.CouponWrongSubscription as error:
        rs.respond(rs.feedback(
            f'Использующийся купон "{error.coupon.code}" не распространяется '
            'на данную подписку, счёт выставлен без его учёта'
        ))

    except coupons_methods.CouponAlreadyUsed as error:
        rs.respond(rs.feedback(
            f'Вы уже использовали купон "{error.coupon.code}" при покупке ранее'
        ))

    # Генерируем новый счёт
    bill_items, total = botpiska_methods.generate_bill_content(subscription, coupon)
    expires_after = rs.global_time.get() + settings.BILL_TIMEOUT

    qiwi_bill = await create_qiwi_bill(gls.qiwi, f'{total:.2f}', expires_after)

    async def register_bill(messages: list[aiogram.types.Message]):
        """ Регистрирует счёт в базе """
        Bill.insert(
            client=client,
            subscription=subscription,
            coupon=coupon,
            qiwi_id=qiwi_bill.id,
            message_id=messages[0].message_id,
            expires_at=expires_after
        ).execute()

    # noinspection PyTypeChecker
    bill_image = pilgram.PilImageInputFile(
        images.render_bill_image(bill_items, total, rs.global_time.get()),
        filename='BILL.png'
    )

    is_gifts_allowed = coupon is None or coupon.type.allows_gifts

    return (
        rse.tmpl_send('apps/botpiska/templates/message-bill.xml', {
            'bill-image': bill_image,
            'subscription': subscription,
            'bill': qiwi_bill,
            'is_gifts_allowed': is_gifts_allowed
        }, on_success=register_bill)
    )

__all__ = ('send_bill',)
