from pathlib import Path

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from utils import template

TEMPLATES = Path('apps/debug/templates')


async def command_debug(message: Message, state: FSMContext):
    data = await state.get_data()
    await template.render(TEMPLATES / 'debug.xml', {
        'user_id': message.from_user.id,
        'data': data.items()
    }).send(message.chat.id)


async def missed_query_handler(query: CallbackQuery):
    await query.message.answer(f'Unhandled query: {query.data}')
