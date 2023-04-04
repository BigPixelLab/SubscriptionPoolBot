from __future__ import annotations

import abc
import asyncio
import logging

import aiogram.types
import aiogram.exceptions

from message_render import MessageRender, MessageRenderList
from response_system.core.slot import Slot

logger = logging.getLogger(__name__)


class Response(abc.ABC):

    @abc.abstractmethod
    async def __call__(self, message: aiogram.types.Message | None):
        raise NotImplementedError


class FunctionCallResponse(Response):
    """ Use as: FunctionCallResponse(lambda: function(..args..)) """

    def __init__(self, function):
        self.function = function

    async def __call__(self, message):
        self.function()


class AsyncCallResponse(Response):
    """ Use as: AsyncCallResponse(async_function(..args..)) """

    def __init__(self, awaitable):
        self.awaitable = awaitable

    async def __call__(self, message):
        await self.awaitable


class AiogramResponseMixin:
    def __init__(self, on_forbidden_error=None, on_bad_request=None, on_success=None):
        self.on_forbidden_error = Slot(on_forbidden_error)
        self.on_bad_request = Slot(on_bad_request)
        self.on_success = Slot(on_success)

    async def capture(self, awaitable):
        try:
            results = await awaitable
        except aiogram.exceptions.TelegramForbiddenError as error:
            if not await self.on_forbidden_error.emit():
                logger.error(error)
            return False
        except aiogram.exceptions.TelegramBadRequest as error:
            if not await self.on_bad_request.emit():
                logger.error(error)
            return False
        await self.on_success.emit(results)
        return True


class DeleteMessageResponse(Response, AiogramResponseMixin):
    def __init__(self, message_id: int = None, chat_id: int = None, bot: aiogram.Bot = None, **kwargs):
        AiogramResponseMixin.__init__(self, **kwargs)

        if chat_id and not message_id:
            raise ValueError('Chat can not be passed without message')

        self.message_id = message_id
        self.chat_id = chat_id
        self.bot = bot

    async def __call__(self, message):
        bot = self.bot or aiogram.Bot.get_current()
        message_id = self.message_id or message.message_id
        chat_id = self.chat_id or message.chat.id
        await self.capture(bot.delete_message(chat_id, message_id))


class EditMessageResponse(Response, AiogramResponseMixin):
    def __init__(self, edit_to: MessageRender, message: aiogram.types.Message = None,
                 bot: aiogram.Bot = None, **kwargs):
        AiogramResponseMixin.__init__(self, **kwargs)
        self.edit_to = edit_to
        self.message = message
        self.bot = bot

    async def __call__(self, message):
        bot = self.bot or aiogram.Bot.get_current()
        message = self.message or message
        await self.capture(self.edit_to.edit(message, bot=bot))


class SendMessageResponse(Response, AiogramResponseMixin):
    def __init__(self, to_send: MessageRenderList, chat_id: int = None,
                 pin: bool | int = False, bot: aiogram.Bot = None, **kwargs):
        AiogramResponseMixin.__init__(self, **kwargs)
        self.to_send = to_send
        self.chat_id = chat_id
        self.pin = pin
        self.bot = bot

    async def __call__(self, message):
        bot = self.bot or aiogram.Bot.get_current()
        chat_id = self.chat_id or message.chat.id

        async def send():
            messages = await self.to_send.send(chat_id, bot=bot)

            if self.pin is not False:
                pin_index = 0 if self.pin is True else self.pin
                msg = messages[pin_index]

                await bot.pin_chat_message(msg.chat.id, msg.message_id)

            return messages

        await self.capture(send())


class FeedbackResponse(Response, AiogramResponseMixin):
    def __init__(self, to_send: MessageRender, duration: float, chat_id: int = None,
                 bot: aiogram.Bot = None, **kwargs):
        AiogramResponseMixin.__init__(self, **kwargs)
        self.to_send = to_send
        self.duration = duration
        self.chat_id = chat_id
        self.bot = bot

    async def __call__(self, message):
        chat_id = self.chat_id or message.chat.id
        bot = self.bot or aiogram.Bot.get_current()

        async def send_feedback():
            msg = await self.to_send.send(chat_id)
            asyncio.create_task(delete_feedback(msg))

        async def delete_feedback(msg):
            await asyncio.sleep(self.duration)
            await DeleteMessageResponse(bot=bot).__call__(msg)

        await self.capture(send_feedback())


class NotifyResponse(Response, AiogramResponseMixin):
    def __init__(self, to_send: MessageRenderList, receivers: list[int], bot: aiogram.Bot = None,
                 on_finish=None, **kwargs):
        AiogramResponseMixin.__init__(self, **kwargs)
        self.to_send = to_send
        self.receivers = receivers
        self.bot = bot

        self.on_finish = Slot(on_finish)

    async def __call__(self, message):
        bot = self.bot or aiogram.Bot.get_current()

        results = []
        for index, chat_id in enumerate(self.receivers):
            is_successful = await self.capture(self.to_send.send(chat_id, bot=bot))
            results.append((index, chat_id, is_successful))
        await self.on_finish.emit(results)


__all__ = (
    'Response',
    'FunctionCallResponse',
    'AsyncCallResponse',
    'DeleteMessageResponse',
    'EditMessageResponse',
    'SendMessageResponse',
    'FeedbackResponse',
    'NotifyResponse'
)
