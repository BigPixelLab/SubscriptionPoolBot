""" ... """
from __future__ import annotations

import peewee

import response_system as rs
from apps.coupons.models import Coupon
from apps.coupons.models_shared import CouponType
from result import *


async def get_coupon(
        code: str,
        user_id: int = None,
        subscription_id: str = None
) -> tuple[Result[None, str], Coupon | None]:
    """
        Получает купон из базы

        Возможные ошибки:
          - NOT_FOUND - Предложенный купон не найден
          - PROHIBITED - Запрещён для активации данным пользователем
          - EXPIRED - Иссяк срок действия купона
          - EXCEEDED_USAGE - Превышено общее число использований купона
          - WRONG_SUBSCRIPTION - Купон не предназначен для данной подписки
          - ALREADY_USED - Купон уже был использован данным пользователем
    """
    try:
        coupon: Coupon = Coupon.select_by_id(code).join(CouponType).get()
    except peewee.DoesNotExist:
        return Error('NOT_FOUND'), None

    if user_id and coupon.sets_referral_id == user_id:
        return Error('PROHIBITED'), coupon

    if coupon.expires_after and rs.global_time.get() > coupon.expires_after:
        return Error('EXPIRED'), coupon

    if coupon.max_usages and coupon.get_total_uses() >= coupon.max_usages:
        return Error('EXCEEDED_USAGE'), coupon

    if subscription_id and not coupon.is_allowed_for_subscription(subscription_id):
        return Error('WRONG_SUBSCRIPTION'), coupon

    if coupon.is_already_used_by(user_id):
        return Error('ALREADY_USED'), coupon

    return Ok(), coupon


__all__ = ('get_coupon',)
