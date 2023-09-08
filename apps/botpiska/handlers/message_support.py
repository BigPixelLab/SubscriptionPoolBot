""" ... """
import aiogram.types
import response_system_extensions as rse
from apps.statistics.models import Statistic


async def support_message_handler(_, user: aiogram.types.User):
    """ ... """
    Statistic.record('open_support', user.id)
    return rse.tmpl_send('apps/botpiska/templates/message-support.xml', {})


__all__ = ('support_message_handler',)
