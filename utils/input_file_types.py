import io
from typing import AsyncGenerator

from aiogram.types import InputFile
from aiogram.types.input_file import DEFAULT_CHUNK_SIZE


class BufferedInputFile(InputFile):
    def __init__(self, buffer: io.BytesIO, filename: str, chunk_size: int = DEFAULT_CHUNK_SIZE):
        super().__init__(filename=filename, chunk_size=chunk_size)

        self.data = buffer

    async def read(self, chunk_size: int) -> AsyncGenerator[bytes, None]:
        while chunk := self.data.read(chunk_size):
            yield chunk
