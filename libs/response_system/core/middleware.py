import contextlib
import datetime
import logging
import typing

import aiogram
import aiogram.exceptions
from aiogram.dispatcher.event.bases import CancelHandler

from message_render import MessageRender
from . import globals_
from .configure import ResponseConfig
from .exceptions import UserFriendlyException
from .responses import Response

logger = logging.getLogger(__name__)


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

            global_time_cv_token = globals_.global_time.set(datetime.datetime.now())
            response_var_cv_token = globals_.response_var.set(Response())
            message_var_cv_token = globals_.message_var.set(message)

            async with waiting or contextlib.AsyncExitStack():
                data.update({'bot': bot, 'user': user, 'chat': chat})

                try:
                    response: Response = await handler(event, data)
                    response += globals_.response_var.get()

                except UserFriendlyException as error:
                    response = error.response()

            for action in response:
                try:
                    await action
                except Exception:
                    logger.error('RESPONSE EXCEPTION AT (' + getattr(handler, '__name__', 'handler') + ')')
                    raise

            globals_.global_time.reset(global_time_cv_token)
            globals_.response_var.reset(response_var_cv_token)
            globals_.message_var.reset(message_var_cv_token)

            await self.answer(event, config.answer if config and config.answer else None)


class MessageResponseMiddleware(ResponseMiddleware):
    """ ... """

    def get_message(self, event: aiogram.types.Message) -> aiogram.types.Message:
        return event

    async def answer(self, event: aiogram.types.Message, text: typing.Optional[str]) -> None:
        pass


class CallbackQueryResponseMiddleware(ResponseMiddleware):
    """ ... """

    def get_message(self, event: aiogram.types.CallbackQuery) -> aiogram.types.Message:
        return event.message

    async def answer(self, event: aiogram.types.CallbackQuery, text: typing.Optional[str]) -> None:
        await event.answer(text)


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


class Lock:
    def __init__(self, storage: set[tuple], key: tuple):
        self.storage = storage
        self.key = key

    def is_set(self):
        return self.key in self.storage

    def __enter__(self):
        self.storage.add(self.key)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.storage.remove(self.key)
