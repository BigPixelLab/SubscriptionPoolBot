from pathlib import Path

import aiogram
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import gls
from utils import template

TEMPLATES = Path('apps/debug/templates')


async def command_debug(message: Message, state: FSMContext):
    data = await state.get_data()
    render = template.render(TEMPLATES / 'debug.xml', {
        'data': data.items()
    })
    await template.send(gls.bot, message.chat.id, render)


async def missed_query_handler(query: CallbackQuery):
    await query.message.answer(f'Unhandled query: {query.data}')
