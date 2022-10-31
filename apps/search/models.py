import datetime
import decimal
import typing

from utils import database


class Service(typing.NamedTuple):
    id: int
    """Service ID"""
    name: str
    """Full name of the service"""
    description: str
    """Full description. Used in service cards"""
    banner: str
    """Banner to use in service card"""
    bought: str
    """Banner to show then subscription of this service is bought"""

    @classmethod
    def get(cls, _id: int) -> 'Service':
        return database.single(
            Service,
            """ select * from "Service" where id = %(id)s """,
            f'Getting service with id {_id}',
            id=_id
        )

    @classmethod
    def get_name(cls, _id: int) -> str:
        return database.single_value(
            """ select name from "Service" where id=%(id)s """,
            f'Getting name of service with id {_id}',
            id=_id
        )


class Subscription(typing.NamedTuple):
    id: int
    """Subscription ID"""
    service: int
    """Service ID for which this subscription is for"""
    duration: datetime.timedelta
    """Duration of the subscription. Used for notifications"""
    price: decimal.Decimal
    """Price of the subscription"""
    name: str
    """Full name, like "4k 30 дней". Will be displayed to user"""
    type: str
    """Category name, like "4k". Used just for sorting"""
    is_code_required: bool
    """If set, will not be shown if no activation code is available"""

    def get_service(self) -> Service:
        return database.single(
            Service,
            """ select * from "Service" where id = %(id)s """,
            f'Getting service {self.service} for subscription {self.id}',
            id=self.service
        )

    @classmethod
    def get(cls, _id: int) -> 'Subscription':
        return database.single(
            Subscription,
            """ select * from "Subscription" where id = %(id)s """,
            f'Getting subscription {_id}',
            id=_id
        )

    @classmethod
    def get_name(cls, _id: int) -> str:
        return database.single_value(
            """ select name from "Subscription" where id = %(id)s """,
            f'Getting subscription name {_id}',
            id=_id
        )

    @classmethod
    def get_full_name_parts(cls, _id: int) -> tuple[str, str]:
        return tuple(database.single_row(
            """
                select E.name, S.name from "Subscription" S
                    join "Service" E on S.service = E.id
                where S.id = %(id)s
            """,
            f'Getting full name parts for subscription {_id}',
            id=_id
        ))
