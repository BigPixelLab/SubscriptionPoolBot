import datetime
import typing

from apps.operators.models import Employee
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
    closed_at: typing.Optional[datetime.datetime]  # TODO: Change in the database

    def get_subscription(self):
        return database.single(Subscription, 'select * from "Subscription" where id = %(id)s', id=self.subscription)

    def get_processed_by(self):
        if self.processed_by is None:
            return None
        return database.single(Employee, 'select * from "Employee" where id = %(id)s', id=self.processed_by)
