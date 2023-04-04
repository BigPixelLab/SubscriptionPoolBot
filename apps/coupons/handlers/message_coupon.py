""" ... """
import aiogram

from ..methods import activate_coupon


async def coupon_message_handler(_, user: aiogram.types.User, code: str):
    """ ... """
    return await activate_coupon(code, user)


__all__ = ('coupon_message_handler',)
