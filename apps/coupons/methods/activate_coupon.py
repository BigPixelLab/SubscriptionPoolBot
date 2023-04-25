import aiogram.types
from aiogram.fsm.storage.base import StorageKey

import gls
import response_system as rs
import template
from apps.botpiska import methods as botpiska_methods
from apps.botpiska.models import Bill
from apps.coupons import methods as coupons_methods
from response_system import Response


async def activate_coupon(code: str, user: aiogram.types.User, silent: bool = False) -> list[Response]:
    """ Активирует купон и при необходимости выводит сообщение со счётом """

    bot = aiogram.Bot.get_current()

    # Получение купона
    result, coupon = await coupons_methods.get_coupon(code, user.id)

    # Обрабатываем случаи, когда купон недействителен
    if result.is_error and result.error in COUPON_EXCEPTIONS:
        message = COUPON_EXCEPTIONS[result.error].format(coupon=coupon.code)
        return rs.message(message)

    if result.is_error:
        return rs.no_response()

    # Если действителен - записываем в userdata
    key = StorageKey(bot.id, user.id, user.id)
    await gls.storage.update_data(bot, key, {
        'coupon': coupon.code
    })

    # Если купон действителен всего для одной подписки - отправляем счёт на эту подписку
    if subscription := coupon.get_sub_single():
        return await botpiska_methods.send_bill(user, subscription)

    # Если есть не просроченный счёт - заново его генерируем
    elif last_bill := Bill.get_legit_by_id(user.id):
        return await botpiska_methods.send_bill(user, last_bill.subscription)

    if silent:
        return rs.no_response()

    return rs.message(
        template.render('apps/coupons/templates/message-coupon-success.xml', {})
    )


COUPON_EXCEPTIONS = {
    'PROHIBITED': (
        'Использующийся купон "{coupon.code}", вероятно, создан '
        'вами и предназначается для других пользователей'
    ),
    'EXPIRED': (
        'Срок действия использующегося купона "{coupon.code}" иссяк '
        '{coupon.expires_after:%d.%m}'
    ),
    'EXCEEDED_USAGE': (
        'Превышено число использований купона "{coupon.code}" '
        '({coupon.max_usages} использований)'
    ),
    'WRONG_SUBSCRIPTION': (
        'Использующийся купон "{coupon.code}" не распространяется '
        'на данную подписку'
    ),
    'ALREADY_USED': (
        'Вы уже использовали купон "{coupon.code}" при покупке ранее'
    )
}

__all__ = ('activate_coupon',)
