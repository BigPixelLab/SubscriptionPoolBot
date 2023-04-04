from __future__ import annotations

import userdata
from apps.coupons import methods as coupons_methods
from apps.coupons.models import Coupon
from result import *


async def get_suggested_coupon(
        user_id: int,
        subscription_id: str = None
) -> tuple[Result[None, str], Coupon | None]:
    """
        Получает активированный купон из базы

        Возможные ошибки:
          - NOT_FOUND - Предложенный купон не найден
          - PROHIBITED - Запрещён для активации данным пользователем
          - EXPIRED - Иссяк срок действия купона
          - EXCEEDED_USAGE - Превышено общее число использований купона
          - WRONG_SUBSCRIPTION - Купон не предназначен для данной подписки
          - ALREADY_USED - Купон уже был использован данным пользователем
    """

    suggested_coupon, = await userdata.get_data(user_id, ['coupon'])

    # Пользователь не активировал купон
    if not suggested_coupon:
        return Ok(), None

    # Получаем купон из базы и заодно проверяем его валидность
    result, coupon = await coupons_methods.get_coupon(suggested_coupon, user_id, subscription_id)

    # Нет смысла держать активированным невалидный купон
    if result.error != 'WRONG_SUBSCRIPTION':
        await userdata.set_data(user_id, coupon=None)

    return result, coupon


__all__ = ('get_suggested_coupon',)
