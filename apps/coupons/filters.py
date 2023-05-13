from __future__ import annotations

import aiogram

from apps.coupons import methods as coupons_methods


async def coupon_filter(message: aiogram.types.Message) -> dict | bool:
    """ ... """
    code = message.text

    if code and coupons_methods.is_coupon_like(code):
        return {'code': code}

    return False
