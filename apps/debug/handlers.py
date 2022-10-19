from pathlib import Path

import aiogram.types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from apps.purchase.callbacks import CheckBillCallback
from utils import template

TEMPLATES = Path('apps/debug/templates')


async def test_handler(message: Message):
    keyboard = aiogram.types.InlineKeyboardMarkup(
        inline_keyboard=[[aiogram.types.InlineKeyboardButton(
            text='TEST',
            callback_data=CheckBillCallback(
                bill_id='',
                sub_id=3,
                coupon=''
            ).pack()
        )]]
    )

    await message.answer('...', reply_markup=keyboard)


async def command_debug(message: Message, state: FSMContext):
    data = await state.get_data()
    await template.render(TEMPLATES / 'debug.xml', {
        'data': data.items()
    }).send(message.chat.id)


async def missed_query_handler(query: CallbackQuery):
    await query.message.answer(f'Unhandled query: {query.data}')
