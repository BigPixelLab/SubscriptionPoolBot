import aiogram

from .control_panel.commands import router as cp_router
from .order.commands import router as order_router

router = aiogram.Router()

router.include_router(cp_router)
router.include_router(order_router)
