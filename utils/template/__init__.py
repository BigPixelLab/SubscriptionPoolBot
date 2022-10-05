from __future__ import annotations

import os

from .types_ import MessageRender, MessageRenderList
from . import tags


def render(path: str | os.PathLike, context: dict) -> MessageRenderList:
    from .parsing import parse_template
    from xml.dom import minidom
    document = minidom.parse(str(path))
    return parse_template(document, context)
