from aiogram.types import User

import response_system_extensions as rse
import userdata
from apps.coupons.methods import get_suggested_coupon, CouponError, CouponNotFound


async def coupon_message_handler(_, user: User):
    """ ... """

    try:
        coupon = await get_suggested_coupon(user.id)
    except (CouponError, CouponNotFound):
        coupon = None

    return rse.tmpl_send('apps/botpiska/templates/message-coupon-general.xml', {
        'coupon': coupon
    })


async def coupon_deactivate_handler(_, user: User):
    """ ... """

    await userdata.set_data(user.id, coupon=None)

    return rse.tmpl_edit('apps/botpiska/templates/message-coupon-general.xml', {
        'coupon': None
    })


__all__ = ('coupon_message_handler', 'coupon_deactivate_handler')
