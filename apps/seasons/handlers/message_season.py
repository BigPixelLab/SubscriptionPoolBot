""" ... """
import aiogram.types

import response_system_extensions as rse
from apps.botpiska.models import Client


async def season_message_handler(_, user: aiogram.types.User):
    """ ... """
    points = Client.get_or_register(user.id).season_bonuses
    return rse.tmpl_send('apps/seasons/templates/message-season-general.xml', {
        'monthly-prize': '[КАКОЙ-ТО ПРИЗ]',
        'points-current': points,
        'points-total': 1000
    })


__all__ = ('season_message_handler',)
