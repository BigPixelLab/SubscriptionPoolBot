import aiogram.filters
import peewee

import response_system as rs
import response_system_extensions as rse
from apps.botpiska.models import Order


async def view_command_handler(_, command: aiogram.filters.CommandObject):
    """ ... """
    if not command.args:
        return rs.feedback('Формат: /view order-id')

    try:
        order_id = int(command.args)
    except ValueError:
        return rs.feedback('"order-id" должно быть integer')

    try:
        order = Order.select_by_id_joined(order_id).get()
    except peewee.DoesNotExist:
        return rs.feedback(f'Заказа #{order_id} нет в базе')

    return rse.tmpl_send('apps/order_processing/templates/op-message-order-detailed.xml', {
        'order': order
    })
