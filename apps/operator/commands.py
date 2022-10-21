import aiogram
from aiogram.filters import Command

from . import handlers
from .control_panel.commands import router as control_panel_router
from .filters import is_employee
from .order.commands import router as order_router

router = aiogram.Router()

router.include_router(control_panel_router)
router.include_router(order_router)

router.message(
    Command(commands=['notify']),
    is_employee
)(handlers.set_notify_status_handler)
