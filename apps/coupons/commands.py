import aiogram
from aiogram.filters import ContentTypesFilter
from aiogram.types import ContentType

from . import filters, handlers

router = aiogram.Router()

# Coupon activation
router.message(
    ContentTypesFilter(content_types=[ContentType.TEXT]),
    filters.CouponLikeFilter()
)(handlers.coupon_handler)
