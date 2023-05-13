""" ... """
import aiogram.filters

import response_system as rs
import response_system_extensions as rse
from apps.botpiska import services
from apps.coupons import methods as coupons_methods


async def start_command_handler(_, command: aiogram.filters.CommandObject, user: aiogram.types.User):
    """ ... """

    # Если передан купон как deep-link
    if command.args and coupons_methods.is_coupon_like(command.args):
        rs.respond(await coupons_methods.activate_coupon(command.args, user, silent=True))

    return rse.tmpl_send('apps/botpiska/templates/message-start.xml', {
        'services': services.Service.get_search_titles()
    })


__all__ = ('start_command_handler',)
