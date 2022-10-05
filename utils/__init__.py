from __future__ import annotations

import typing

T = typing.TypeVar('T')


def first_of(smth: typing.Sequence[T]) -> T | None:
    try:
        return next(iter(smth))
    except StopIteration:
        return None
