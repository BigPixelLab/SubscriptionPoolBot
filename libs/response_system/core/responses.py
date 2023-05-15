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
TNotifyCompletionHandler = typing.Callable[[int, int], typing.Awaitable]

FEEDBACK_VISIBILITY_TIME = 2
__debugging__ = False


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


async def handle(handler: typing.Optional[typing.Callable[[...], typing.Awaitable]], *args):
    if handler is None:
        return
    await handler(*args)


async def action_edit(
        message: MessageRender,
        original: aiogram.types.Message,
        bot: aiogram.Bot,

        on_success: TEditSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None
):
    # noinspection PyBroadException
    try:
        result = await message.edit(original, bot=bot)
        await handle(on_success, result)

    except Exception as error:
        do_raise = __debugging__ and on_error is None

        if isinstance(error, aiogram.exceptions.TelegramForbiddenError):
            do_raise = __debugging__ and on_forbidden is None
            await handle(on_forbidden)

        await handle(on_error)

        if do_raise:
            raise


async def action_delete(
        original: int,
        chat: int,
        bot: aiogram.Bot,

        on_success: TDeleteSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None,

        delay: float = 0
):
    if delay:
        await asyncio.sleep(delay)

    # noinspection PyBroadException
    try:
        result = await bot.delete_message(chat, original)
        await handle(on_success, result)

    except Exception as error:
        do_raise = __debugging__ and on_error is None

        if isinstance(error, aiogram.exceptions.TelegramForbiddenError):
            do_raise = __debugging__ and on_forbidden is None
            await handle(on_forbidden)

        await handle(on_error)

        if do_raise:
            raise


async def action_send(
        message: MessageRenderList,
        chat: int,
        bot: aiogram.Bot,

        on_success: TSendSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None
):
    # noinspection PyBroadException
    try:
        result = await message.send(chat, bot=bot)
        await handle(on_success, result)

    except Exception as error:
        do_raise = __debugging__ and on_error is None

        if isinstance(error, aiogram.exceptions.TelegramForbiddenError):
            do_raise = __debugging__ and on_forbidden is None
            await handle(on_forbidden)

        await handle(on_error)

        if do_raise:
            raise


async def action_feedback(
        message: MessageRender,
        chat: int,
        bot: aiogram.Bot,

        on_success: TFeedbackSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None,
        on_delete: TBasicHandler = None
):
    # noinspection PyBroadException
    try:
        fb, = message.send(chat, bot=bot)
        asyncio.create_task(
            action_delete(
                fb.message_id,
                fb.chat.id, bot,
                on_success=on_delete,
                delay=FEEDBACK_VISIBILITY_TIME
            )
        )
        await handle(on_success, fb)

    except Exception as error:
        do_raise = __debugging__ and on_error is None

        if isinstance(error, aiogram.exceptions.TelegramForbiddenError):
            do_raise = __debugging__ and on_forbidden is None
            await handle(on_forbidden)

        await handle(on_error)

        if do_raise:
            raise


async def action_notify(
        message: MessageRenderList,
        receivers: typing.Sequence[int],
        bot: aiogram.Bot,

        on_every_success: TNotifyEverySuccessHandler = None,
        on_every_forbidden: TNotifyBasicSuccessHandler = None,
        on_every_error: TNotifyBasicSuccessHandler = None,
        on_completion: TNotifyCompletionHandler = None
):
    succeeded = 0
    # noinspection DuplicatedCode
    for chat in receivers:
        # noinspection PyBroadException
        try:
            result = await message.send(chat, bot=bot)
            await handle(on_every_success, result)
            succeeded += 1

        except Exception as error:
            do_raise = __debugging__ and on_every_error is None

            if isinstance(error, aiogram.exceptions.TelegramForbiddenError):
                do_raise = __debugging__ and on_every_forbidden is None
                await handle(on_every_forbidden, chat)

            await handle(on_every_error, chat)

            if do_raise:
                raise

    await on_completion(succeeded, len(receivers))


# ---


def edit(
        message: typing.Union[MessageRender, str],
        original: aiogram.types.Message = None,
        bot: aiogram.Bot = None,

        on_success: TEditSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None
) -> Response:
    response = Response()
    response.add_action(
        action_edit(
            to_MessageRender(message),
            original or globals_.message_var.get(),
            bot or aiogram.Bot.get_current(),
            on_success=on_success,
            on_forbidden=on_forbidden,
            on_error=on_error
        ),
        priority=0
    )
    return response


def delete(
        original: typing.Union[aiogram.types.Message, int] = None,
        chat: int = None,
        bot: aiogram.Bot = None,

        on_success: TDeleteSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None
) -> Response:
    if chat and not isinstance(original, int):
        raise ValueError('Chat can be set only when original passed id')

    if chat is None and isinstance(original, int):
        raise ValueError('Chat must be specified when original passed by id')

    if isinstance(original, aiogram.types.Message):
        original, chat = original.message_id, original.chat.id

    response = Response()
    response.add_action(
        action_delete(
            original,
            chat,
            bot or aiogram.Bot.get_current(),
            on_success=on_success,
            on_forbidden=on_forbidden,
            on_error=on_error
        ),
        priority=0
    )
    return response


def send(
        message: typing.Union[MessageRenderList, MessageRender, str],
        chat: int = None,
        bot: aiogram.Bot = None,

        on_success: TSendSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None
) -> Response:
    response = Response()
    response.add_action(
        action_send(
            to_MessageRenderList(message),
            chat or globals_.message_var.get().chat.id,
            bot or aiogram.Bot.get_current(),
            on_success=on_success,
            on_forbidden=on_forbidden,
            on_error=on_error
        ),
        priority=2
    )
    return response


def feedback(
        message: typing.Union[MessageRender, str],
        chat: int = None,
        bot: aiogram.Bot = None,
        on_success: TFeedbackSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None,
        on_delete: TBasicHandler = None
) -> Response:
    response = Response()
    response.add_action(
        action_feedback(
            to_MessageRender(message),
            chat or globals_.message_var.get().chat.id,
            bot or aiogram.Bot.get_current(),
            on_success=on_success,
            on_forbidden=on_forbidden,
            on_error=on_error,
            on_delete=on_delete
        ),
        priority=3
    )
    return response


def notify(
        message: typing.Union[MessageRenderList, MessageRender, str],
        receivers: typing.Sequence[int],
        bot: aiogram.Bot = None,

        on_every_success: TNotifyEverySuccessHandler = None,
        on_every_forbidden: TNotifyBasicSuccessHandler = None,
        on_every_error: TNotifyBasicSuccessHandler = None,
        on_completion: TNotifyCompletionHandler = None
) -> Response:
    response = Response()
    response.add_action(
        action_notify(
            to_MessageRenderList(message),
            receivers,
            bot or aiogram.Bot.get_current(),
            on_every_success=on_every_success,
            on_every_forbidden=on_every_forbidden,
            on_every_error=on_every_error,
            on_completion=on_completion
        ),
        priority=4
    )
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
