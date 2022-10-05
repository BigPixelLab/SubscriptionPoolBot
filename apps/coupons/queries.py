from utils import database
from . import models


def get_coupon_by_code(code: str) -> models.Coupon:
    return database.single(models.Coupon, """
        select * from "Coupon"
        where
            code = %(code)s
            -- no is_expired check cause we just need coupon, expired or not
        limit 1
    """, code=code)


def is_promo_used_by_customer(code: str, customer: int):
    return database.single_value("""
        -- If there is at least one order from customer with given coupon, coupon considered as used
        select count(*) from "Order" O
        where
            O.coupon = %s and
            O.customer_id = %s
    """, code, customer) > 0
