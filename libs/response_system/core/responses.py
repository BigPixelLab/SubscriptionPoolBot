from __future__ import annotations

import asyncio
import typing

import aiogram
import aiogram.exceptions
from sortedcontainers import SortedList

from message_render import MessageRender, MessageRenderList
from . import globals_

TBasicHandler = typing.Callable[[], typing.Awaitable]
TEditSuccessHandler = typing.Callable[[typing.Union[aiogram.types.Message, bool]], typing.Awaitable]
TDeleteSuccessHandler = typing.Callable[[bool], typing.Awaitable]
TSendSuccessHandler = typing.Callable[[list[typing.Optional[aiogram.types.Message]]], typing.Awaitable]
TFeedbackSuccessHandler = typing.Callable[[aiogram.types.Message], typing.Awaitable]
TNotifyBasicSuccessHandler = typing.Callable[[int], typing.Awaitable]
TNotifyEverySuccessHandler = typing.Callable[[int, int], typing.Awaitable]

FEEDBACK_VISIBILITY_TIME = 2


class Response:
    class ResponseActionItem(typing.NamedTuple):
        action: typing.Awaitable
        priority: int

    def __init__(self):
        self.actions: SortedList = SortedList(key=lambda x: x.priority)

    def __iter__(self):
        return (i.action for i in self.actions)

    def __add__(self, other: 'Response'):
        if other is None:
            return self
        if not isinstance(other, Response):
            raise NotImplemented
        self.actions.update(other.actions)
        return self

    __iadd__ = __add__

    def add_action(self, action: typing.Awaitable, priority: int):
        self.actions.add(self.ResponseActionItem(action, priority))


def to_MessageRender(value: typing.Union[MessageRender, str]) -> MessageRender:
    if isinstance(value, MessageRender):
        return value
    return MessageRender(value)


def to_MessageRenderList(value: typing.Union[MessageRenderList, MessageRender, str]) -> MessageRenderList:
    if isinstance(value, MessageRenderList):
        return value
    return MessageRenderList([
        to_MessageRender(value)
    ])


async def capture(
        function: typing.Awaitable,
        on_success: typing.Callable[[...], typing.Awaitable] = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None
):
    # noinspection PyBroadException
    try:
        result = await function
        if on_success:
            await on_success(result)

    except aiogram.exceptions.TelegramForbiddenError:
        if not on_forbidden and not on_error:
            raise

        if on_forbidden:
            await on_forbidden()
        if on_error:
            await on_error()

    except Exception:
        if not on_error:
            raise
        await on_error()


# @response_action(priority=0)
def edit(
        message: typing.Union[MessageRender, str],
        original: aiogram.types.Message = None,
        on_success: TEditSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None,
        bot: aiogram.Bot = None
) -> Response:
    async def action():
        _bot = bot or aiogram.Bot.get_current()

        _message = to_MessageRender(message)
        _original = original or globals_.message_var.get()

        await capture(
            _message.edit(_original, bot=_bot),
            on_success,
            on_forbidden,
            on_error
        )

    response = Response()
    response.add_action(action(), priority=0)
    return response


def delete(
        original: typing.Union[aiogram.types.Message, int] = None,
        chat: int = None,
        on_success: TDeleteSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None,
        bot: aiogram.Bot = None
) -> Response:
    async def action():
        _bot = bot or aiogram.Bot.get_current()

        if chat and not original:
            raise ValueError('Chat cannot be set without original message id')

        _chat = chat or globals_.message_var.get().chat.id
        _original = original or globals_.message_var.get().message_id

        await capture(
            _bot.delete_message(_chat, _original),
            on_success,
            on_forbidden,
            on_error
        )

    response = Response()
    response.add_action(action(), priority=1)
    return response


def send(
        message: typing.Union[MessageRenderList, MessageRender, str],
        chat: int = None,
        on_success: TSendSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None,
        bot: aiogram.Bot = None
) -> Response:
    async def action():
        _bot = bot or aiogram.Bot.get_current()

        _chat = chat or globals_.message_var.get().chat.id
        _message = to_MessageRenderList(message)

        await capture(
            _message.send(_chat, bot=_bot),
            on_success,
            on_forbidden,
            on_error
        )

    response = Response()
    response.add_action(action(), priority=2)
    return response


def feedback(
        message: typing.Union[MessageRender, str],
        on_success: TFeedbackSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None,
        on_delete: TBasicHandler = None,
        chat: int = None,
        bot: aiogram.Bot = None
) -> Response:
    async def _delete_feedback(sent: aiogram.types.Message):
        await asyncio.sleep(FEEDBACK_VISIBILITY_TIME)
        await capture(sent.delete(), on_success=on_delete)

    async def action():
        _bot = bot or aiogram.Bot.get_current()

        _chat = chat or globals_.message_var.get().chat.id
        _message = to_MessageRender(message)

        await capture(
            _message.send(_chat, bot=_bot),
            lambda x: asyncio.gather(
                asyncio.create_task(_delete_feedback(x)),
                on_success(x)
            ),
            on_forbidden,
            on_error
        )

    response = Response()
    response.add_action(action(), priority=3)
    return response


def notify(
        message: typing.Union[MessageRenderList, MessageRender, str],
        receivers: typing.Iterable[int],
        on_every_success: TNotifyEverySuccessHandler = None,
        on_every_forbidden: TNotifyBasicSuccessHandler = None,
        on_every_error: TNotifyBasicSuccessHandler = None,
        bot: aiogram.Bot = None
) -> Response:
    async def action():
        _bot = bot or aiogram.Bot.get_current()

        _message = to_MessageRenderList(message)

        for chat in receivers:
            await capture(
                _message.send(chat, bot=_bot),
                lambda x: on_every_success(chat, x),
                lambda: on_every_forbidden(chat),
                lambda: on_every_error(chat)
            )

    response = Response()
    response.add_action(action(), priority=4)
    return response


def do(function: typing.Awaitable) -> Response:
    response = Response()
    response.add_action(function, priority=5)
    return response


def no_response() -> Response:
    return Response()


def respond(response: Response):
    """ Преждевременно выполняет Response-ы """
    globals_.response_var.set(
        globals_.response_var.get()
        + response
    )
