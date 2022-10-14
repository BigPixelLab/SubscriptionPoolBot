from __future__ import annotations

import datetime

from utils import database
from ..coupons import models as coupon_models


def get_valid_coupon(coupon_code: str) -> coupon_models.Coupon | None:
    return database.single(
        coupon_models.Coupon,
        """
            select * from "Coupon" C
            where C.code = %(coupon_code)s and C.is_expired = false
        """,
        f'Getting coupon "{coupon_code}"',
        coupon_code=coupon_code
    )
