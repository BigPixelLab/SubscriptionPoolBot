""" ... """
import typing


class Service(typing.NamedTuple):
    """ ... """
    id: str
    search_title: str
    showcase_template: str
    has_subscription_plans: bool = True
    featured_subscription_id: str = None

    @classmethod
    def get_search_titles(cls) -> list[str]:
        """ ... """
        return [service.search_title for service in SERVICES]

    @classmethod
    def get_search_titles_map(cls) -> dict[str, 'Service']:
        """ ... """
        return {service.search_title: service for service in SERVICES}


SERVICES = {
    Service(
        id='netflix',
        search_title='NETFLIX',
        showcase_template='apps/botpiska/templates/services/netflix/showcase.xml'
    ),
    Service(
        id='spotify',
        search_title='SPOTIFY',
        showcase_template='apps/botpiska/templates/services/spotify/showcase.xml',
        featured_subscription_id='spotify_ind_1y'
    ),
    Service(
        id='steam',
        search_title='STEAM',
        showcase_template='apps/botpiska/templates/services/steam/showcase.xml',
        has_subscription_plans=False
    )
}

SERVICE_MAP = {service.id: service for service in SERVICES}
