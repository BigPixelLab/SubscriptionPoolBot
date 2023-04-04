from __future__ import annotations

import dataclasses

from message_render import MessageRender


@dataclasses.dataclass
class ResponseConfig:
    waiting: MessageRender | None
    answer: str | None
    lock: str


def configure(waiting: MessageRender = None, answer: str = None, lock: str = None):
    """ ... """

    async def _filter(*_, **__) -> dict | bool:
        return {'__response_config': ResponseConfig(waiting, answer, lock)}

    return _filter
