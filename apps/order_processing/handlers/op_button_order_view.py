import peewee

import response_system as rs
import response_system_extensions as rse
from apps.botpiska.models import Order
from apps.order_processing import callbacks


async def view_order_handler(_, callback_data: callbacks.OrderActionCallback):
    """ ... """

    try:
        order = Order.select_by_id_joined(callback_data.order_id).get()
    except peewee.DoesNotExist:
        return rs.feedback(f'Заказа #{callback_data.order_id} нет в базе')

    return rse.tmpl_edit('apps/order_processing/templates/op-message-order-detailed.xml', {
        'order': order
    })


__all__ = ('view_order_handler',)
