import datetime
import typing
from dataclasses import dataclass

from croniter import croniter

import response_system as rs


@dataclass
class Event:
    pass


class ConditionChecker:
    """ Базовый класс для проверки того, должен ли быть запущен обработчик события """

    def check(self, dt: datetime.datetime) -> bool:
        """ Возвращает True, если обработчик может быть запущен """
        raise NotImplementedError


class Cron(ConditionChecker):
    def __init__(self, cron: str, **duration):
        super().__init__()
        self._duration = datetime.timedelta(**duration)
        self._cron = cron

    def check(self, dt: datetime.datetime) -> bool:
        min_datetime = croniter(self._cron, dt).get_prev(datetime.datetime)
        return min_datetime <= dt <= min_datetime + self._duration


class RegisteredEventHandler(typing.NamedTuple):
    condition: ConditionChecker
    handler: typing.Callable[[Event], typing.Awaitable[rs.Response]]


_registered_event_handlers: dict[str, list[RegisteredEventHandler]] = {}


def embedded_event(*, trigger: str, on: ConditionChecker = None):
    def decorator(function):

        async def wrapper(event):
            rs.respond(await function(event))

        _registered_event_handlers.setdefault(trigger, [])
        _registered_event_handlers[trigger].append(
            RegisteredEventHandler(on, wrapper)
        )

        return wrapper
    return decorator


async def trigger_embedded_events(trigger: str, event: Event):
    try:
        handlers = _registered_event_handlers[trigger]
    except KeyError:
        return

    time = rs.global_time.get()

    for handler in handlers:
        if handler.condition is None or handler.condition.check(time):
            await handler.handler(event)
