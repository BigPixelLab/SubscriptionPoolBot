from __future__ import annotations

import os.path
import re

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

_cached_templates = {}

_keyboard_seperator = re.compile(r'([\-#]){3,}')
_button_pattern = re.compile(r'\[([\w\s]+)]')


INLINE_PRESET = InlineKeyboardBuilder, InlineKeyboardMarkup, 'inline_keyboard'
REPLY_PRESET = ReplyKeyboardBuilder, ReplyKeyboardMarkup, 'keyboard'


def render(template_path: str | os.PathLike, context: dict, *, use_cache: bool = True, as_caption: bool = False):
    """
    Отрисовывает шаблон из файла.
    Аргумент context используется для передачи в шаблон элементов для замены
      и для настройки кнопок клавиатуры.
    """
    template = _get_template(template_path, use_cache)
    return _render(template, context, as_caption)


def _render(template: str, context: dict, as_caption: bool):
    result = {}

    # Split message and keyboard
    message, *keyboard_markup = re.split(_keyboard_seperator, template, maxsplit=1)

    if keyboard_markup:
        _keyboard_type, keyboard_markup = keyboard_markup

        preset = INLINE_PRESET if _keyboard_type == '-' else REPLY_PRESET
        result["reply_markup"] = _render_as_keyboard(keyboard_markup, context, preset)

    # Formatting message
    text = "caption" if as_caption else "text"
    result[text] = _render_as_text(message, context)

    return result


def render_as_text(template_path: str | os.PathLike, context: dict, *, use_cache: bool = True):
    """ ... """
    template = _get_template(template_path, use_cache)
    return _render_as_text(template, context)


def _render_as_text(template: str, context: dict):
    # Formatting message
    paragraphs = template.strip().split('\n\n\n')

    _paragraphs = []
    for paragraph in paragraphs:
        lines = paragraph.split('\n\n')

        _lines = []
        for line in lines:
            _lines.append(line.replace('\n', ' '))

        _paragraphs.append('\n'.join(_lines))

    _message = '\n\n'.join(_paragraphs)
    _message = _message.format(**context)

    return _message


def render_as_keyboard(template_path: str | os.PathLike, context: dict, *, preset, use_cache: bool = True):
    """ ... """
    template = _get_template(template_path, use_cache)
    return _render_as_keyboard(template, context, preset)


def _render_as_keyboard(template: str, context: dict, preset):
    builder_class, keyboard_class, key = preset

    builder = builder_class()

    markup_rows = template.split('\n')
    for row in markup_rows:
        button_markups = re.findall(_button_pattern, row)

        for button_markup in button_markups:
            title = button_markup

            button_args = {'text': title}
            button_args.update(context.get(title, {}))

            builder.button(**button_args)

        if button_markups:
            builder.row()

    markup = builder.export()
    return keyboard_class(**{key: markup})


def _get_template(path: str, use_cache: bool):
    global _cached_templates

    resolved_path = os.path.abspath(path)

    if use_cache and resolved_path in _cached_templates:
        template = _cached_templates[resolved_path]
    else:
        with open(resolved_path, 'rt', encoding='utf-8') as file:
            template = file.read()

        if use_cache:
            _cached_templates[resolved_path] = template

    return template
