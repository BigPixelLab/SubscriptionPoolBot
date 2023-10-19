""" ... """
from __future__ import annotations

import aiogram.types
import peewee

import response_system as rs
from apps.botpiska import callbacks
from apps.botpiska.methods import send_bill
from apps.botpiska.models import Subscription
from apps.statistics.models import Statistics


async def buy_button_handler(_, callback_data: callbacks.BuyButtonCallbackData, user:aiogram.types.User):
    """ ... """

    user = aiogram.types.User.get_current()

    try:
        subscription = Subscription.get_by_id(callback_data.subscription_id)
        Statistics.record('open_bill', user.id, subscription_id=callback_data.subscription_id)
    except peewee.DoesNotExist:
        return rs.no_response()

    return await send_bill(user, subscription)


__all__ = (
    'buy_button_handler',
)
