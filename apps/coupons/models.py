import datetime
import random
import string
import typing

from utils import database


class Coupon(typing.NamedTuple):
    id: int
    """ Coupon ID """
    code: str
    """ Six character unique code, containing only upper letters, digits and '-' """
    discount: int
    """ Discount in percents """
    is_expired: bool
    """ Is coupon expired. Usually set automatically then used by more than specified in max_usages """
    expire_after: datetime.datetime
    """ If set, after this date coupon is going to be set as expired """
    max_usages: int
    """ How many people can use this coupon"""
    is_one_time: bool
    """ If true, coupon will be deleted after first usage """
    subscription: int
    """ If set, coupon can be activated only for given subscription """
    referer: int
    """ User who generated coupon. Usually coupons are not allowed to be used by ones who generated them """

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
                    -- Expire because of time (if set)
                    expire_after is not null and
                    %(now)s > expire_after or
                    
                    -- Expire because exceeded max number of usages (if set)
                    max_usages is not null and (
                        -- Count of usages
                        select count(*) from "Order" where coupon = %(code)s
                    ) >= max_usages
            """,
            now=datetime.datetime.now(),
            code=code
        )

    @classmethod
    def is_used(cls, code: str, user: int):
        return database.single_value(
            """
                -- If there is at least one order from customer with given coupon, coupon considered as used
                select count(*) > 0 from "Order" O
                where
                    O.coupon = %(code)s and
                    O.customer_id = %(user)s
            """,
            f'Getting information about whether the coupon "{code}" was used by the user {user}',
            code=code,
            user=user
        )

    @classmethod
    def add(cls, code: str, discount: int, subscription: int = None, max_usages: int = 1, referer: int = None,
            is_one_time: bool = False):
        result = database.single_value(
            """
                insert into "Coupon" (code, discount, max_usages, subscription, referer, is_one_time)
                values (%(code)s, %(discount)s, %(max_usages)s, %(subscription)s, %(referer)s, %(is_one_time)s)
                on conflict (code) do nothing returning code
            """,
            f'Adding new coupon {code}',
            code=code,
            discount=discount,
            max_usages=max_usages,
            subscription=subscription,
            referer=referer,
            is_one_time=is_one_time
        )
        return result is not None

    @classmethod
    def _generate(cls):
        return ''.join(
            random.choice(string.digits + string.ascii_uppercase + '-')
            for _ in range(6)
        )

    @classmethod
    def generate(cls, discount: int, subscription: int = None, max_usages: int = 1, referer: int = None,
                 is_one_time: bool = True):
        code = cls._generate()
        while not cls.add(code, discount, subscription, max_usages, referer, is_one_time):
            code = cls._generate()
        return code

    @classmethod
    def delete(cls, code: str):
        database.execute(
            """ delete from "Coupon" where code = %(code)s """,
            f'Deleting coupon {code}',
            code=code
        )
