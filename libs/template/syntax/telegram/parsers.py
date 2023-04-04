from typing import Generator, Any

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton

from message_render import MessageRenderList, MessageRender
from .exceptions import TemplateTelegramError
from .types import *
from ...types import Parser


class DocumentParser(Parser):
    def __parse__(self) -> Generator[Any, Any, None]:
        messages = None

        while (token := (yield)) is not None:
            if messages is not None:
                raise TemplateTelegramError('Got another token')
            elif isinstance(token, MessageRenderList):
                messages = token
                continue
            elif isinstance(token, MessageRender):
                messages = MessageRenderList([token])
                continue
            raise TemplateTelegramError(f'Got unexpected token "{token}" (type: {token.__class__})')

        if messages is None:
            raise TemplateTelegramError('Got no tokens')

        yield messages


class MessagesParser(Parser):
    def __parse__(self) -> Generator[Any, Any, None]:
        messages = MessageRenderList()

        while (token := (yield)) is not None:
            if isinstance(token, MessageRender):
                messages.append(token)
                continue
            raise TemplateTelegramError(f'Got unexpected token "{token}" (type: {token.__class__})')

        yield messages


class MessageParser(Parser):
    def __parse__(self) -> Generator[Any, Any, None]:
        message = MessageRender("")
        layout = TextLayout()

        while (token := (yield)) is not None:
            if isinstance(token, ImageID):
                if message.photo is not None:
                    raise TemplateTelegramError('Message can only have one photo')
                if message.animation is not None:
                    raise TemplateTelegramError('Message can not have both photo and animation')
                message.photo = token
                continue
            if isinstance(token, AnimationID):
                if message.animation is not None:
                    raise TemplateTelegramError('Message can only have one animation')
                if message.photo is not None:
                    raise TemplateTelegramError('Message can not have both photo and animation')
                message.animation = token
                continue
            if isinstance(token, ImageFile):
                if message.photo is not None:
                    raise TemplateTelegramError('Message can only have one photo')
                if message.animation is not None:
                    raise TemplateTelegramError('Message can not have both photo and animation')
                message.photo = token.input_file
                continue
            if isinstance(token, AnimationFile):
                if message.animation is not None:
                    raise TemplateTelegramError('Message can only have one animation')
                if message.photo is not None:
                    raise TemplateTelegramError('Message can not have both photo and animation')
                message.animation = token.input_file
                continue
            if isinstance(token, BlockText):
                layout.add_paragraph(token)
                continue
            if isinstance(token, (InlineText, str)):
                layout.add(token)
                continue
            if isinstance(token, (InlineKeyboardMarkup, ReplyKeyboardMarkup)):
                if message.keyboard is not None:
                    raise TemplateTelegramError('Message can only have one keyboard')
                message.keyboard = token
                continue
            raise TemplateTelegramError(f'Got unexpected token "{token}" (type: {token.__class__})')

        message.text = layout.result()
        yield message


class TextParser(Parser):
    def __parse__(self) -> Generator[Any, Any, None]:
        layout = TextLayout()

        while (token := (yield)) is not None:
            if isinstance(token, BlockText):
                layout.add_paragraph(token)
                continue
            if isinstance(token, (InlineText, str)):
                layout.add(token)
                continue
            raise TemplateTelegramError(f'Got unexpected token "{token}" (type: {token.__class__})')

        yield layout.result()


class KeyboardMarkupParser(Parser):
    def __parse__(self) -> Generator[Any, Any, None]:
        layout = KeyboardLayout()

        while (token := (yield)) is not None:
            if isinstance(token, KeyboardLayoutRow):
                layout.add_row(token)
                continue
            if isinstance(token, (InlineKeyboardButton, KeyboardButton)):
                layout.add(token)
                continue
            raise TemplateTelegramError(f'Got unexpected token "{token}" (type: {token.__class__})')

        yield layout.result()


class KeyboardRowParser(Parser):
    def __parse__(self) -> Generator[Any, Any, None]:
        buttons = KeyboardLayoutRow()

        while (token := (yield)) is not None:
            if isinstance(token, (InlineKeyboardButton, KeyboardButton)):
                buttons.append(token)
                continue
            raise TemplateTelegramError(f'Got unexpected token "{token}" (type: {token.__class__})')

        yield buttons


TELEGRAM = DocumentParser()
MESSAGES = MessagesParser()
MESSAGE = MessageParser()
ELEMENT = TextParser()
NO_HTML = TextParser()
INLINE_KEYBOARD = KeyboardMarkupParser()
REPLY_KEYBOARD = KeyboardMarkupParser()
INLINE_KEYBOARD_ROW = KeyboardRowParser()
REPLY_KEYBOARD_ROW = KeyboardRowParser()


__all__ = (
    'TELEGRAM',
    'MESSAGES',
    'MESSAGE',
    'ELEMENT',
    'NO_HTML',
    'INLINE_KEYBOARD',
    'REPLY_KEYBOARD',
    'INLINE_KEYBOARD_ROW',
    'REPLY_KEYBOARD_ROW',
)
