import datetime

import peewee

import gls
import response_system as rs
import response_system_extensions as rse
from apps.botpiska.models import Order
from apps.order_processing import callbacks


async def close_order_handler(_, callback_data: callbacks.OrderActionCallback) -> rs.Response:
    """ ... """

    try:
        order = Order.select_by_id_joined(callback_data.order_id).get()
    except peewee.DoesNotExist:
        return rs.feedback(f'Заказа #{callback_data.order_id} нет в базе')

    if not order.processing_employee_id:
        return rs.feedback(f'Можно закрыть только взятый заказ')

    if order.closed_at:
        return rs.feedback(f'Заказ уже закрыт')

    order.closed_at = datetime.datetime.now()
    order.save()

    return (
        rse.tmpl_edit('apps/order_processing/templates/op-message-order-detailed.xml', {
            'order': order
        })
        + rse.tmpl_send('apps/order_processing/templates/order-status-notifications/closed.xml', {
            'order': order
        }, chat=order.client_id, bot=gls.bot)
    )


__all__ = ('close_order_handler',)
