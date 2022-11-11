import aiogram
from aiogram import F
from aiogram.filters import Command

from .. import filters
from . import handlers

router = aiogram.Router()

# Open operator panel
router.message(
    Command(commands=['operator', 'op']),
    filters.is_employee  # Expensive, has call to the database
)(handlers.show_operator_panel_handler)

# Update operator panel
router.callback_query(
    F.data == 'cp:update',
    filters.is_employee
)(handlers.update_operator_panel_handler)

router.message(
    Command(commands=['post']),
    filters.is_employee
)(handlers.send_mailing)
