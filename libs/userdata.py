from __future__ import annotations

import aiogram
from aiogram.fsm.storage.base import StorageKey, BaseStorage

__storage__: BaseStorage = ...


async def get_data(user_id: int, fields: list[str] = None, /, *, extract_field=dict.get) -> tuple | dict:
    """ Простой интерфейс к Storage библиотеки aiogram.
        Если указан fields - возвращает кортеж со значениями
        указанных полей, если нет, то весь dict """

    if __storage__ is ...:
        raise TypeError('No __storage__ is specified')

    if len(fields) == 0:
        raise ValueError('List of fields can not be empty')

    bot = aiogram.Bot.get_current()
    key = StorageKey(bot.id, user_id, user_id)
    data = await __storage__.get_data(bot, key)

    if fields is None:
        return data

    return tuple(extract_field(data, key) for key in fields)


async def set_data(user_id: int, data: dict = None, /, **kwargs):
    """ Простой интерфейс к Storage библиотеки aiogram.
        Обновляет сохранённые данные указанными значениями.
        Данные могут быть указаны как словарём, так и
        с помощью kwargs """

    if __storage__ is ...:
        raise TypeError('No __storage__ is specified')

    if data and kwargs:
        raise ValueError('Data can not be specified with both '
                         'data argument and kwargs')

    bot = aiogram.Bot.get_current()
    key = StorageKey(bot.id, user_id, user_id)
    data_ = await __storage__.get_data(bot, key)

    data_.update(data or kwargs)

    await __storage__.update_data(bot, key, data or kwargs)


__all__ = ('get_data', 'set_data')
