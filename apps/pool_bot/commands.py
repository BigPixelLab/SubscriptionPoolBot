import aiogram
from aiogram import F
from aiogram.filters import Command

from . import handlers
from ..operator import filters

router = aiogram.Router()

router.startup()(handlers.on_startup)

# Intro command
router.message(commands=['start'])(handlers.command_start)
router.message(F.text == 'Поддержка')(handlers.support_handler)
router.message(F.text == 'Соглашение')(handlers.terms_handler)

router.message(
    Command(commands=['updrs']),
    filters.is_employee
)(handlers.update_resources_handler)

router.message(
    Command(commands=['send']),
    filters.is_employee
)(handlers.send_message_handler)
