import contextlib
import typing

import aiogram.types
import peewee

_resource_cache = {}


def resource(path: str) -> typing.Union[aiogram.types.InputFile, str]:
    """ Возвращает file-id ресурса, или InputFile для его загрузки """
    from apps.maintenance.models import ResourceCache
    global _resource_cache

    # Will try to get resource from cache, if failed continues
    with contextlib.suppress(KeyError):
        return _resource_cache[path]

    # Tries to get resource from database, if failed continues
    bot = aiogram.Bot.get_current()
    with contextlib.suppress(peewee.DoesNotExist):

        # Getting from database
        res = ResourceCache.select().where(
            ResourceCache.bot_id == bot.id, ResourceCache.path == path
        ).get()

        # Saving to cache (if found in database)
        _resource_cache[path] = res.file_id

        return res.file_id

    # Returns resource from file system
    return aiogram.types.FSInputFile(path)


def load(path: str, file_id: str) -> None:
    """ Загружает file-id в систему """
    from apps.maintenance.models import ResourceCache
    global _resource_cache

    bot = aiogram.Bot.get_current()

    # Saving to cache
    _resource_cache[path] = file_id

    # Saving to database
    ResourceCache(
        path=path,
        bot_id=bot.id,
        file_id=file_id
    ).save(force_insert=True)


__all__ = ('resource',)
