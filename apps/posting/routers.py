import aiogram.filters

from apps.botpiska import filters
from apps.posting import handlers

posting_router = aiogram.Router()

posting_router.message(
    aiogram.filters.Command(commands=['post']),
    filters.employee_filter
)(handlers.post_handler_command)
