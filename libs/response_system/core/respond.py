import typing

from . import globals_
from .response import Response


async def respond(responses: typing.Iterable[Response]):
    """ Преждевременно выполняет Response-ы """

    message = globals_.message.get()

    for response in responses:
        await response(message)


__all__ = ('respond',)
