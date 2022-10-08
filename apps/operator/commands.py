import aiogram

from .control_panel.commands import router as control_panel_router
from .order.commands import router as order_router

router = aiogram.Router()

router.include_router(control_panel_router)
router.include_router(order_router)
