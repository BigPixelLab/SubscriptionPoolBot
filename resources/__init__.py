import enum
from dataclasses import dataclass

from utils import database


# noinspection PyArgumentList
class ResourceType(enum.Enum):
    DOCUMENT = enum.auto()
    PHOTO = enum.auto()


@dataclass
class Resource:
    index: str
    path: str


@dataclass
class UploadedResource(Resource):
    name: str
    type: ResourceType


@dataclass
class LocalResource(Resource):
    pass


# Files that will be updated by /updrs command
# and uploaded to telegram
RESOURCES = [
    # MAIN
    UploadedResource(
        index='intro_banner',
        path='resources/botpiska/INTRO.jpg',
        name='INTRO.jpg',
        type=ResourceType.PHOTO
    ),
    LocalResource(
        index='bill',
        path='resources/botpiska/BILL.png',
    ),
    LocalResource(
        index='bill_font',
        path='resources/botpiska/shtrixfr57.ttf'
    ),

    # SERVICES
    UploadedResource(
        index='netflix_bought_video',
        path='resources/services/netflix/NETFLIX-BOUGHT.mp4',
        name='NETFLIX-BOUGHT.mp4',
        type=ResourceType.DOCUMENT
    ),
    UploadedResource(
        index='netflix_service_banner',
        path='resources/services/netflix/NETFLIX-BANNER.jpg',
        name='NETFLIX-BANNER.jpg',
        type=ResourceType.PHOTO
    ),
    UploadedResource(
        index='spotify_bought_video',
        path='resources/services/spotify/SPOTIFY-BOUGHT.mp4',
        name='SPOTIFY-BOUGHT.mp4',
        type=ResourceType.DOCUMENT
    ),
    UploadedResource(
        index='spotify_service_banner',
        path='resources/services/spotify/SPOTIFY-BANNER.jpg',
        name='SPOTIFY-BANNER.jpg',
        type=ResourceType.PHOTO
    ),
    LocalResource(
        index='spotify_service_term',
        path='resources/services/spotify/spotify_terms.xml'
    ),
    LocalResource(
        index='netflix_service_term',
        path='resources/services/netflix/netflix_terms.xml'
    ),

    # EVENTS
    UploadedResource(
        index='one_plus_one_spotify_3h_banner',
        path='resources/events/one_plus_one_spotify/ONE_PLUS_ONE_SPOTIFY_3H_BANNER.png',
        name='ONE_PLUS_ONE_SPOTIFY_3H_BANNER.png',
        type=ResourceType.PHOTO
    ),
    UploadedResource(
        index='one_plus_one_spotify_10h_banner',
        path='resources/events/one_plus_one_spotify/ONE_PLUS_ONE_SPOTIFY_10H_BANNER.png',
        name='ONE_PLUS_ONE_SPOTIFY_10H_BANNER.png',
        type=ResourceType.PHOTO
    ),

    UploadedResource(
        index='promo_for_fastest_30',
        path='resources/events/daily_posts/PROMO-FOR-FASTEST-30.jpg',
        name='PROMO-FOR-FASTEST-30.jpg',
        type=ResourceType.PHOTO
    ),

    UploadedResource(
        index='lottery_box_banner',
        path='resources/events/daily_posts/lottery_box/lottery_box_banner.png',
        name='lottery_box_banner.png',
        type=ResourceType.PHOTO
    ),
    UploadedResource(
        index='lottery_box_10',
        path='resources/events/daily_posts/lottery_box/lottery_box_10.png',
        name='lottery_box_10.png',
        type=ResourceType.PHOTO
    ),
    UploadedResource(
        index='lottery_box_15',
        path='resources/events/daily_posts/lottery_box/lottery_box_15.png',
        name='lottery_box_15.png',
        type=ResourceType.PHOTO
    ),
    UploadedResource(
        index='lottery_box_20',
        path='resources/events/daily_posts/lottery_box/lottery_box_20.png',
        name='lottery_box_20.png',
        type=ResourceType.PHOTO
    ),
    UploadedResource(
        index='lottery_box_25',
        path='resources/events/daily_posts/lottery_box/lottery_box_25.png',
        name='lottery_box_25.png',
        type=ResourceType.PHOTO
    ),
    UploadedResource(
        index='lottery_box_30',
        path='resources/events/daily_posts/lottery_box/lottery_box_30.png',
        name='lottery_box_30.png',
        type=ResourceType.PHOTO
    ),
    UploadedResource(
        index='lottery_box_50',
        path='resources/events/daily_posts/lottery_box/lottery_box_50.png',
        name='lottery_box_50.png',
        type=ResourceType.PHOTO
    ),
    UploadedResource(
        index='lottery_box_100',
        path='resources/events/daily_posts/lottery_box/lottery_box_100.png',
        name='lottery_box_100.png',
        type=ResourceType.PHOTO
    ),
    UploadedResource(
        index='lottery_box_spotify',
        path='resources/events/daily_posts/lottery_box/lottery_box_spotify.png',
        name='lottery_box_spotify.png',
        type=ResourceType.PHOTO
    ),
    UploadedResource(
        index='lottery_box_netflix',
        path='resources/events/daily_posts/lottery_box/lottery_box_netflix.png',
        name='lottery_box_netflix.png',
        type=ResourceType.PHOTO
    ),
    LocalResource(
        index='lottery_box_prize_spotify_pr_month_free',
        path='resources/events/daily_posts/lottery_box/templates/prize_spotify_pr_month_free.xml'
    ),
    LocalResource(
        index='lottery_box_prize_spotify_pr_year_30',
        path='resources/events/daily_posts/lottery_box/templates/prize_spotify_pr_year_30.xml'
    ),
    LocalResource(
        index='lottery_box_prize_netflix_4k_month_30',
        path='resources/events/daily_posts/lottery_box/templates/prize_netflix_4k_month_30.xml'
    ),
    LocalResource(
        index='lottery_box_prize_any_25',
        path='resources/events/daily_posts/lottery_box/templates/prize_any_25.xml'
    ),
    LocalResource(
        index='lottery_box_prize_any_20',
        path='resources/events/daily_posts/lottery_box/templates/prize_any_20.xml'
    ),
UploadedResource(
        index='bad_news',
        path='resources/events/res.png',
        name='bad_news.png',
        type=ResourceType.PHOTO
    ),
]


# Format: {bot_id: {file_index: file_id}}
_cached: dict[int, dict[str, str]] = {}

UPLOADED_RESOURCES = [res for res in RESOURCES if isinstance(res, UploadedResource)]
RESOURCE_INDEX_MAP = {res.index: res for res in RESOURCES if isinstance(res, Resource)}

# Structure to quick-test valid file indexes
UPLOADED_RESOURCE_INDEXES = set(
    res.index
    for res in RESOURCE_INDEX_MAP.values()
    if isinstance(res, UploadedResource)
)
RESOURCE_INDEXES = set(RESOURCE_INDEX_MAP.keys())


def get(index: str, *, key: int, use_cache: bool = True) -> str:
    """ Возвращает file_id для UploadedResource по индексу """
    assert index in UPLOADED_RESOURCE_INDEXES

    _cached.setdefault(key, {})
    cache = _cached.get(key)

    if use_cache and (file_id := cache.get(index)):
        return file_id

    file_id = database.single_value(
        f""" select {index} from "File" where bot_id = %(bot_id)s """,
        f'Caching file with index "{index}"',
        bot_id=key
    )

    cache[index] = file_id
    return file_id


def update(index: str, file_id: str, /, key: int):
    """ Обновляет file_id по индексу, только для UploadedResource """
    assert index in UPLOADED_RESOURCE_INDEXES
    database.execute(
        f"""
            insert into "File" (bot_id, {index})
            values (%(bot_id)s, %(file_id)s)
            on conflict (bot_id) do update set
                {index} = excluded.{index}
        """,
        f'Updating {index=} to {file_id=}',
        file_id=file_id,
        bot_id=key
    )
    clear_cache(file_index=index, key=key)


def resolve(index: str) -> Resource:
    """ Возвращает объект ресурса по его индексу """
    assert index in RESOURCE_INDEXES
    return RESOURCE_INDEX_MAP[index]


def clear_cache(*, key: int, file_index: str = None):
    """
    Очищает кэш file_id ресурсов. Удаляет кэш конкретного ресурса,
    если задан file_index
    """
    cache = _cached.get(key)
    if cache is None:
        return
    if file_index in cache:
        del cache[file_index]
        return
    cache.clear()
