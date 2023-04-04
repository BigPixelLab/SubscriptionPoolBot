from __future__ import annotations

import contextlib
import datetime

import aiogram
import aiogram.exceptions
from aiogram.dispatcher.event.bases import CancelHandler

from . import globals_
from .configure import ResponseConfig
from .lock import Lock
from .respond import respond
from .response import Response
from .waiting_message_manager import WaitingMessageManager


class ResponseMiddleware:
    def __init__(self):
        self._set_locks = set()

    def get_message(self, event: aiogram.types.TelegramObject) -> tuple[aiogram.types.Message]:
        """ ... """
        raise NotImplementedError

    async def answer(self, event: aiogram.types.TelegramObject, text: str) -> None:
        """ ... """
        raise NotImplementedError

    async def __call__(self, handler, event: aiogram.types.TelegramObject, data: dict):

        message = self.get_message(event)

        # noinspection PyTypeChecker
        user: aiogram.types.User = aiogram.types.User.get_current()
        # noinspection PyTypeChecker
        chat: aiogram.types.Chat = aiogram.types.Chat.get_current()
        bot = aiogram.Bot.get_current()

        config: ResponseConfig = data.pop('__response_config', None)

        lock = None
        if config and config.lock:
            lock = Lock(self._set_locks, key=(bot.id, user.id, config.lock))

        if isinstance(lock, Lock) and lock.is_set():
            raise CancelHandler()

        waiting = None
        if config and config.waiting:
            waiting = WaitingMessageManager(config.waiting)

        with lock or contextlib.nullcontext():
            # noinspection PyUnusedLocal
            responses = []

            global_time_cv_token = globals_.global_time.set(datetime.datetime.now())
            message_cv_token = globals_.message.set(message)

            async with waiting or contextlib.AsyncExitStack():
                data.update({'bot': bot, 'user': user, 'chat': chat})
                responses: list[Response] = await handler(event, data)

            await respond(filter(None, responses or []))

            globals_.global_time.reset(global_time_cv_token)
            globals_.message.reset(message_cv_token)

            await self.answer(event, config and config.answer)


class MessageResponseMiddleware(ResponseMiddleware):
    """ ... """

    def get_message(self, event: aiogram.types.Message) -> aiogram.types.Message:
        return event

    async def answer(self, event: aiogram.types.Message, text: str | None) -> None:
        pass


class CallbackQueryResponseMiddleware(ResponseMiddleware):
    """ ... """

    def get_message(self, event: aiogram.types.CallbackQuery) -> aiogram.types.Message:
        return event.message

    async def answer(self, event: aiogram.types.CallbackQuery, text: str | None) -> None:
        await event.answer(text)


__all__ = (
    'ResponseMiddleware',
    'MessageResponseMiddleware',
    'CallbackQueryResponseMiddleware'
)
