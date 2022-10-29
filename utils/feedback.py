from __future__ import annotations

import asyncio

from aiogram import Bot
from aiogram.types import Message

import settings


async def send_waiting(text: str, chat_id: int, /, *, bot: Bot = None) -> Message:
    bot: Bot = bot or Bot.get_current()
    return await bot.send_message(chat_id, text, disable_notification=True)


async def send_feedback(text: str, chat_id: int, /, *, bot: Bot = None):
    """ Should be called somewhere at the end of the handler. Blocks execution """
    bot: Bot = bot or Bot.get_current()
    message = await bot.send_message(chat_id, text)
    await asyncio.sleep(settings.FEEDBACK_TIME)
    await message.delete()
