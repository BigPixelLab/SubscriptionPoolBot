import typing

from utils import database


class Coupon(typing.NamedTuple):
    id: int
    """Coupon ID"""
    code: str
    """Six character unique code, containing only upper letters, digits and '-'"""
    discount: int
    """Discount in percents"""
    is_expired: bool
    """Is coupon expired. Usually set automatically then used by more than specified in max_usages"""
    max_usages: int
    """How many people can use this coupon"""

    @classmethod
    def get(cls, code: str) -> 'Coupon':
        return database.single(
            Coupon,
            """ select * from "Coupon" where code = %(coupon_code)s """,
            f'Getting coupon with code "{code}"',
            coupon_code=code
        )

    @classmethod
    def get_free(cls, code: str):
        return database.single(
            Coupon,
            """
                select * from "Coupon" C
                where C.code = %(code)s and C.is_expired = false
            """,
            f'Getting unexpired coupon "{code}"',
            code=code
        )

    @classmethod
    def update_expired(cls, code: str):
        database.execute(
            """
                update "Coupon" set
                    is_expired = true
                where
                    max_usages is not null and (
                        select count(*) from "Order" where coupon = %(code)s
                    ) >= max_usages
            """,
            code=code
        )
