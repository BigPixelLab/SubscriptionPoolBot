import response_system as rs
import template
from apps.botpiska.models import Order, Subscription


async def get_orders_handler(_):
    """ ... """
    orders = Order.select_open().join(Subscription).order_by(Order.created_at)
    return rs.message(template.render('apps/order_processing/templates/op-message-order-list.xml', {
        'orders': list(orders)
    }).extract())


async def update_orders_handler(_):
    """ ... """
    orders = Order.select_open().join(Subscription).order_by(Order.created_at)
    return rs.edit_original(template.render('apps/order_processing/templates/op-message-order-list.xml', {
        'orders': list(orders)
    }).extract())


__all__ = ('get_orders_handler', 'update_orders_handler')
