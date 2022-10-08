import datetime
import typing

from apps.operator.models import Employee
from apps.search.models import Subscription
from utils import database


class Order(typing.NamedTuple):
    id: int
    subscription: int  # Subscription.id
    coupon: typing.Optional[str]  # Coupon  (for promo-coupons)
    total: float
 
    customer_id: int
    processed_by: typing.Optional[int]  # Employee.id
    created_at: datetime.datetime
    closed_at: typing.Optional[datetime.datetime]

    def get_subscription(self):
        return database.single(Subscription, 'select * from "Subscription" where id = %(id)s', id=self.subscription)

    def get_processed_by(self):
        if self.processed_by is None:
            return None
        return database.single(Employee, 'select * from "Employee" where id = %(id)s', id=self.processed_by)

    @classmethod
    def get(cls, _id: int) -> 'Order':
        return database.single(
            Order,
            """ select * from "Order" where id = %(id)s """,
            f'Getting order with id {_id}',
            id=_id
        )

    @classmethod
    def mark_as_taken(cls, order_id: int, operator_id: int):
        database.execute(
            """
                update "Order" set
                    processed_by = %(operator_id)s
                where id = %(order_id)s
            """,
            f'Marking order #{order_id} as taken',
            operator_id=operator_id,
            order_id=order_id
        )
