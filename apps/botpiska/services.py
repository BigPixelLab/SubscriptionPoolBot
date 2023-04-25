""" ... """
import typing


class Service(typing.NamedTuple):
    """ ... """
    id: str
    search_title: str
    showcase_template: str
    order_template: str = None
    has_subscription_plans: bool = True
    featured_subscription_id: str = None

    @classmethod
    def verify(cls, service: 'Service'):
        if service.has_subscription_plans and not service.order_template:
            raise ValueError(f"Service '{service.id}' that has subscription plans must have 'order_template' set")

    @classmethod
    def get_search_titles(cls) -> list[str]:
        """ ... """
        return [service.search_title for service in SERVICES]

    @classmethod
    def get_search_titles_map(cls) -> dict[str, 'Service']:
        """ ... """
        return {service.search_title: service for service in SERVICES}

    @classmethod
    def get_by_id(cls, id_: str) -> typing.Optional['Service']:
        return SERVICE_MAP.get(id_)


SERVICES: set[Service] = {
    Service(
        id='netflix',
        search_title='NETFLIX',
        showcase_template='apps/botpiska/templates/services/netflix/showcase.xml',
        order_template='apps/botpiska/templates/services/netflix/order.xml'
    ),
    Service(
        id='spotify',
        search_title='SPOTIFY',
        showcase_template='apps/botpiska/templates/services/spotify/showcase.xml',
        order_template='apps/botpiska/templates/services/spotify/order.xml',
        featured_subscription_id='spotify_ind_1y'
    ),
    Service(
        id='steam',
        search_title='STEAM',
        showcase_template='apps/botpiska/templates/services/steam/showcase.xml',
        has_subscription_plans=False
    )
}

for _service in SERVICES:
    Service.verify(_service)

SERVICE_MAP: dict[str, Service] = {service.id: service for service in SERVICES}
