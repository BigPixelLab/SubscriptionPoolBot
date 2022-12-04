from __future__ import annotations

import logging
import typing
from contextlib import suppress
from dataclasses import dataclass
from typing import Any

import aiogram
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, Message, \
    InputMediaPhoto, InputMediaAnimation

Context = dict[str, Any]
logger = logging.getLogger(__name__)


async def silence_telegram(function: typing.Awaitable, silence: bool = True):
    if not silence:
        return await function
    with suppress(TelegramBadRequest, TelegramForbiddenError, ValueError):
        return await function


@dataclass
class MessageRender:
    text: str
    photo: str | None = None
    video: str | None = None
    keyboard: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None

    def export_for_aiogram(self, force_caption: bool = False, no_media: bool = False) -> dict:
        result = {}

        if self.photo and self.video:
            raise ValueError('Cant export render containing image and video at the same time')

        if self.photo or self.video or force_caption:
            result['caption'] = self.text
        else:
            result['text'] = self.text

        if self.photo and not no_media:
            result['photo'] = self.photo

        if self.video and not no_media:
            result['animation'] = self.video

        if self.keyboard:
            result['reply_markup'] = self.keyboard

        return result

    async def _send(self, chat_id: int, bot: aiogram.Bot = None):
        bot = bot or aiogram.Bot.get_current()

        config = {}

        if self.keyboard:
            config['reply_markup'] = self.keyboard

        if self.photo:
            return await bot.send_photo(
                chat_id,
                photo=self.photo,
                caption=self.text,
                **config
            )

        if self.video:
            return await bot.send_animation(
                chat_id,
                animation=self.video,
                caption=self.text,
                **config
            )

        return await bot.send_message(
            chat_id,
            text=self.text,
            **config
        )

    async def send(self, chat_id: int, bot: aiogram.Bot = None, silence_errors: bool = True):
        return await silence_telegram(self._send(chat_id, bot), silence_errors)

    async def _edit(self, message: Message, bot: aiogram.Bot = None):
        bot = bot or aiogram.Bot.get_current()

        config = {}

        if self.keyboard:
            config['reply_markup'] = self.keyboard

        if not message.photo and not message.animation:
            return await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=self.text,
                **config
            )

        media = None
        if self.photo and message.photo:
            media = InputMediaPhoto(
                media=self.photo,
                caption=self.text
            )
        elif self.video and message.animation:
            media = InputMediaAnimation(
                media=self.video,
                caption=self.text
            )
        elif self.photo or self.video:
            raise ValueError('Render must have the same media type as a message')

        if media:
            return await bot.edit_message_media(
                chat_id=message.chat.id,
                message_id=message.message_id,
                media=media,
                **config
            )

        return await bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message.message_id,
            caption=self.text,
            **config
        )

    async def edit(self, message: Message, bot: aiogram.Bot = None, silence_errors: bool = True):
        return await silence_telegram(self._edit(message, bot), silence_errors)


class MessageRenderList(list[MessageRender]):
    def __init__(self, *args, **kwargs):
        super(MessageRenderList, self).__init__(*args, **kwargs)

    async def send(self, chat_id: int, bot: aiogram.Bot = None, silence_errors: bool = True):
        sent_messages = []
        for message in self:
            sent_messages.append(await message.send(chat_id, bot=bot, silence_errors=silence_errors))
        return sent_messages

    def first(self) -> MessageRender | None:
        if self:
            return self[0]
        return None


class PhotoUri(str):
    pass


class VideoUri(str):
    pass


class InlineText(str):
    pass


class BlockText(str):
    pass


class InlineKeyboardRow(list[InlineKeyboardButton]):
    pass


class ReplyKeyboardRow(list[KeyboardButton]):
    pass


class TextLayout:
    def __init__(self):
        self._layout = []

    def append_inline(self, text: str):
        """Добавляет текст в последнюю строку layout-а"""
        if not self._layout or isinstance(self._layout[-1], str):
            self._layout.append([])
        self._layout[-1].append(text)

    def append_block(self, text: str):
        """Добавляет в layout обособленный блок текста"""
        self._close_inline()
        self._layout.append(text)

    def finish(self) -> str:
        """Возвращает отрендеренный текст"""
        self._close_inline()
        return '\n'.join(self._layout)

    def _close_inline(self):
        """Если последний блок в layout-е - список, объединяем все его элементы пробелами"""
        if not self._layout or isinstance(self._layout[-1], str):
            return
        block = self._layout.pop()
        self._layout.append(' '.join(block))


class Scope:
    def __init__(self):
        self._registered = {}

    def get(self, tag: str):
        """Returns functions in format like (function, type)"""
        return self._registered.get(tag)

    @classmethod
    def register(cls, tag: str, *scopes: Scope):
        def _decorator(function):
            for scope in scopes:
                scope._registered[tag] = function
            return function
        return _decorator
