import io
from typing import AsyncGenerator

from PIL.Image import Image
from aiogram.types import InputFile
from aiogram.types.input_file import DEFAULT_CHUNK_SIZE


class PilImageInputFile(InputFile):
    """ Allows to use BytesIO as a file source.
       Great for sending images generated at runtime """

    def __init__(self, buffer: io.BytesIO, filename: str, chunk_size: int = DEFAULT_CHUNK_SIZE):
        super().__init__(filename=filename, chunk_size=chunk_size)
        self.data = buffer

    @classmethod
    def from_image(cls, image: Image, filename: str, format='PNG',
                   chunk_size: int = DEFAULT_CHUNK_SIZE) -> 'PilImageInputFile':
        image.save(buffer := io.BytesIO(), format=format)
        buffer.seek(0)
        return PilImageInputFile(buffer, filename, chunk_size=chunk_size)

    async def read(self, chunk_size: int) -> AsyncGenerator[bytes, None]:
        while chunk := self.data.read(chunk_size):
            yield chunk


__all__ = (
    'PilImageInputFile',
)
