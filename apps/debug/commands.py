from aiogram import Router

from . import handlers

router = Router()

router.message(commands=['debug'])(handlers.command_debug)
router.callback_query()(handlers.missed_query_handler)
