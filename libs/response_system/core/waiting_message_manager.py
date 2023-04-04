import contextlib

import aiogram
import aiogram.exceptions

from message_render import MessageRender


class WaitingMessageManager:
    def __init__(self, render: MessageRender):
        self.render: MessageRender = render
        self.message: aiogram.types.Message

    async def __aenter__(self):
        # noinspection PyTypeChecker
        chat: aiogram.types.Chat = aiogram.types.Chat.get_current()
        with contextlib.suppress(aiogram.exceptions.TelegramForbiddenError):
            self.message = await self.render.send(chat.id)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not hasattr(self, 'message'):
            return
        with contextlib.suppress(aiogram.exceptions.TelegramForbiddenError):
            await self.message.delete()
