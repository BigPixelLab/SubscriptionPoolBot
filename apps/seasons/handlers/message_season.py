""" ... """
import aiogram.types

import response_system as rs
import template
from apps.botpiska.models import Client


async def season_message_handler(_, user: aiogram.types.User):
    """ ... """
    points = Client.get_or_register(user.id).season_bonuses
    return rs.message(template.render('apps/seasons/templates/message-season-general.xml', {
        'monthly-prize': '[КАКОЙ-ТО ПРИЗ]',
        'points-current': points,
        'points-total': 1000
    }))


__all__ = ('season_message_handler',)
