import datetime
import decimal
import typing
from dataclasses import dataclass

from aiogram.filters import Command

from apps.operator.models import Employee
from apps.search.models import Subscription
from utils import database


@dataclass
class Order:
    id: int
    """ Order ID """
    subscription: int
    """ Subscription ID """
    coupon: typing.Optional[str]
    """ Coupon code, that been activated then order been placed """
    total: float
    """ Final payment amount """
 
    customer_id: int
    """ Telegram ID of the user who placed the order """

    processed_by: typing.Optional[int]
    """ Telegram ID of the user who processing order """
    created_at: datetime.datetime
    """ Date and time of the moment then order been placed """
    closed_at: typing.Optional[datetime.datetime]
    """ Dane and time of the moment then order been closed """

    is_cont_notified: bool
    """ Is customer who placed the order already notified about continuation """

    def get_subscription(self):
        return database.single(
            Subscription,
            """ select * from "Subscription" where id = %(id)s """,
            f'Getting subscription of order #{self.id}',
            id=self.subscription
        )

    def get_processed_by(self):
        if self.processed_by is None:
            return None
        return database.single(
            Employee,
            """ select * from "Employee" where id = %(id)s """,
            f'Getting operator of order #{self.id}',
            id=self.processed_by
        )

    @classmethod
    def get(cls, _id: int) -> 'Order':
        return database.single(
            Order,
            """ select * from "Order" where id = %(id)s """,
            f'Getting order with id {_id}',
            id=_id
        )

    @classmethod
    def get_top(cls) -> 'Order':
        return database.single(
            Order,
            """
                select * from "Order"
                where
                    processed_by is null and
                    closed_at is null
                order by created_at limit 1
            """,
            'Getting top order from queue'
        )

    @classmethod
    def mark_as_taken(cls, _id: int, operator_id: int):
        database.execute(
            """
                update "Order" set
                    processed_by = %(operator_id)s
                where id = %(order_id)s
            """,
            f'Marking order #{_id} as taken',
            operator_id=operator_id,
            order_id=_id
        )

    @classmethod
    def is_taken_by(cls, _id: int, operator_id: int):
        return bool(database.single_value(
            """
                select count(*) from "Order"
                where
                    id = %(id)s and
                    processed_by = %(processed_by)s
            """,
            f'Checking if order #{_id} is taken by {operator_id}',
            processed_by=operator_id,
            id=_id
        ))

    @classmethod
    def return_to_queue(cls, _id: int):
        database.execute(
            """
                update "Order" set
                    processed_by = null
                where id = %(id)s
            """,
            f'Returning order #{_id} back to the queue',
            id=_id
        )

    @classmethod
    def get_position_in_queue(cls, _id: int):
        return database.single_value(
            """
                select count(*) from "Order"
                where
                    processed_by is null and
                    closed_at is null and
                    created_at < (
                        select created_at from "Order"
                        where id = %(id)s
                    )
            """,
            f'Getting position in queue for order #{_id}',
            id=_id
        )

    @classmethod
    def close(cls, _id: int, operator_id: int):
        database.execute(
            """
                update "Order" set
                    processed_by = %(processed_by)s,
                    closed_at = %(closed_at)s
                where id = %(id)s
            """,
            f'Closing order #{_id} by operator {operator_id}',
            processed_by=operator_id,
            closed_at=datetime.datetime.now(),
            id=_id
        )

    @classmethod
    def place(cls, sub_id: int, total: decimal.Decimal, customer_id: int, coupon: str):
        return database.single(
            Order,
            """
                insert into "Order" (subscription, total, customer_id, coupon, created_at)
                values (%(sub_id)s, %(total)s, %(customer_id)s, %(coupon)s, %(created_at)s)
                returning *
            """,
            f'Placing new order on {sub_id=} by {customer_id} on total {total}₽',
            sub_id=sub_id,
            total=total,
            customer_id=customer_id,
            coupon=coupon,
            created_at=datetime.datetime.now()
        )
