import enum
import typing

from utils import database


# noinspection PyArgumentList
class ResourceType(enum.Enum):
    DOCUMENT = enum.auto()
    PHOTO = enum.auto()


class Resource(typing.NamedTuple):
    type: ResourceType
    index: str
    path: str
    name: str


# Files that will be updated by /updrs command
RESOURCES = [
    # MAIN
    Resource(
        index='intro_banner',
        path='resources/INTRO.jpg',
        name='INTRO.jpg',
        type=ResourceType.PHOTO
    ),

    # SERVICES
    Resource(
        index='netflix_bought_video',
        path='resources/NETFLIX-BOUGHT.mp4',
        name='NETFLIX-BOUGHT.mp4',
        type=ResourceType.DOCUMENT
    ),
    Resource(
        index='netflix_service_banner',
        path='resources/NETFLIX-BANNER.jpg',
        name='NETFLIX-BANNER.jpg',
        type=ResourceType.PHOTO
    ),
    Resource(
        index='spotify_bought_video',
        path='resources/SPOTIFY-BOUGHT.mp4',
        name='SPOTIFY-BOUGHT.mp4',
        type=ResourceType.DOCUMENT
    ),
    Resource(
        index='spotify_service_banner',
        path='resources/SPOTIFY-BANNER.jpg',
        name='SPOTIFY-BANNER.jpg',
        type=ResourceType.PHOTO
    ),

    # EVENTS
    Resource(
        index='one_plus_one_spotify_banner',
        path='resources/ONE_PLUS_ONE_SPOTIFY_BANNER.png',
        name='ONE_PLUS_ONE_SPOTIFY_BANNER.png',
        type=ResourceType.PHOTO
    ),
]


# Format: {bot_id: {file_index: file_id}}
_cached: dict[int, dict[str, str]] = {}

# Structure to quick-test valid file indexes
VALID_FILE_INDEXES = set(res.index for res in RESOURCES)


def get(index: str, *, key: int, use_cache: bool = True) -> str:
    """ Возвращает file_id ресурса """
    _cached.setdefault(key, {})
    cache = _cached.get(key)

    file_index = str(index)
    assert file_index in VALID_FILE_INDEXES

    if use_cache and (file_id := cache.get(file_index)):
        return file_id

    file_id = database.single_value(
        f""" select {file_index} from "File" where bot_id = %(bot_id)s """,
        f'Caching file with index "{file_index}"',
        bot_id=key
    )

    cache[file_index] = file_id
    return file_id


def update(index: str, file_id: str, /, key: int):
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
