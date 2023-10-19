""" ... """
import aiogram.filters

import response_system as rs
import response_system_extensions as rse
from apps.botpiska import services
from apps.coupons import methods as coupons_methods
from apps.statistics.models import *


async def start_command_handler(_, command: aiogram.filters.CommandObject, user: aiogram.types.User):
    """ ... """

    client, is_created = Client.get_or_register(user.id)
    # Если передан купон как deep-link
    if command.args and coupons_methods.is_coupon_like(command.args):
        Statistics.record('command_start_deep_link', user.id,coupon=command.args)
        rs.respond(await coupons_methods.activate_coupon(command.args, user, silent=True))
    elif is_created:
        Statistics.record('first_command_start', user.id)
    else:
        Statistics.record('command_start', user.id)
    return rse.tmpl_send('apps/botpiska/templates/message-start.xml', {
        'services': services.Service.get_search_titles()
    })

async def previous_state_handler(_):
    return rse.tmpl_send('apps/botpiska/templates/message-previous-state.xml', {
        'services': services.Service.get_search_titles()
    })


__all__ = ('start_command_handler', 'previous_state_handler',)
