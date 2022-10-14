from __future__ import annotations

import datetime
import typing

import settings
from utils import database


class ActivationCode(typing.NamedTuple):
    id: int
    """ Activation Code ID """
    code: str
    """ Licence key """
    subscription: int
    """ Subscription ID, for which code is intended """
    linked_order: int | None
    """ Order ID, for which code is reserved """
    reserved_at: datetime.datetime | None
    """ Date and time when code was reserved (not linked) """
    reserved_by: int | None
    """ Telegram ID of user who reserved the code """

    @classmethod
    def is_reserved(cls, user: int, sub_id: int) -> bool:
        return database.single_value(
            """
                select count(*) > 0 from "ActivationCode" AC
                where
                    AC.subscription = %(subscription)s and
                    AC.reserved_by = %(user)s
            """,
            f'Checking is user {user} have reserved activation code for subscription {sub_id}',
            subscription=sub_id,
            user=user
        )

    @classmethod
    def reserve(cls, user: int, sub_id: int) -> bool:
        return database.single_value(
            """
                update "ActivationCode" set
                    reserved_at = %(reserved_at)s,
                    reserved_by = %(reserved_by)s
                where id = (
                    select AC.id from "ActivationCode" AC
                    where
                        AC.subscription = %(subscription)s and 
                        AC.reserved_at is null
                    limit 1
                )
                returning id
            """,
            f'Reserving activation code on subscription {sub_id} for user {user}',
            reserved_at=datetime.datetime.now(),
            reserved_by=user,
            subscription=sub_id
        ) is not None

    @classmethod
    def update_reserved(cls):
        # Time when AC should've been reserved to expire now. Adding minute for extra safety
        time = datetime.datetime.now() - datetime.timedelta(seconds=settings.BILL_TIMEOUT_SEC + 60)
        database.execute(
            """
                update "ActivationCode" AC set
                    reserved_at = null,
                    reserved_by = null
                where AC.reserved_at <= %(expired_time)s
            """,
            'Updating reserved activation codes',
            expired_time=time
        )

    @classmethod
    def get_linked(cls, order_id: int) -> str:
        return database.single_value(
            """
                select code from "ActivationCode"
                where linked_order = %(order_id)s
            """,
            f'Getting activation code for order #{order_id}',
            order_id=order_id
        )

    @classmethod
    def link_order(cls, order_id: int):
        database.execute(
            """
                update "ActivationCode" set
                    linked_order = %(linked_order)s
                where id = (
                    -- First unclaimed activation code for given subscription
                    select AC.id from "ActivationCode" as AC
                    where
                        AC.linked_order is null and
                        AC.reserved_at is null and
                        AC.subscription = (
                            -- Getting ordered subscription
                            select O.subscription from "Order" O
                            where id = %(linked_order)s
                        )
                    order by AC.id limit 1
                )
            """,
            f'Linking activation code with order #{order_id}',
            linked_order=order_id
        )
