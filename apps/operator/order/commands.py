import aiogram
from aiogram import F

from .. import filters
from . import callbacks, handlers_

router = aiogram.Router()

# Take top order
router.callback_query(
    F.data == 'order:take_top',
    filters.is_employee
)(handlers.take_top_order_handler)

# Take specific order
router.callback_query(
    callbacks.OrderCallback.filter(F.action == 'take'),
    filters.is_employee
)(handlers.take_top_order_handler)

# Return order
router.callback_query(
    callbacks.OrderCallback.filter(F.action == 'return'),
    filters.is_employee
)(handlers.return_order_handler)

# Close order
router.callback_query(
    callbacks.OrderCallback.filter(F.action == 'close'),
    filters.is_employee
)(handlers.close_order_handler)
