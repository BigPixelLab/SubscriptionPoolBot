import aiogram
from aiogram import F
from aiogram.types import CallbackQuery

import posts
import settings
from apps.operator.commands import router as operator_router
from apps.pool_bot.commands import router as pool_bot_router
from apps.search.commands import router as search_router
from apps.coupons.commands import router as coupon_router
from apps.purchase.commands import router as purchase_router
from apps.debug.commands import router as debug_router

router = aiogram.Router()

routers: list[aiogram.Router] = [
    pool_bot_router,
    operator_router,
    coupon_router,
    purchase_router,
    router
]

# Register posts handlers
posts_router = aiogram.Router()
for register_func in posts.HANDLER_REGISTER_FUNCTIONS:
    register_func(posts_router)
routers.append(posts_router)

if settings.DEBUG:
    routers.append(debug_router)

# Must be at the end, contains handler which takes all the text messages
routers.append(search_router)


async def delete_this_message_handler(query: CallbackQuery):
    await query.message.delete()


router.callback_query(
    F.data == 'delete_this_message'
)(delete_this_message_handler)
