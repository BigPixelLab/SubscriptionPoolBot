import datetime
import typing


class OrderInfo(typing.NamedTuple):
    order_id: int
    created_at: datetime.datetime
    is_taken: bool
    service: str
    subscription: str
    sub_price: float
