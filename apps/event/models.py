from __future__ import annotations

import datetime
import typing

from utils import database


class Event(typing.NamedTuple):
    name: str
    """ ID of the event """
    starts_at: datetime.datetime
    """ Date and time of the start of the event """
    ends_at: datetime.datetime
    """ Date and time of the end of the event """

    @classmethod
    def is_going_now(cls, name: str) -> 'Event' | None:
        """ Проходит ли указанное событие сейчас """
        return database.single(
            Event,
            """
                select * from "Event"
                where 
                    %(name)s = name and
                    %(now)s between starts_at and ends_at
            """,
            f'Checking if event "{name}" is going now',
            now=datetime.datetime.now(),
            name=name,
        )
