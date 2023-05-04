from __future__ import annotations

import typing

import aiogram
import aiogram.types
import aiogram.exceptions

import gls
import template
from template_for_aiogram import aiogram_syntax
from apps.botpiska.models import Employee
from response_system.core import globals_
from response_system.core.responses import TEditSuccessHandler, TBasicHandler, Response, TSendSuccessHandler, \
    TFeedbackSuccessHandler, TNotifyEverySuccessHandler, TNotifyBasicSuccessHandler, handle, \
    TNotifyCompletionHandler, action_edit, action_send, action_feedback


async def action_tmpl_notify(
        path: str, context: dict,
        receivers: typing.Sequence[int],
        bot: aiogram.Bot,
        include_chat_id: str,  # Добавляет чат отправки в контекст

        on_every_success: TNotifyEverySuccessHandler = None,
        on_every_forbidden: TNotifyBasicSuccessHandler = None,
        on_every_error: TNotifyBasicSuccessHandler = None,
        on_completion: TNotifyCompletionHandler = None
):
    if not include_chat_id:
        message = template.render(path, context)
    succeeded = 0

    for chat in receivers:
        if include_chat_id:
            message = template.render(path, {
                **{include_chat_id: chat},
                **context
            })

        # noinspection PyBroadException,DuplicatedCode
        try:
            # noinspection PyUnboundLocalVariable
            result = await message.send(chat, bot=bot)
            await handle(on_every_success, result)
            succeeded += 1
        except aiogram.exceptions.TelegramForbiddenError:
            await handle(on_every_forbidden, chat)
            await handle(on_every_error, chat)
        except Exception:
            await handle(on_every_error, chat)

    await on_completion(succeeded, len(receivers))


# ---


def tmpl_edit(
        path: str, context: dict,
        original: aiogram.types.Message = None,
        bot: aiogram.Bot = None,

        on_success: TEditSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None
) -> Response:
    response = Response()
    response.add_action(
        action_edit(
            template.render(path, context, syntax=aiogram_syntax).extract(),
            original or globals_.message_var.get(),
            bot or aiogram.Bot.get_current(),
            on_success=on_success,
            on_forbidden=on_forbidden,
            on_error=on_error
        ),
        priority=0
    )
    return response


def tmpl_send(
        path: str, context: dict,
        chat: int = None,
        bot: aiogram.Bot = None,

        on_success: TSendSuccessHandler = None,
        on_forbidden: TBasicHandler = None,
        on_error: TBasicHandler = None
) -> Response:
    response = Response()
    response.add_action(
        action_send(
            template.render(path, context, syntax=aiogram_syntax),
            chat or globals_.message_var.get().chat.id,
            bot or aiogram.Bot.get_current(),
            on_success=on_success,
            on_forbidden=on_forbidden,
            on_error=on_error
        ),
        priority=2
    )
    return response


def tmpl_feedback(
        path: str, context: dict,
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
            template.render(path, context, syntax=aiogram_syntax).extract(),
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


def tmpl_notify(
        path: str, context: dict,
        receivers: typing.Sequence[int],
        bot: aiogram.Bot = None,
        include_chat_id: str = None,  # Добавляет чат отправки в контекст

        on_every_success: TNotifyEverySuccessHandler = None,
        on_every_forbidden: TNotifyBasicSuccessHandler = None,
        on_every_error: TNotifyBasicSuccessHandler = None,
        on_completion: TNotifyCompletionHandler = None
) -> Response:
    response = Response()
    response.add_action(
        action_tmpl_notify(
            path, context,
            receivers,
            bot or aiogram.Bot.get_current(),
            include_chat_id,
            on_every_success=on_every_success,
            on_every_forbidden=on_every_forbidden,
            on_every_error=on_every_error,
            on_completion=on_completion
        ),
        priority=4
    )
    return response


def tmpl_notify_employee(
        path: str, context: dict,
        include_chat_id: str = None,  # Добавляет чат отправки в контекст

        on_every_success: TNotifyEverySuccessHandler = None,
        on_every_forbidden: TNotifyBasicSuccessHandler = None,
        on_every_error: TNotifyBasicSuccessHandler = None,
        on_completion: TNotifyCompletionHandler = None
) -> Response:
    response = Response()
    response.add_action(
        action_tmpl_notify(
            path, context,
            Employee.get_all_chats(),
            gls.operator_bot,
            include_chat_id,
            on_every_success=on_every_success,
            on_every_forbidden=on_every_forbidden,
            on_every_error=on_every_error,
            on_completion=on_completion
        ),
        priority=4
    )
    return response
