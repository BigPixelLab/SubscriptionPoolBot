import aiogram.types
from aiogram.fsm.storage.base import StorageKey

import gls
import response_system as rs
import response_system_extensions as rse
from apps.botpiska import methods as botpiska_methods
from apps.botpiska.models import Bill, Subscription
from apps.coupons import methods as coupons_methods
from apps.statistics.models import Statistics
from response_system import Response


async def activate_coupon(code: str, user: aiogram.types.User, silent: bool = False) -> Response:
    """ Активирует купон и при необходимости выводит сообщение со счётом """
    bot = aiogram.Bot.get_current()

    # Получение купона
    coupon = await coupons_methods.get_coupon(code, user.id)

    # ...
    Statistics.record('activated_coupon', user.id, coupon=coupon.code)

    # Если действителен - записываем в userdata
    key = StorageKey(bot.id, user.id, user.id)
    await gls.storage.update_data(bot, key, {
        'coupon': coupon.code
    })
    # Если купон действителен всего для одной подписки - отправляем счёт на эту подписку
    if subscription := coupon.get_sub_single():
        return await botpiska_methods.send_bill(user, Subscription.get_by_id(subscription))

    # Если есть не просроченный счёт - заново его генерируем
    elif last_bill := Bill.get_legit_by_id(user.id):
        return await botpiska_methods.send_bill(user, last_bill.subscription)

    if silent:
        return rs.no_response()

    return rse.tmpl_send('apps/coupons/templates/message-coupon-success.xml', {})


__all__ = ('activate_coupon',)
