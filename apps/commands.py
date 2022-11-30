import aiogram
from aiogram.types import CallbackQuery

import resources
import settings
from apps.operator.commands import router as operator_router
from apps.pool_bot.commands import router as pool_bot_router
from apps.purchase import callbacks
from apps.search.commands import router as search_router
from apps.coupons.commands import router as coupon_router
from apps.purchase.commands import router as purchase_router
from apps.debug.commands import router as debug_router
from utils import template

router = aiogram.Router()

routers: list[aiogram.Router] = [
    pool_bot_router,
    operator_router,
    coupon_router,
    purchase_router,
    router
]

if settings.DEBUG:
    routers.append(debug_router)

# Must be at the end, contains handler which takes all the text messages
routers.append(search_router)


async def service_terms_handler(query: CallbackQuery, callback_data: callbacks.TermsCallback):
    await template.render(resources.resolve(callback_data.terms).path, {
        'terms': callback_data.terms
    }).send(query.message.chat.id, silence_errors=False)
    await query.answer()


async def delete_this_message_handler(query: CallbackQuery):
    await query.message.delete()

router.callback_query(
    callbacks.TermsCallback.filter()
)(service_terms_handler)

router.callback_query(
    aiogram.F.data == 'delete_this_message'
)(delete_this_message_handler)
