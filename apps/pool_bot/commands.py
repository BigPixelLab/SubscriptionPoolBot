import aiogram
from aiogram import F

from . import handlers

router = aiogram.Router()

router.startup()(handlers.on_startup)

# Intro command
router.message(commands=['start'])(handlers.command_start)
router.message(F.text == 'Поддержка')(handlers.support_handler)
router.message(F.text == 'Соглашение')(handlers.terms_handler)
