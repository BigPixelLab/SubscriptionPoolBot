from __future__ import annotations

import os.path
import typing
from pathlib import Path

T = typing.TypeVar('T')
K = typing.TypeVar('K')


def find(obj: K, sequence: typing.Sequence[T], /, key: typing.Callable[[T], K] = lambda x: x) -> T | None:
    try:
        return next(i for i in sequence if key(i) == obj)
    except StopIteration:
        return None
