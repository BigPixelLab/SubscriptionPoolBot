import aiogram.filters
import peewee

import response_system as rs
import template
from apps.botpiska.models import Order, Subscription
from apps.coupons.models import Coupon


async def view_command_handler(_, command: aiogram.filters.CommandObject):
    """ ... """
    if not command.args:
        return rs.feedback('Формат: /view order-id')

    try:
        order_id = int(command.args)
    except ValueError:
        return rs.feedback('"order-id" должно быть integer')

    try:
        order = Order.select().where(Order.id == order_id) \
            .join(Subscription) \
            .switch(Order) \
            .join(Coupon, peewee.JOIN.LEFT_OUTER).get()

    except peewee.DoesNotExist:
        return rs.feedback(f'Заказа #{order_id} нет в базе')

    return rs.message(template.render('apps/order_processing/templates/op-message-order-detailed.xml', {
        'order': order
    }).extract())
