from dataclasses import dataclass

from aiogram import Router
from aiogram.types import CallbackQuery

from . import handlers
from ..purchase.callbacks import CheckBillCallback
from ..purchase.handlers import bill_paid_handler

router = Router()

router.message(commands=['debug'])(handlers.command_debug)
router.callback_query()(handlers.missed_query_handler)

router.message(
	commands=['test']
)(handlers.test_handler)
