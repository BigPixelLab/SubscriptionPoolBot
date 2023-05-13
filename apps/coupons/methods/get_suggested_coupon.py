from __future__ import annotations

import userdata
from apps.coupons.methods import CouponWrongSubscription, CouponError, CouponNotFound, get_coupon
from apps.coupons.models import Coupon


async def get_suggested_coupon(
        user_id: int,
        subscription_id: str = None
) -> Coupon | None:
    """ Получает активированный купон из базы """

    suggested_coupon, = await userdata.get_data(user_id, ['coupon'])

    # Пользователь не активировал купон
    if not suggested_coupon:
        return None

    # Получаем купон из базы и заодно проверяем его валидность
    try:
        return await get_coupon(suggested_coupon, user_id, subscription_id)

    except CouponWrongSubscription:
        raise

    except (CouponError, CouponNotFound):
        # Нет смысла держать активированным невалидный купон
        await userdata.set_data(user_id, coupon=None)
        raise


__all__ = ('get_suggested_coupon',)
