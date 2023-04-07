""" Регистрация дополнительных тегов и настройки шаблонизатора """
from __future__ import annotations

import typing

import aiogram.types

import progressbar
import resources
import settings
from template.dev import *
from template_for_aiogram.types import *
from template_for_aiogram.scopes import *
from template import set_global_context

if typing.TYPE_CHECKING:
    from apps.botpiska.models import Subscription

# TEMPLATE GLOBALS --------------------------------------------------

set_global_context({
    'support': settings.SUPPORT_CHAT_ID,
    'tech_support': settings.TECH_SUPPORT_CHAT_ID,
    'telegram': aiogram.types
})


# SPECIFIERS --------------------------------------------------------

def res_extract_func(value, context, _) -> aiogram.types.InputFile | str:
    """ Воспринимает переданное значение в качестве индекса файла.
        Производит поиск cache->database->filesystem """
    return resources.resource(value.format_map(context))


specifiers.update(rs=res_extract_func)


# TAGS --------------------------------------------------------------
# Parser.register_to_many([MESSAGE, ELEMENT], arguments={'user': (int, None), 'display': (str, 'Пользователь')})

@register([MESSAGE, ELEMENT], name='progressbar')
def _progressbar(_, *, steps: int, of: int, width: int = None) -> str:
    """ Progressbar """
    return progressbar.progressbar(steps / of, width)


@register([MESSAGE, ELEMENT])
def chat(_, *, user: int = None, display: str = 'Пользователь') -> Text:
    """ Ссылка на чат с пользователем, оформленная как его имя """

    if user is not None:
        return f'<a href="tg://user?id={user}">{display}</a>'
    return display


@register([MESSAGE, ELEMENT], name='chat-current')
def chat_current(_) -> Text:
    """ Ссылка на чат с текущим пользователем, оформленная как его имя """

    if user := typing.cast(typing.Optional[aiogram.types.User], aiogram.types.User.get_current()):
        return chat(_, user=user.id, display=user.first_name)
    return chat(_)


@register([INLINE_KEYBOARD, INLINE_KEYBOARD_ROW], name='buy-button')
def buy_button(_, *, subscription: 'Subscription', discount: int = None) -> aiogram.types.InlineKeyboardButton:
    """ Кнопка для покупки подписки """

    text = f'{subscription.short_title} — {subscription.monthly_price:.2f}₽/мес'

    if discount is not None:
        text += f' ( скидка {discount}% )'

    if subscription.is_featured:
        text = f'🔶 {text} 🔶'

    return aiogram.types.InlineKeyboardButton(
        callback_data=f'buy:{subscription.id}',
        text=text
    )
