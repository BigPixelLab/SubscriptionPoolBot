from __future__ import annotations

import datetime
import typing


class SeasonType:
    WINTER = 'ЗИМНИЙ СЕЗОН'
    SPRING = 'ВЕСЕННИЙ СЕЗОН'
    SUMMER = 'ЛЕТНИЙ СЕЗОН'
    AUTUMN = 'ОСЕННИЙ СЕЗОН'


class Season(typing.NamedTuple):
    season_type: str


SEASON_TO_TIME = {
    SeasonType.WINTER: lambda x, y: datetime.datetime(y, 12, 1) <= x or x < datetime.datetime(y, 3, 1),
    SeasonType.SPRING: lambda x, y: datetime.datetime(y, 3, 1) <= x < datetime.datetime(y, 6, 1),
    SeasonType.SUMMER: lambda x, y: datetime.datetime(y, 6, 1) <= x < datetime.datetime(y, 9, 1),
    SeasonType.AUTUMN: lambda x, y: datetime.datetime(y, 9, 1) <= x < datetime.datetime(y, 12, 1)
}


def get_current_season():
    """ Возвращает идущий в данный момент сезон """
    return Season(
        season_type=SeasonType.SPRING
    )
