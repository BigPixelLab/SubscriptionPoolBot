import re
from typing import Callable
from xml.dom import minidom

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton, FSInputFile

from .scopes import message_scope, element_scope, inline_keyboard_scope, inline_keyboard_row_scope, \
    reply_keyboard_scope, reply_keyboard_row_scope
from .types_ import TextLayout, Context, MessageRender, InlineText, BlockText, PhotoUri, InlineKeyboardRow, \
    ReplyKeyboardRow, Scope, MessageRenderList, VideoUri
from .utils import show_element, duplicate_elements_contexts

SPACING_PATTERN = re.compile(r'\s+')


def parse_text_node(root: minidom.Element, context: Context) -> str:
    words = re.split(SPACING_PATTERN, root.nodeValue)
    return ' '.join(words).strip().format_map(context)


def traverse_and_parse_children(root: minidom.Element,
                                scope: Scope,
                                context: Context,
                                output_handler: Callable,
                                text_handler: Callable = None):
    for node in root.childNodes:
        # Text nodes
        if text_handler and node.nodeType == minidom.Element.TEXT_NODE:
            text = parse_text_node(node, context)
            if not text:
                continue
            text_handler(text)

        # Element nodes
        if node.nodeType == minidom.Element.ELEMENT_NODE:
            parser = scope.get(node.tagName)
            if not parser:
                raise ValueError(f'There is no registered tag name "{node.tagName}" in this scope')

            if not show_element(node, context):
                continue

            for _context in duplicate_elements_contexts(node, context):
                result = parser(node, _context)
                output_handler(result)


def parse_template(root: minidom.Element, context: Context) -> MessageRenderList:
    messages = MessageRenderList()

    if (msg_set := root.firstChild).tagName == 'message-set':
        not_parsed = msg_set.childNodes
    elif (msg := root.firstChild).tagName == 'message':
        not_parsed = [msg]
    else:
        raise ValueError('Only "message" or "message-set" can be the root tag')

    for node in not_parsed:
        if node.nodeType != minidom.Element.ELEMENT_NODE:
            continue

        if node.tagName != 'message':
            raise ValueError('"message-set" cannot contain non-message tags')

        if not show_element(node, context):
            continue

        for _context in duplicate_elements_contexts(node, context):
            result = parse_message(node, _context)
            messages.append(result)

    return messages


def parse_message(root: minidom.Element, context: Context) -> MessageRender:
    layout = TextLayout()
    render = MessageRender('')

    def output(result):
        if isinstance(result, InlineText):
            layout.append_inline(result)

        elif isinstance(result, BlockText):
            layout.append_block(result)

        elif isinstance(result, (PhotoUri, FSInputFile)):
            if render.photo or render.video:
                raise ValueError('Only one image or video can be specified per message')
            render.photo = result

        elif isinstance(result, VideoUri):
            if render.photo or render.video:
                raise ValueError('Only one image or video can be specified per message')
            render.video = result

        elif isinstance(result, (InlineKeyboardMarkup, ReplyKeyboardMarkup)):
            if render.keyboard:
                raise ValueError('Only one keyboard can be specified per message')
            render.keyboard = result

        elif result is None:
            return

        else:
            raise NotImplementedError('This type of result is not implemented')

    traverse_and_parse_children(
        root, message_scope, context,
        output_handler=output,
        text_handler=lambda txt: layout.append_inline(txt)
    )

    render.text = layout.finish()
    return render


def parse_element(root: minidom.Element, context: Context) -> str:
    layout = TextLayout()

    def output(result):
        if isinstance(result, InlineText):
            layout.append_inline(result)

        elif isinstance(result, BlockText):
            layout.append_block(result)

        elif result is None:
            return

        else:
            raise NotImplementedError('This type of result is not implemented')

    traverse_and_parse_children(
        root, element_scope, context,
        output_handler=output,
        text_handler=lambda txt: layout.append_inline(txt)
    )

    return layout.finish()


def parse_inline_keyboard(root: minidom.Element, context: Context) -> list[list[InlineKeyboardButton]]:
    layout = []
    row = []

    def output(result):
        if isinstance(result, InlineKeyboardButton):
            row.append(result)

        elif isinstance(result, InlineKeyboardRow):
            if row:
                layout.append(list(row))
                row.clear()
            layout.append(result)

        else:
            raise NotImplemented('This type of result is not implemented')

    traverse_and_parse_children(
        root, inline_keyboard_scope, context,
        output_handler=output
    )

    if row:
        layout.append(row)
    return layout


def parse_inline_keyboard_row(root: minidom.Element, context: Context) -> InlineKeyboardRow:
    layout = InlineKeyboardRow()

    def output(result):
        if isinstance(result, InlineKeyboardButton):
            layout.append(result)

        else:
            raise NotImplemented('This type of result is not implemented')

    traverse_and_parse_children(
        root, inline_keyboard_row_scope, context,
        output_handler=output,
    )

    return layout


def parse_reply_keyboard(root: minidom.Element, context: Context) -> list[list[KeyboardButton]]:
    layout = []
    row = []

    def output(result):
        if isinstance(result, KeyboardButton):
            row.append(result)

        elif isinstance(result, ReplyKeyboardRow):
            if row:
                layout.append(list(row))
                row.clear()
            layout.append(result)

        else:
            raise NotImplemented('This type of result is not implemented')

    traverse_and_parse_children(
        root, reply_keyboard_scope, context,
        output_handler=output,
    )

    if row:
        layout.append(row)
    return layout


def parse_reply_keyboard_row(root: minidom.Element, context: Context) -> ReplyKeyboardRow:
    layout = ReplyKeyboardRow()

    def output(result):
        if isinstance(result, KeyboardButton):
            layout.append(result)

        else:
            raise NotImplemented('This type of result is not implemented')

    traverse_and_parse_children(
        root, reply_keyboard_row_scope, context,
        output_handler=output
    )

    return layout
