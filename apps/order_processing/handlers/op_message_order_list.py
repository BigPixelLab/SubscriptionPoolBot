import response_system_extensions as rse
from apps.botpiska.models import Order, Subscription


async def get_orders_handler(_):
    """ ... """
    orders = Order.select_open().join(Subscription).order_by(Order.created_at)
    return rse.tmpl_send('apps/order_processing/templates/op-message-order-list.xml', {
        'orders': list(orders)
    })


async def update_orders_handler(_):
    """ ... """
    orders = Order.select_open().join(Subscription).order_by(Order.created_at)
    return rse.tmpl_edit('apps/order_processing/templates/op-message-order-list.xml', {
        'orders': list(orders)
    })


__all__ = ('get_orders_handler', 'update_orders_handler')
