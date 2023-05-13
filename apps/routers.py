"""
Подключение handler-ов произведено таким образом (а не напрямую к
dispatcher-у, например) для явного контроля порядка, в котором
события будут обрабатываться, вместо того чтобы рассчитывать на
порядок импорта, как было бы в противном случае
"""
import aiogram

import settings
from .botpiska.routers import botpiska_router, op_botpiska_router
from .coupons.routers import coupon_router
from .debug.routers import debug_router, only_in_dev_debug_router
from .notifications.routers import notifications_router
from .order_processing.routers import op_order_processing_router
from .posting.routers import posting_router
from .seasons.routers import seasons_router

# Router-ы основного бота
routers: list[aiogram.Router] = [
    botpiska_router,
    posting_router,
    notifications_router,
    coupon_router,
    seasons_router,
    debug_router,
]

if settings.DEBUG:
    routers.append(only_in_dev_debug_router)

# Router-ы операторского бота
operator_routers: list[aiogram.Router] = [
    op_order_processing_router,
    op_botpiska_router,
]
