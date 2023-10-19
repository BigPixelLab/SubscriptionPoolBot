import aiogram.filters
from aiogram.filters import Command

from . import handlers

# Команды доступные только в DEBUG режиме
only_in_dev_debug_router = aiogram.Router()

only_in_dev_debug_router.callback_query.register(
    handlers.unhandled_callback_query
)

only_in_dev_debug_router.message(
    Command(commands=['test'])
)(handlers.test_handler)

# Команды доступные в любом режиме
debug_router = aiogram.Router()
