import datetime
import typing


class Notification(typing.NamedTuple):
    id: int
    order: int  # Order.id
    created_at: datetime.date
