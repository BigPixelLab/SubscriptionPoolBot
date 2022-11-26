from __future__ import annotations

import datetime
import random
import string
import typing

import settings
from utils import database


class Coupon(typing.NamedTuple):
    id: int
    """ Coupon ID """
    code: str
    """ Six character unique code, containing only upper letters, digits and '-' """
    discount: int
    """ Discount in percents """
    subscription: int | None = None
    """ If set, coupon can be activated only for given subscription """
    referer: int | None = None
    """ User who generated coupon. Usually coupons are not allowed to be used by ones who generated them """

    is_expired: bool = False
    """ Is coupon expired. Usually set automatically then used by more than specified in max_usages """
    expire_after: datetime.datetime | None = None
    """ If set, after this date coupon is going to be set as expired """
    max_usages: int | None = None
    """ How many people can use this coupon"""
    is_one_time: bool = False
    """ If true, coupon will be deleted after first usage """

    @classmethod
    def _update_expired(cls):
        database.execute(
            """
                update "Coupon" as C set
                    is_expired = (
                        -- Expire because of time (if set)
                        expire_after is not null and
                        %(now)s > expire_after or
                    
                        -- Expire because exceeded max number of usages (if set)
                        max_usages is not null and (
                            -- Count of usages
                            select count(*) from "Order"
                            where coupon = C.code
                        ) + (
                            -- Count of reservations
                            select count(*) from "User"
                            where reserved_coupon = C.code and
                                %(now)s <= last_bill_expire_after
                        ) >= max_usages
                    )
                where true
            """,
            now=datetime.datetime.now()
        )

    @classmethod
    def get(cls, code: str) -> Coupon | None:
        cls._update_expired()
        return database.single(
            Coupon,
            """ select * from "Coupon" where code = %(code)s """,
            f'Getting coupon with code "{code}"',
            code=code
        )

    @classmethod
    def get_not_expired(cls, code: str, user_id: int) -> Coupon | None:
        now = datetime.datetime.now()
        database.execute(
            """
                -- All of this "insert" stuff is to be sure that user is in the table
                insert into "User" (
                    user_id,
                    last_interaction,
                    reserved_coupon,
                    last_bill_expire_after
                ) values (
                    %(user_id)s,
                    %(now)s,
                    (  -- Get unexpired coupon, null will be returned if not found
                        select code from "Coupon" C
                        where C.code = %(code)s and not (
                            -- All that expiration stuff
                        
                            -- Expire because of time (if set)
                            expire_after is not null and
                            %(now)s > expire_after or
                            
                            -- Expire because exceeded max number of usages (if set)
                            max_usages is not null and (
                                -- Count of usages
                                select count(*) from "Order"
                                where coupon = C.code
                            ) + (
                                -- Count of reservations
                                select count(*) from "User" U
                                where
                                    U.reserved_coupon = C.code and
                                    %(now)s <= U.last_bill_expire_after and
                                    U.user_id != %(user_id)s
                            ) >= max_usages
                        )
                    ),
                    %(expire_after)s
                )
                on conflict (user_id) do update set
                    last_interaction = excluded.last_interaction,
                    reserved_coupon = excluded.reserved_coupon,
                    last_bill_expire_after = excluded.last_bill_expire_after
            """,
            f'Getting unexpired coupon "{code}"',
            expire_after=now + datetime.timedelta(seconds=settings.BILL_TIMEOUT_SEC),
            now=now,
            user_id=user_id,
            code=code
        )

        return database.single(
            Coupon,
            """
                select * from "Coupon"
                where code = %(code)s
            """,
            code=code
        )

    @classmethod
    def free_reservation(cls, user_id: int):
        database.execute(
            """
                insert into "User" (
                    user_id,
                    last_interaction,
                    reserved_coupon,
                    last_bill_expire_after
                ) values (
                    %(user_id)s,
                    %(last_inter)s,
                    null,
                    null
                )
                on conflict (user_id) do update set
                    last_interaction = excluded.last_interaction,
                    reserved_coupon = excluded.reserved_coupon,
                    last_bill_expire_after = excluded.last_bill_expire_after
            """,
            f'Freeing reservation for user {user_id}',
            last_inter=datetime.datetime.now(),
            user_id=user_id
        )

    @classmethod
    def is_used_by(cls, code: str, user_id: int):
        return database.single_value(
            """
                -- If there is at least one order from customer with given coupon, coupon considered as used
                select count(*) > 0 from "Order" O
                where
                    O.coupon = %(code)s and
                    O.customer_id = %(user_id)s
            """,
            f'Getting information about whether the coupon "{code}" was used by the user {user_id}',
            code=code,
            user_id=user_id
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
