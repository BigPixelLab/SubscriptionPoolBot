import aiogram.filters

from apps.botpiska import filters
from apps.posting import handlers, states, callbacks

posting_router = aiogram.Router()

posting_router.message(
    aiogram.filters.Command(commands=['post']),
    filters.employee_filter
)(handlers.post_handler_command)

posting_router.message(
    states.PostStates.WAITING_FOR_POST,
    filters.employee_filter
)(handlers.post_received_handler)

posting_router.callback_query(
    callbacks.PostCallback.filter(),
    filters.employee_filter
)(handlers.post_button_handler)
