import datetime
import typing

NOTIFY_CUSTOMER_BEFORE_DAYS = datetime.timedelta(days=3)


class Resource(typing.NamedTuple):
    type: str
    index: str
    path: str
    name: str


# Files that will be updated by /updrs command
UPDATE_RESOURCES = [
    Resource('document', 'netflix_bought_video', 'resources/NETFLIX-BOUGHT.mp4', 'NETFLIX-BOUGHT.mp4'),
    Resource('document', 'spotify_bought_video', 'resources/SPOTIFY-BOUGHT.mp4', 'SPOTIFY-BOUGHT.mp4'),
    Resource('photo', 'netflix_service_banner', 'resources/NETFLIX-BANNER.jpg', 'NETFLIX-BANNER.jpg'),
    Resource('photo', 'spotify_service_banner', 'resources/SPOTIFY-BANNER.jpg', 'SPOTIFY-BANNER.jpg'),
    Resource('photo', 'intro_banner', 'resources/INTRO.jpg', 'INTRO.jpg'),
]
