import aiogram.filters

from . import handlers

# Команды доступные только в DEBUG режиме
only_in_dev_debug_router = aiogram.Router()

only_in_dev_debug_router.callback_query.register(
    handlers.unhandled_callback_query
)

# Команды доступные в любом режиме
debug_router = aiogram.Router()
