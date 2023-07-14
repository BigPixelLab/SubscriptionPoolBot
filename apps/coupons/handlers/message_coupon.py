""" ... """
import aiogram

import response_system as rs
from apps.coupons import methods as coupons_methods
from ..methods import activate_coupon


async def coupon_message_handler(_, user: aiogram.types.User, code: str):
    """ ... """
    try:
        return await activate_coupon(code, user)

    except coupons_methods.CouponNotFound:
        return rs.feedback(
            f'Не удалось найти купон "{code}"'
        )

    except coupons_methods.CouponProhibited as error:
        return rs.feedback(
            f'Использующийся купон "{error.coupon.code}", вероятно, создан '
            'вами и предназначается для других пользователей'
        )

    except coupons_methods.CouponExpired as error:
        return rs.feedback(
            f'Срок действия использующегося купона "{error.coupon.code}" иссяк '
            f'{error.coupon.created_at + error.coupon.type.lifespan:%d.%m}'
        )

    except coupons_methods.CouponExceededUsage as error:
        return rs.feedback(
            f'Превышено число использований купона "{error.coupon.code}" '
            f'({error.coupon.max_usages} использований)'
        )

    except coupons_methods.CouponWrongSubscription as error:
        return rs.feedback(
            f'Использующийся купон "{error.coupon.code}" не распространяется '
            'на данную подписку'
        )

    except coupons_methods.CouponAlreadyUsed as error:
        return rs.feedback(
            f'Вы уже использовали купон "{error.coupon.code}" при покупке ранее'
        )


__all__ = ('coupon_message_handler',)
