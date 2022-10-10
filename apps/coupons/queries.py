from utils import database


def is_promo_used_by_customer(code: str, customer: int) -> bool:
    return database.single_value(
        """
            -- If there is at least one order from customer with given coupon, coupon considered as used
            select count(*) > 0 from "Order" O
            where
                O.coupon = %(coupon_code)s and
                O.customer_id = %(customer_id)s
        """,
        f'Getting information about whether the coupon "{code}" was used by the user {customer}',
        coupon_code=code,
        customer_id=customer
    )
