from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from typing import Any

import aiogram
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

Context = dict[str, Any]


@dataclass
class MessageRender:
    text: str
    photo: str | None = None
    keyboard: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None

    def export_for_aiogram(self, force_photo_mode: bool = False, force_text_mode: bool = False) -> dict:
        if force_photo_mode and force_text_mode:
            raise ValueError('Only one mode can be forced at a time')

        result = {}

        if self.photo or force_photo_mode:
            result['photo'] = self.photo
            result['caption'] = self.text

        elif not self.photo or force_text_mode:
            result['text'] = self.text

        if self.keyboard:
            result['reply_markup'] = self.keyboard

        return result

    async def send(self, chat_id: int, bot: aiogram.Bot = None, force_caption: bool = False):
        bot = bot or aiogram.Bot.get_current()
        if self.photo or force_caption:
            return await bot.send_photo(chat_id, **self.export_for_aiogram())
        return await bot.send_message(chat_id, **self.export_for_aiogram())

    async def edit(self, chat_id: int, message_id: int, bot: aiogram.Bot = None, force_caption: bool = False):
        bot = bot or aiogram.Bot.get_current()
        with suppress(TelegramBadRequest):
            exported = self.export_for_aiogram(force_photo_mode=force_caption)
            if 'photo' in exported:
                exported.pop('photo')
                await bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    **exported
                )
                return
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                **exported
            )


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
