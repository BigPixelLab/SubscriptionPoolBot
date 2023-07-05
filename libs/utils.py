from __future__ import annotations

import asyncio
import typing

T = typing.TypeVar('T')
K = typing.TypeVar('K')


def find(obj: K, sequence: typing.Sequence[T], /, key: typing.Callable[[T], K] = lambda x: x) -> T | None:
    try:
        return next(i for i in sequence if key(i) == obj)
    except StopIteration:
        return None


async def do_nothing(*_, **__):
    """ Можно использовать как заглушку, чтобы игнорировать ошибки response-ах,
        например rs.delete(on_error=do_nothing) """
    await asyncio.sleep(0)
