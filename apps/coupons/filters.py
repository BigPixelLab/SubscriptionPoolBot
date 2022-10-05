import string

import aiogram.filters


class CouponLikeFilter(aiogram.filters.BaseFilter):
    POSSIBLE_COUPON_SYMBOLS = set(string.digits + string.ascii_uppercase + '-')
    COUPON_LENGTH = 6

    async def __call__(self, message: aiogram.types.Message):
        coupon = message.text or message.caption

        if not coupon:
            return False

        if not set(coupon).issubset(self.POSSIBLE_COUPON_SYMBOLS) or \
                len(coupon) != self.COUPON_LENGTH:
            return False

        return {'coupon_code': coupon}
