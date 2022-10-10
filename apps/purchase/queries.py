from __future__ import annotations

import datetime

from utils import database
from ..coupons import models as coupon_models


def is_user_have_reserved_ac(user_id: int, sub_id: int) -> bool:
    return database.single_value(
        """
            select count(*) > 0 from "ActivationCodes" AC
            where
                AC.subscription = %(subscription)s and
                AC.reserved_by = %(user)s
        """,
        f'Checking is user {user_id} have reserved activation code for subscription {sub_id}',
        subscription=sub_id,
        user=user_id
    )


def reserve_ac(user_id: int, sub_id: int) -> bool:
    """Returns True on success"""
    return database.single_value(
        """
            update "ActivationCodes" set
                reserved_at = %(reserved_at)s,
                reserved_by = %(reserved_by)s
            where id = (
                select AC.id from "ActivationCodes" AC
                where
                    AC.subscription = %(subscription)s and 
                    AC.reserved_at is null
                limit 1
            )
            returning id
        """,
        f'Reserving activation code on subscription {sub_id} for user {user_id}',
        reserved_at=datetime.datetime.now(),
        reserved_by=user_id,
        subscription=sub_id
    ) is not None


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
