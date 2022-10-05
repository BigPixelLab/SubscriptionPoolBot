from utils import database
from . import models


def get_coupon_by_code(code: str) -> models.Coupon:
    return database.single(
        models.Coupon,
        """
            select * from "Coupon"
            where
                code = %(coupon_code)s
                -- no is_expired check cause we just need coupon, expired or not
            limit 1
        """,
        coupon_code=code
    )


def is_promo_used_by_customer(code: str, customer: int) -> bool:
    return database.single_value(
        """
            -- If there is at least one order from customer with given coupon, coupon considered as used
            select count(*) > 0 from "Order" O
            where
                O.coupon = %(coupon_code)s and
                O.customer_id = %(customer_id)s
        """,
        coupon_code=code,
        customer_id=customer
    )
