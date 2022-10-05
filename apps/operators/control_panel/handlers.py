from contextlib import suppress

from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from apps.operators.control_panel.renders import render_operator_panel


async def show_operator_panel_handler(message: Message):
    await message.answer(**render_operator_panel())


async def update_operator_panel_handler(query: CallbackQuery):
    with suppress(TelegramBadRequest):
        await query.message.edit_text(**render_operator_panel())
    await query.answer('Панель оператора обновлена')
