import aiogram
from aiogram import F

from . import handlers

seasons_router = aiogram.Router()

# Запрос "Сезон"
seasons_router.message(
    F.text.lower() == "сезон"
)(handlers.season_message_handler)
