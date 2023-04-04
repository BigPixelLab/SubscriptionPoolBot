import re
from typing import Union

from aiogram.types import InputFile, InlineKeyboardMarkup, WebAppInfo, LoginUrl, CallbackGame, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButtonPollType, KeyboardButton

from message_render import MessageRenderList, MessageRender
from .converters import str2list
from .exceptions import TemplateTelegramError
from .parsers import *
from .types import *
from ...exceptions import ParsingError
from ...types import register, Tag, ConvertBy, TokenSet, SendNothing, ReadOnlyDict


@register([TELEGRAM])
def messages(tag: Tag) -> MessageRenderList:
    """ Список сообщений """
    return MESSAGES.parse(tag.element, tag.context)


@register([TELEGRAM, MESSAGES])
def message(tag: Tag, *, requires: ConvertBy[str2list] = None) -> MessageRender:
    """ Сообщение """
    requires = requires or []
    if expected := set(requires) - set(tag.context.keys()):
        raise TemplateTelegramError(f'Template requires additional {expected} context variables')
    return MESSAGE.parse(tag.element, tag.context)


@register([MESSAGE, ELEMENT])
def template(tag: Tag, *, src: str, __rem: dict) -> TokenSet:
    """ Встраивает набор элементов из шаблона """

    from xml.dom import minidom
    document = minidom.parse(src)
    tmpl: minidom.Element = document.childNodes[0]

    # Enforcing correct syntax

    if tmpl.tagName != 'template':
        raise ParsingError(f'Expected template file at "{src}"')

    if unexpected := set(tmpl.attributes.keys()) - {'requires'}:
        raise ParsingError(f'{tag.element.tagName}: Got unexpected arguments {unexpected}')

    # Checking if there is any mismatch in required and provided arguments

    try:
        required = set(str2list(tmpl.attributes['requires'].value))
    except KeyError:
        required = set()
    provided = set(__rem)

    if unprovided := required - provided:
        raise ParsingError(f'{tag.element.tagName}: Arguments {unprovided} were expected, but not provided')
    if unexpected := provided - required:
        raise ParsingError(f'{tag.element.tagName}: Got unexpected arguments {unexpected}')

    # Processing template elements

    for element in tmpl.childNodes:
        tag.process(element, ReadOnlyDict(__rem))
    return SendNothing


SPACING_PATTERN = re.compile(r'\s+')


@MESSAGE.register_text
@ELEMENT.register_text
@NO_HTML.register_text
def _text_(tag: Tag) -> BlockText:
    """ Не обрамлённый в теги текст """
    words = re.split(SPACING_PATTERN, tag.element.nodeValue)
    result = ' '.join(words).strip().format_map(tag.context)
    return InlineText(result)


@register([MESSAGE, ELEMENT])
def heading(tag: Tag) -> BlockText:
    """ Заголовок """
    return BlockText(f'<b>{NO_HTML.parse(tag.element, tag.context).upper()}</b>')


@register([MESSAGE, ELEMENT])
def p(tag: Tag) -> BlockText:
    """ Параграф """
    return BlockText(ELEMENT.parse(tag.element, tag.context))


@register([MESSAGE, ELEMENT])
def br(_) -> BlockText:
    """ Пустая строка """
    return BlockText()


@register([MESSAGE, ELEMENT])
def span(tag: Tag) -> InlineText:
    """ Часть текста """
    return InlineText(ELEMENT.parse(tag.element, tag.context))


@register([NO_HTML], name='span')
def span_no_html(tag: Tag) -> InlineText:
    """ Часть текста """
    return InlineText(NO_HTML.parse(tag.element, tag.context))


@register([MESSAGE, ELEMENT])
def a(tag: Tag, *, href: str) -> InlineText:
    """ Ссылка """
    return InlineText(f'<a href="{href}">{NO_HTML.parse(tag.element, tag.context)}</a>')


def _simple_tag_handler(t: str):
    @register([MESSAGE, ELEMENT], name=t)
    def _tag(tag: Tag) -> InlineText:
        return InlineText(f'<{t}>{ELEMENT.parse(tag.element, tag.context)}</{t}>')
    return _tag


b = _simple_tag_handler('b')
i = _simple_tag_handler('i')
u = _simple_tag_handler('u')
code = _simple_tag_handler('code')


@register([MESSAGE])
def img(_, *, src: str) -> Union[ImageID, ImageFile]:
    """ Добавляет изображение в сообщение """
    # InputFile can be provided via context vars
    if isinstance(src, InputFile):
        return ImageFile(src)
    if isinstance(src, str):
        return ImageID(src)
    raise TemplateTelegramError(f'img.src expected "str" or "InputFile", got "{type(src)}"')


@register([MESSAGE])
def anim(_, *, src: str) -> Union[AnimationID, AnimationFile]:
    """ Добавляет анимацию в сообщение """
    # InputFile can be provided via context vars
    if isinstance(src, InputFile):
        return AnimationFile(src)
    if isinstance(src, str):
        return AnimationID(src)
    raise TemplateTelegramError(f'anim.src expected "str" or "InputFile", got "{type(src)}"')


@register([MESSAGE], name='inline-keyboard')
def inline_keyboard(tag: Tag) -> InlineKeyboardMarkup:
    """ Добавляет inline-клавиатуру к сообщению """
    layout = INLINE_KEYBOARD.parse(tag.element, tag.context)
    return InlineKeyboardMarkup(inline_keyboard=layout)


@register([INLINE_KEYBOARD], name='row')
def row_inline_keyboard(tag: Tag) -> KeyboardLayoutRow:
    """ Добавляет строку к inline-клавиатуре """
    return INLINE_KEYBOARD_ROW.parse(tag.element, tag.context)


@register([INLINE_KEYBOARD, INLINE_KEYBOARD_ROW], name='button')
def button_inline_keyboard(tag: Tag, *, text: str = None, url: str = None, callback_data: str = None,
                           web_app: WebAppInfo = None, login_url: LoginUrl = None,
                           switch_inline_query: str = None, switch_inline_query_current_chat: str = None,
                           callback_game: CallbackGame = None, pay: bool = False) \
        -> InlineKeyboardButton:
    """ Добавляет кнопку к inline-клавиатуре """

    if text is None:
        text = NO_HTML.parse(tag.element, tag.context)

    return InlineKeyboardButton(
        text=text, url=url, callback_data=callback_data, web_app=web_app, login_url=login_url,
        switch_inline_query=switch_inline_query, switch_inline_query_current_chat=switch_inline_query_current_chat,
        callback_game=callback_game, pay=pay
    )


@register([MESSAGE], name='reply-keyboard')
def reply_keyboard(tag: Tag, *, resize_keyboard: bool = None, one_time_keyboard: bool = None,
                   input_field_placeholder: str = None, selective: bool = None) -> ReplyKeyboardMarkup:
    """ Добавляет reply-клавиатуру к сообщению """

    layout = REPLY_KEYBOARD.parse(tag.element, tag.context)
    return ReplyKeyboardMarkup(
        keyboard=layout, resize_keyboard=resize_keyboard, one_time_keyboard=one_time_keyboard,
        input_field_placeholder=input_field_placeholder, selective=selective
    )


@register([REPLY_KEYBOARD], name='row')
def row_reply_keyboard(tag: Tag) -> KeyboardLayoutRow:
    """ Добавляет строку к reply-клавиатуре """
    return REPLY_KEYBOARD_ROW.parse(tag.element, tag.context)


@register([REPLY_KEYBOARD, REPLY_KEYBOARD_ROW], name='button')
def button_reply_keyboard(tag: Tag, *, text: str = None, request_contact: bool = None, request_location: bool = None,
                          request_poll: KeyboardButtonPollType = None, web_app: WebAppInfo = None) -> KeyboardButton:
    """ Добавляет кнопку к reply-клавиатуре """

    if text is None:
        text = NO_HTML.parse(tag.element, tag.context)

    return KeyboardButton(
        text=text, request_contact=request_contact, request_location=request_location, request_poll=request_poll,
        web_app=web_app
    )
