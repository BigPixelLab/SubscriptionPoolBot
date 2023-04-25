import peewee

import response_system as rs
import template
from apps.botpiska.models import Order


async def get_unprocessed_order_handler(_):
    """ ... """
    try:
        order = Order.select_open_joined().where(
            Order.processing_employee.is_null(True)
        ).order_by(Order.created_at).get()

    except peewee.DoesNotExist:
        return rs.feedback('Нет активных заказов')

    return rs.message(template.render('apps/order_processing/templates/op-message-order-detailed.xml', {
        'order': order
    }))


__all__ = ('get_unprocessed_order_handler',)
