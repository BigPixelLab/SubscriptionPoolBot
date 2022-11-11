from __future__ import annotations

from enum import auto

from aiogram import Bot
from strenum import SnakeCaseStrEnum

from utils import database


# noinspection PyArgumentList
class FileIndex(SnakeCaseStrEnum):
    """
    Перечисление всех ресурсов, используемых ботом.
    Используется для получения file_id из базы данных,
    поэтому все поля данного объекта должны иметь там
    колонку с таким же именем в snake_case
    """
    INTRO_BANNER = auto()
    NETFLIX_SERVICE_BANNER = auto()
    NETFLIX_BOUGHT_VIDEO = auto()
    SPOTIFY_SERVICE_BANNER = auto()
    SPOTIFY_BOUGHT_VIDEO = auto()
    ONE_PLUS_ONE_SPOTIFY_BANNER = auto()


# Format: {bot_id: {file_index: file_id}}
_cached: dict[int, dict[str, str]] = {}

# Structure to quick-test valid file indexes
# noinspection PyUnresolvedReferences
VALID_FILE_INDEXES = set(fi.value for fi in FileIndex)


def get(fi: FileIndex | str, *, use_cache: bool = True, bot: Bot = None) -> str:
    """ Возвращает file_id ресурса """
    bot = bot or Bot.get_current()
    _cached.setdefault(bot.id, {})
    cache = _cached.get(bot.id)

    file_index = str(fi)
    assert file_index in VALID_FILE_INDEXES

    if use_cache and (file_id := cache.get(file_index)):
        return file_id

    file_id = database.single_value(
        f""" select {file_index} from "File" where bot_id = %(bot_id)s """,
        f'Caching file with index "{file_index}"',
        bot_id=bot.id
    )

    cache[file_index] = file_id
    return file_id


def clear_cache(*, file_index: str = None, bot: Bot = None):
    """
    Очищает кэш file_id ресурсов. Удаляет кэш конкретного ресурса,
    если задан file_index
    """
    bot = bot or Bot.get_current()
    cache = _cached.get(bot.id)
    if cache is None:
        return
    if file_index in cache:
        del cache[file_index]
        return
    cache.clear()
