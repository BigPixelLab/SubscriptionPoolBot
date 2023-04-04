""" ... """
from __future__ import annotations

import aiogram

import gls
import pilgram
import response_system as rs
import settings
import template
from apps.botpiska import images
from apps.botpiska import methods as botpiska_methods
from apps.botpiska.methods.create_qiwi_bill import create_qiwi_bill
from apps.botpiska.models import Subscription, Bill, Client
from apps.coupons import methods as coupons_methods
from response_system import Response


async def send_bill(
        user: aiogram.types.User,
        subscription: Subscription
) -> list[Response]:
    """
    Генерирует и отправляет сообщение со счётом указанному пользователю.

    :param user: Пользователь, которому будет отправлен счёт (для
        пользователя будет удалён ранее сгенерированный счёт).
    :param subscription: Подписка, которую покупает пользователь.
        Используется для определения суммы выставляемого счёта
    :return: Последовательность Response-объектов, отправляющих счёт
        или предупреждения
    """

    client = Client.get_or_register(user.id)

    # Выводим соглашение, если оно ещё не было выведено для пользователя
    if not client.terms_message_id:
        async def set_client_terms_message_id(messages: list[aiogram.types.Message]):
            message, = messages
            client.terms_message_id = message.message_id
            client.save()

        await rs.respond(rs.message(
            template.render('apps/botpiska/templates/message-terms.xml', {}).extract(),
            on_success=set_client_terms_message_id,
            pin=True
        ))

    # Разбираемся с ранее выставленными счетами
    result = await botpiska_methods.delete_previous_bill(user)

    if result.error == 'BILL_IS_PAID':
        return rs.feedback(
            'У вас имеется не закрытый оплаченный счёт. '
            'Чтобы сгенерировать новый, сначала завершите '
            'предыдущий заказ'
        )

    # Если подписка, которую пытаются купить уже недоступна
    if not subscription.display:
        return rs.feedback('Эта подписка в данный момент недоступна')

    # Получаем активированный купон
    result, coupon = await coupons_methods.get_suggested_coupon(user.id, subscription.id)
    coupon_feedback = None

    if result.error in COUPON_EXCEPTIONS:
        coupon_feedback = COUPON_EXCEPTIONS[result.error].format(coupon=coupon)

    # Генерируем новый счёт
    bill_items, total = botpiska_methods.generate_bill_content(subscription, coupon)
    expires_after = rs.global_time.get() + settings.BILL_TIMEOUT

    result = await create_qiwi_bill(gls.qiwi, f'{total:.2f}', expires_after)
    if result.is_error:
        return rs.feedback(
            'Ошибка создания счёта, пожалуйста, '
            'обратитесь в поддержку'
        )

    qiwi_bill = result.unpack()

    def register_bill(messages: list[aiogram.types.Message]):
        """ Регистрирует счёт в базе """
        message, = messages  # гарантированно одно сообщение в списке
        Bill.insert(
            client=client,
            subscription=subscription,
            coupon=coupon,
            qiwi_id=qiwi_bill.id,
            message_id=message.message_id,
            expires_after=expires_after
        ).execute()

    # noinspection PyTypeChecker
    bill_image = pilgram.PilImageInputFile(
        images.render_bill_image(bill_items, total, rs.global_time.get()),
        filename='BILL.png'
    )

    is_gifts_allowed = coupon is None or coupon.is_gifts_allowed

    return rs.message(
        template.render('apps/botpiska/templates/message-bill.xml', {
            'bill-image': bill_image,
            'subscription': subscription,
            'bill': qiwi_bill,
            'is_gifts_allowed': is_gifts_allowed
        }).extract(),  # extract, чтобы удостоверится, что в списке всего одно сообщение
        feedback=coupon_feedback,
        on_success=register_bill
    )


COUPON_EXCEPTIONS = {
    'PROHIBITED': (
        'Использующийся купон "{coupon.code}", вероятно, создан '
        'вами и предназначается для других пользователей, счёт '
        'выставлен без его учёта'
    ),
    'EXPIRED': (
        'Срок действия использующегося купона "{coupon.code}" иссяк '
        '{coupon.expires_after:%d.%m}, счёт выставлен без его учёта'
    ),
    'EXCEEDED_USAGE': (
        'Превышено число использований купона "{coupon.code}" '
        '({coupon.max_usages} использований), счёт выставлен '
        'без его учёта'
    ),
    'WRONG_SUBSCRIPTION': (
        'Использующийся купон "{coupon.code}" не распространяется '
        'на данную подписку, счёт выставлен без его учёта'
    ),
    'ALREADY_USED': (
        'Вы уже использовали купон "{coupon.code}" при покупке ранее'
    )
}

__all__ = ('send_bill',)
