from __future__ import annotations

import asyncio
import typing

import aiogram
import aiogram.types

import gls
import template
from apps.botpiska.models import Employee
from response_system.core import globals_
from response_system.core.responses import TEditSuccessHandler, TBasicHandler, Response, capture, TSendSuccessHandler, \
    TFeedbackSuccessHandler, FEEDBACK_VISIBILITY_TIME, TNotifyEverySuccessHandler, TNotifyBasicSuccessHandler


def tmpl_edit(
        path: str, context: dict,
        original: aiogram.types.Message = None,
        on_success: TEditSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None,
        bot: aiogram.Bot = None
) -> Response:
    async def action():
        _bot = bot or aiogram.Bot.get_current()

        _message = template.render(path, context).extract()
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


def tmpl_send(
        path: str, context: dict,
        on_success: TSendSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None,
        chat: int = None,
        bot: aiogram.Bot = None
) -> Response:
    async def action():
        _bot = bot or aiogram.Bot.get_current()

        _chat = chat or globals_.message_var.get().chat.id
        _message = template.render(path, context)

        await capture(
            _message.send(_chat, bot=_bot),
            on_success,
            on_forbidden,
            on_error
        )

    response = Response()
    response.add_action(action(), priority=2)
    return response


def tmpl_feedback(
        path: str, context: dict,
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
        _message = template.render(path, context).extract()

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


def tmpl_notify(
        path: str, context: dict,
        receivers: typing.Iterable[int],
        include_chat_id: str = None,  # Добавляет чат отправки в контекст
        on_every_success: TNotifyEverySuccessHandler = None,
        on_every_forbidden: TNotifyBasicSuccessHandler = None,
        on_every_error: TNotifyBasicSuccessHandler = None,
        bot: aiogram.Bot = None
) -> Response:
    async def action():
        _bot = bot or aiogram.Bot.get_current()

        if not include_chat_id:
            _message = template.render(path, context)

        for chat in receivers:
            if include_chat_id:
                _message = template.render(path, {
                    **{include_chat_id: chat},
                    **context
                })

            # noinspection PyUnboundLocalVariable
            await capture(
                _message.send(chat, bot=_bot),
                lambda x: on_every_success(chat, x),
                lambda: on_every_forbidden(chat),
                lambda: on_every_error(chat)
            )

    response = Response()
    response.add_action(action(), priority=4)
    return response


def tmpl_notify_employee(
        path: str, context: dict,
        include_chat_id: str = None,  # Добавляет чат отправки в контекст
        on_every_success: TNotifyEverySuccessHandler = None,
        on_every_forbidden: TNotifyBasicSuccessHandler = None,
        on_every_error: TNotifyBasicSuccessHandler = None
) -> Response:
    receivers = Employee.get_all_chats()
    return tmpl_notify(
        path, context, receivers,
        include_chat_id=include_chat_id,
        on_every_success=on_every_success,
        on_every_forbidden=on_every_forbidden,
        on_every_error=on_every_error,
        bot=gls.operator_bot
    )
