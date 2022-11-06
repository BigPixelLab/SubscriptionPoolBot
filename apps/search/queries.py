from utils import database
from . import models


def get_services() -> list[models.Service]:
    return database.fetch(
        models.Service,
        """ select * from "Service" """,
        'Getting list of services'
    )


def get_sub_plans(service_id: int) -> list[models.Subscription]:
    """
    Возвращает планы подписки для конкретного сервиса,
    отсортированные по типу и длительности
    """
    return database.fetch(
        models.Subscription,
        """
            select * from "Subscription" S
            where S.service = %(service_id)s
            order by S.type, S.duration
        """,
        f'Getting subscription plans for "{service_id=}"',
        service_id=service_id
    )
