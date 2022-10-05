from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import gls

MFD_KEY = 'mfd'


async def mark_for_deletion(*messages: Message, state: FSMContext, group: str = 'default'):
    data = await state.get_data()
    data.setdefault(MFD_KEY, {})
    data[MFD_KEY].setdefault(group, [])
    for message in messages:
        data[MFD_KEY][group].append(message.message_id)
    await state.set_data(data)


async def delete_marked(*, state: FSMContext, group: str = 'default'):
    data = await state.get_data()
    if MFD_KEY not in data or group not in data[MFD_KEY]:
        return
    for message_id in data[MFD_KEY][group]:
        with suppress(TelegramBadRequest):
            await gls.bot.delete_message(state.key.chat_id, message_id)
