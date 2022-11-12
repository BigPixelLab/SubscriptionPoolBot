from __future__ import annotations

import typing
from contextlib import suppress

import aiogram
import aiogram.exceptions

T = typing.TypeVar('T')
K = typing.TypeVar('K')


def find(obj: K, sequence: typing.Sequence[T], /, key: typing.Callable[[T], K] = lambda x: x) -> T | None:
    try:
        return next(i for i in sequence if key(i) == obj)
    except StopIteration:
        return None


async def safe_answer(query: aiogram.types.CallbackQuery):
    """
    Безопасная альтернатива query.answer(), не
    выдаёт ошибку в случае если query просрочен
    """
    with suppress(aiogram.exceptions.TelegramBadRequest):
        await query.answer()
