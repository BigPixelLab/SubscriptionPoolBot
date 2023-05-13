""" ... """
import aiogram

from . import filters, handlers

coupon_router = aiogram.Router()

coupon_router.message(
    filters.coupon_filter
)(handlers.coupon_message_handler)
