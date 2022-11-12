from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile

import resources
from .parsing import parse_element, parse_inline_keyboard_row, parse_inline_keyboard, parse_reply_keyboard, \
    parse_reply_keyboard_row
from .types_ import Scope, ReplyKeyboardRow, InlineKeyboardRow, PhotoUri, InlineText, BlockText, VideoUri
from .utils import mp
from .scopes import message_scope, element_scope, inline_keyboard_scope, inline_keyboard_row_scope, \
    reply_keyboard_scope, reply_keyboard_row_scope


# Text arranging
@Scope.register('br', message_scope, element_scope)
def break_parser(*_) -> BlockText:
    return BlockText('')


@Scope.register('p', message_scope, element_scope)
def paragraph_parser(element, context) -> BlockText:
    value = parse_element(element, context)
    return BlockText(mp(element, '', value, '', padding_only=True))


@Scope.register('x', message_scope, element_scope)
def paragraph_parser(element, context) -> InlineText:
    value = parse_element(element, context)
    return InlineText(mp(element, '', value, ''))


# Interactive

@Scope.register('a', message_scope, element_scope)
def paragraph_parser(element, context) -> InlineText:
    href = element.attributes.get('href').value.format_map(context)
    value = parse_element(element, context)
    return InlineText(mp(element, f'<a href="{href}">', value, '</a>'))


# Basic html styling

@Scope.register('b', message_scope, element_scope)
def paragraph_parser(element, context) -> InlineText:
    value = parse_element(element, context)
    return InlineText(mp(element, '<b>', value, '</b>'))


@Scope.register('i', message_scope, element_scope)
def paragraph_parser(element, context) -> InlineText:
    value = parse_element(element, context)
    return InlineText(mp(element, '<i>', value, '</i>'))


@Scope.register('u', message_scope, element_scope)
def paragraph_parser(element, context) -> InlineText:
    value = parse_element(element, context)
    return InlineText(mp(element, '<u>', value, '</u>'))


@Scope.register('m', message_scope, element_scope)
def paragraph_parser(element, context) -> InlineText:
    value = parse_element(element, context)
    return InlineText(mp(element, '<code>', value, '</code>'))


# Custom styling

@Scope.register('h1', message_scope, element_scope)
def paragraph_parser(element, context) -> BlockText:
    value = parse_element(element, context)
    return BlockText(mp(element, '<b>', value.upper(), '</b>'))


@Scope.register('h2', message_scope, element_scope)
def paragraph_parser(element, context) -> BlockText:
    value = parse_element(element, context)
    return BlockText(mp(element, '<b>', value.title(), '</b>'))


@Scope.register('h3', message_scope, element_scope)
def paragraph_parser(element, context) -> BlockText:
    value = parse_element(element, context)
    return BlockText(mp(element, '<i><u>', value.title(), '</u></i>'))


@Scope.register('up', message_scope, element_scope)
def paragraph_parser(element, context) -> InlineText:
    value = parse_element(element, context)
    return InlineText(mp(element, '', value.upper(), ''))


@Scope.register('lw', message_scope, element_scope)
def paragraph_parser(element, context) -> InlineText:
    value = parse_element(element, context)
    return InlineText(mp(element, '', value.lower(), ''))


@Scope.register('ttl', message_scope, element_scope)
def paragraph_parser(element, context) -> InlineText:
    value = parse_element(element, context)
    return InlineText(mp(element, '', value.title(), ''))


@Scope.register('aln-l', message_scope, element_scope)
def paragraph_parser(element, context) -> InlineText:
    width = int(element.attributes.get('width').value)
    fill = attr.value if (attr := element.attributes.get('fill')) else ' '
    value = parse_element(element, context)
    return InlineText(mp(element, '', value.ljust(width, fill), ''))


@Scope.register('aln-r', message_scope, element_scope)
def paragraph_parser(element, context) -> InlineText:
    width = int(element.attributes.get('width').value)
    fill = attr.value if (attr := element.attributes.get('fill')) else ' '
    value = parse_element(element, context)
    return InlineText(mp(element, '', value.rjust(width, fill), ''))


@Scope.register('aln-c', message_scope, element_scope)
def paragraph_parser(element, context) -> InlineText:
    width = int(element.attributes.get('width').value)
    fill = attr.value if (attr := element.attributes.get('fill')) else ' '
    value = parse_element(element, context)
    return InlineText(mp(element, '', value.center(width, fill), ''))


# Additive

@Scope.register('set', message_scope, element_scope)
def set_cv_parser(element, context) -> None:
    cv_attr = element.attributes['cv']
    to_attr = element.attributes['to']
    context[cv_attr.value] = eval(to_attr.value, {}, context)


# Aiogram specific stuff

@Scope.register('img', message_scope)
def image_parser(element, context) -> PhotoUri | FSInputFile:
    if file_attr := element.attributes.get('file'):
        return PhotoUri(file_attr.value)
    if file_attr := element.attributes.get('index'):
        from aiogram import Bot
        return PhotoUri(resources.get(file_attr.value, key=Bot.get_current().id))
    if src_attr := element.attributes.get('src'):
        return FSInputFile(path=src_attr.value.format_map(context), filename='hello.jpg')
    raise ValueError('Tag "img" must contain "src" attribute')


@Scope.register('video', message_scope)
def image_parser(element, context) -> VideoUri:
    try:
        src_attr = element.attributes['src']
    except KeyError:
        raise ValueError('Tag "video" must contain "src" attribute')
    return VideoUri(src_attr.value.format_map(context))


@Scope.register('inline-keyboard', message_scope)
def inline_keyboard_parser(element, context) -> InlineKeyboardMarkup:
    layout = parse_inline_keyboard(element, context)
    return InlineKeyboardMarkup(inline_keyboard=layout)


@Scope.register('kr', inline_keyboard_scope)
def inline_keyboard_row_parser(element, context) -> InlineKeyboardRow:
    return parse_inline_keyboard_row(element, context)


@Scope.register('button', inline_keyboard_scope, inline_keyboard_row_scope)
def inline_keyboard_button_parser(element, context) -> InlineKeyboardButton:
    settings = {}

    if text_attr := element.attributes.get('text'):
        settings['text'] = text_attr.value.format_map(context)

    if url_attr := element.attributes.get('url'):
        settings['url'] = url_attr.value.format_map(context)

    if callback_data_attr := element.attributes.get('callback_data'):
        settings['callback_data'] = callback_data_attr.value.format_map(context)

    if siq_attr := element.attributes.get('switch_inline_query'):
        settings['switch_inline_query'] = siq_attr.value.format_map(context)

    if siq_current_chat_attr := element.attributes.get('switch_inline_query_current_chat'):
        settings['switch_inline_query_current_chat'] = siq_current_chat_attr.value.format_map(context)

    if pay_attr := element.attributes.get('pay'):
        settings['pay'] = pay_attr.value == 'True'

    if id_attr := element.attributes.get('id'):
        settings.update(context[id_attr.value])

    if 'text' not in settings:
        settings['text'] = parse_element(element, context)

    return InlineKeyboardButton(**settings)


@Scope.register('reply-keyboard', message_scope)
def reply_keyboard_parser(element, context) -> ReplyKeyboardMarkup:
    settings = {}

    if resize_keyboard_attr := element.attributes.get('resize_keyboard'):
        settings['resize_keyboard'] = resize_keyboard_attr.value == 'True'

    if one_time_keyboard_attr := element.attributes.get('one_time_keyboard'):
        settings['one_time_keyboard'] = one_time_keyboard_attr.value.lower() == 'True'

    if input_field_placeholder_attr := element.attributes.get('input_field_placeholder'):
        settings['input_field_placeholder'] = input_field_placeholder_attr.value.format_map(context)

    if selective_attr := element.attributes.get('selective'):
        settings['selective'] = selective_attr.value.lower() == 'True'

    if id_attr := element.attributes.get('id'):
        settings.update(context[id_attr.value])

    if 'keyboard' not in settings:
        settings['keyboard'] = parse_reply_keyboard(element, context)

    return ReplyKeyboardMarkup(**settings)


@Scope.register('kr', reply_keyboard_scope)
def reply_keyboard_row_parser(element, context) -> ReplyKeyboardRow:
    return parse_reply_keyboard_row(element, context)


@Scope.register('button', reply_keyboard_scope, reply_keyboard_row_scope)
def reply_keyboard_button_parser(element, context) -> KeyboardButton:
    settings = {}

    if text_attr := element.attributes.get('text'):
        settings['text'] = text_attr.value.format_map(context)

    if request_contact_attr := element.attributes.get('request_contact'):
        settings['request_contact'] = request_contact_attr.value.lower() == 'True'

    if request_location_attr := element.attributes.get('request_location'):
        settings['request_location'] = request_location_attr.value.lower() == 'True'

    if id_attr := element.attributes.get('id'):
        settings.update(context[id_attr.value])

    if 'text' not in settings:
        settings['text'] = parse_element(element, context)

    return KeyboardButton(**settings)


# CUSTOM

@Scope.register('subscription', message_scope, element_scope)
def subscription_parser(_, context):
    service = context.get('service')
    if service and hasattr(service, 'name'):
        service = service.name
    if not service:
        service = context.get('service_name')
    assert service

    subscription = context.get('subscription')
    if subscription and hasattr(subscription, 'name'):
        subscription = subscription.name
    if not subscription:
        subscription = context.get('subscription_name')
    assert subscription

    return InlineText(f'{service.upper()} {subscription}')


@Scope.register('order', message_scope, element_scope)
def order_parser(_, context):
    order = context.get('order')
    if order and hasattr(order, 'id'):
        order = order.id
    if not order:
        order = context.get('order_id')
    assert order

    return InlineText(f'#{order}')
