import typing
from typing import TypeVar

from aiogram.types import InputFile

T = TypeVar('T')


class TextLayout:
    def __init__(self):
        self._paragraphs: list[str] = []
        self._buffer: list[str] = []

    def add(self, text: str):
        """ ... """
        if not text:
            return
        self._buffer.append(text)

    def add_paragraph(self, text: str):
        """ ... """
        self.close_buffer()
        self._paragraphs.append(text)

    def close_buffer(self):
        """ ... """
        if not self._buffer:
            return
        paragraph = ' '.join(self._buffer)
        self._paragraphs.append(paragraph)
        self._buffer.clear()

    def result(self) -> str:
        """ ... """
        self.close_buffer()
        return '\n'.join(self._paragraphs)


class KeyboardLayout:
    def __init__(self):
        self._rows: list[list] = []
        self._buffer: list = []

    def add(self, button):
        """ ... """
        self._buffer.append(button)

    def add_row(self, row: list):
        """ ... """
        self.close_buffer()
        self._rows.append(row)

    def close_buffer(self):
        """ ... """
        if not self._buffer:
            return
        self._rows.append(self._buffer)
        self._buffer = []

    def result(self) -> list[list]:
        """ ... """
        self.close_buffer()
        return self._rows


def _sub_type(name: str, tp: T) -> T:
    return type(name, (tp,), {})


BlockText = _sub_type('BlockText', str)
InlineText = _sub_type('InlineText', str)
KeyboardLayoutRow = _sub_type('KeyboardLayoutRow', list)

ImageID = _sub_type('ImageID', str)
AnimationID = _sub_type('AnimationID', str)


class ImageFile(typing.NamedTuple):
    input_file: InputFile


class AnimationFile(typing.NamedTuple):
    input_file: InputFile


__all__ = (
    'TextLayout',
    'KeyboardLayout',
    'BlockText',
    'InlineText',
    'KeyboardLayoutRow',
    'ImageID',
    'AnimationID',
    'ImageFile',
    'AnimationFile',
)
