from __future__ import annotations

import dataclasses
import typing

import aiogram

from message_render import MessageRenderList, MessageRender
from .response import *

__default_feedback_duration__: float = 2


@dataclasses.dataclass
class Feedback:
    message: MessageRender
    duration: float


@dataclasses.dataclass
class Notification:
    messages: MessageRenderList
    receivers: list[int]
    bot: aiogram.Bot = None


def _to_MessageRender(value: MessageRender | str) -> MessageRender:
    if isinstance(value, MessageRender):
        return value
    return MessageRender(value)


def _to_MessageRenderList(value: MessageRenderList | MessageRender | str) -> MessageRenderList:
    if isinstance(value, MessageRenderList):
        return value
    return MessageRenderList([
        _to_MessageRender(value)
    ])


# noinspection PyShadowingNames
def feedback(
        feedback: Feedback | MessageRender | str,
        /, *,
        duration: float = None,
        bot: aiogram.Bot = None,
        **kwargs
) -> list[Response]:
    """ Генерирует ответ, отправляющий feedback-сообщение """

    if isinstance(feedback, Feedback):
        return [FeedbackResponse(
            feedback.message,
            duration or feedback.duration,
            bot=bot,
            **kwargs
        )]
    return [FeedbackResponse(
        _to_MessageRender(feedback),
        duration or __default_feedback_duration__,
        bot=bot,
        **kwargs
    )]


def notify(
        notification: Notification | MessageRenderList | MessageRender | str,
        receivers: list[int] = None,
        /, *,
        bot: aiogram.Bot = None,
        **kwargs
) -> list[Response]:
    """ Генерирует ответ, отправляющий оповещение """

    if isinstance(notification, Notification):
        return [NotifyResponse(
            notification.messages,
            receivers or notification.receivers,
            bot=notification.bot or bot,
            **kwargs
        )]
    return [NotifyResponse(
        _to_MessageRenderList(notification),
        receivers,
        bot=bot,
        **kwargs
    )]


# Решение проблем с Name Shadowing
_feedback = feedback
_notify = notify


# noinspection PyShadowingNames
def edit(
        msg: aiogram.types.Message | None,
        render: MessageRender | str,
        /, *,
        feedback: Feedback | MessageRender | str = None,
        notify: Notification = None,
        bot: aiogram.Bot = None,
        **kwargs
) -> list[Response]:
    """ Генерирует ответ, редактирующий указанное сообщение.
        Работает только в callback_query handler-ах """

    responses = [EditMessageResponse(
        _to_MessageRender(render),
        message=msg,
        **kwargs
    )]

    if feedback:
        responses.extend(_feedback(feedback, bot=bot))

    if notify:
        responses.extend(_notify(notify, bot=bot))

    return responses


def edit_original(
        render: MessageRender | str,
        **kwargs
) -> list[Response]:
    """ Генерирует ответ, редактирующий исходное сообщение.
        Работает только в callback_query handler-ах """
    return edit(None, render, **kwargs)


# Решение проблем с Name Shadowing
_edit_original = edit_original


# noinspection PyShadowingNames
def delete(
        message_id: int | None,
        /, *,
        feedback: Feedback | MessageRender | str = None,
        notify: Notification = None,
        bot: aiogram.Bot = None,
        **kwargs
) -> list[Response]:
    """ Генерирует ответ, удаляющий указанное сообщение.
        Работает только в callback_query handler-ах """

    responses = [DeleteMessageResponse(
        message_id, **kwargs
    )]

    if feedback:
        responses.extend(_feedback(feedback, bot=bot))

    if notify:
        responses.extend(_notify(notify, bot=bot))

    return responses


def delete_original(
        **kwargs
) -> list[Response]:
    """ Генерирует ответ, удаляющий исходное сообщение.
        Работает только в callback_query handler-ах """
    return delete(None, **kwargs)


# Решение проблем с Name Shadowing
_delete_original = delete_original


# noinspection PyShadowingNames
def message(
        render: MessageRenderList | MessageRender | str,
        /, *,
        edit_original: MessageRender | str = None,
        delete_original: bool = False,
        feedback: Feedback | MessageRender | str = None,
        notify: Notification = None,
        pin: bool | int = False,
        bot: aiogram.Bot = None,
        **kwargs
) -> list[Response]:
    """ Генерирует ответ, отправляющий сообщение в чат.
        edit_original и delete_original будут
        работать только в callback_query handler-ах """

    responses = []

    if edit_original and delete_original:
        raise ValueError('Can not edit and delete message at the same time')

    elif edit_original:
        responses.extend(_edit_original(edit_original, bot=bot))

    elif delete_original:
        responses.extend(_delete_original(bot=bot))

    responses.append(SendMessageResponse(
        _to_MessageRenderList(render),
        pin=pin, bot=bot,
        **kwargs
    ))

    if feedback:
        responses.extend(_feedback(feedback, bot=bot))

    if notify:
        responses.extend(_notify(notify, bot=bot))

    return responses


def call(function: typing.Callable, /) -> list[Response]:
    """ Генерирует ответ, вызывающий функцию. Для случаев, когда
       писать отдельный Response не имеет смысла """

    return [FunctionCallResponse(function)]


def await_(awaitable: typing.Awaitable, /) -> list[Response]:
    """ Генерирует ответ, вызывающий асинхронную функцию. Для
       случаев, когда писать отдельный Response не имеет смысла """

    return [AsyncCallResponse(awaitable)]


def no_response() -> list[Response]:
    """ Возвращает пустой список. Используется для явного указания
       отсутствия ответа """

    return []


empty_response = no_response


__all__ = (
    'Feedback',
    'Notification',
    'message',
    'edit',
    'edit_original',
    'delete',
    'delete_original',
    'feedback',
    'notify',
    'call',
    'await_',
    'no_response',
    'empty_response'
)
