""" ... """
from __future__ import annotations

import datetime

import peewee

import response_system as rs
from apps.coupons.models import Coupon, CouponType
from response_system import UserFriendlyException


class CouponNotFound(UserFriendlyException):
    """ Купон не найден """


class CouponError(UserFriendlyException):
    """ Базовый класс для ошибок связанных с получением купона """

    def __init__(self, coupon: Coupon, description: str):
        super().__init__(description)
        self._coupon = coupon

    @property
    def coupon(self):
        return self._coupon


class CouponProhibited(CouponError):
    """ Купон не найден """


class CouponExpired(CouponError):
    """ Срок действия купона истёк """


class CouponExceededUsage(CouponError):
    """ Превышено разрешённое количество использований купона """


class CouponWrongSubscription(CouponError):
    """ Купон не предназначен для данной подписки """


class CouponAlreadyUsed(CouponError):
    """ Купон уже был использован данным пользователем """


async def get_coupon(
        code: str,
        user_id: int = None,
        subscription_id: str = None
) -> Coupon:
    """ Получает купон из базы """

    try:
        coupon: Coupon = Coupon.select_by_id(code).join(CouponType).get()
    except peewee.DoesNotExist:
        raise CouponNotFound(f'Купон "{code}" не найден')

    if user_id and coupon.sets_referral_id == user_id:
        raise CouponProhibited(coupon, 'Купон запрещён для активации данным пользователем')

    if coupon.type.lifespan and rs.global_time.get() + coupon.type.lifespan > datetime.datetime.now():
        raise CouponExpired(coupon, 'Истёк срок действия купона')

    if coupon.type.max_usages and coupon.get_total_uses() >= coupon.type.max_usages:
        raise CouponExceededUsage(coupon, 'Превышено разрешённое количество использований купона')

    if subscription_id and not coupon.is_allowed_for_subscription(subscription_id):
        raise CouponWrongSubscription(coupon, 'Купон не предназначен для данной подписки')

    if coupon.is_already_used_by(user_id):
        raise CouponAlreadyUsed(coupon, 'Купон уже был использован данным пользователем')

    return coupon


__all__ = (
    'get_coupon',
    'CouponNotFound',
    'CouponError',
    'CouponProhibited',
    'CouponExpired',
    'CouponExceededUsage',
    'CouponWrongSubscription',
    'CouponAlreadyUsed'
)
