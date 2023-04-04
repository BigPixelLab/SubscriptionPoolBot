""" ... """
import aiogram.filters

import response_system as rs
import template
from apps.botpiska import services
from apps.coupons import methods as coupons_methods


async def start_command_handler(_, command: aiogram.filters.CommandObject, user: aiogram.types.User):
    """ ... """

    additional_responses = []

    # Если передан купон как deep-link
    if command.args and coupons_methods.is_coupon_like(command.args):
        additional_responses += await coupons_methods.activate_coupon(command.args, user, silent=True)

    return rs.message(template.render('apps/botpiska/templates/message-start.xml', {
        'services': services.Service.get_search_titles()
    })) + additional_responses


__all__ = ('start_command_handler',)
