import aiogram
from aiogram import F
from aiogram.filters import Command

from .. import filters
from . import callbacks, handlers

router = aiogram.Router()

# Take/View order by id
router.message(
    Command(commands=['order', 'view']),
    filters.is_employee
)(handlers.order_handler)

# Take top order
router.callback_query(
    F.data == 'order:take_top',
    filters.is_employee
)(handlers.order_handler)

# Take specific order
router.callback_query(
    callbacks.OrderCallback.filter(F.action == 'take'),
    filters.is_employee
)(handlers.order_handler)

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
