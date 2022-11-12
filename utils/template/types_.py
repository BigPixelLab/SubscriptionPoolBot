from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import aiogram
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, Message

Context = dict[str, Any]
logger = logging.getLogger(__name__)


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
        if self.photo:
            return await bot.send_photo(chat_id, **self.export_for_aiogram())
        if self.video:
            return await bot.send_animation(chat_id, **self.export_for_aiogram())
        return await bot.send_message(chat_id, **self.export_for_aiogram())

    async def send(self, chat_id: int, bot: aiogram.Bot = None, silence_errors: bool = True):
        try:
            return await self._send(chat_id, bot)
        except (TelegramBadRequest, TelegramForbiddenError) as error:
            if not silence_errors:
                raise error
            logger.error(repr(error))

    async def _edit(self, message: Message, bot: aiogram.Bot = None):
        bot = bot or aiogram.Bot.get_current()
        is_caption = bool(message.photo) or bool(message.animation)

        config = self.export_for_aiogram(
            force_caption=is_caption,
            no_media=True
        )

        if is_caption:
            return await bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=message.message_id,
                **config
            )

        return await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            **config
        )

    async def edit(self, message: Message, bot: aiogram.Bot = None, silence_errors: bool = True):
        try:
            return await self._edit(message, bot)
        except (TelegramBadRequest, TelegramForbiddenError) as error:
            if not silence_errors:
                raise error
            logger.error(repr(error))


class MessageRenderList(list[MessageRender]):
    def __init__(self, *args, **kwargs):
        super(MessageRenderList, self).__init__(*args, **kwargs)

    async def send(self, chat_id: int, bot: aiogram.Bot = None):
        sent_messages = []
        for message in self:
            sent_messages.append(await message.send(chat_id, bot=bot))
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
