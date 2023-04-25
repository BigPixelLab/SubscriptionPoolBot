import peewee

import response_system as rs
import template
from apps.botpiska.models import Order, Subscription
from apps.coupons.models import Coupon, CouponType
from apps.order_processing import callbacks


async def view_order_handler(_, callback_data: callbacks.OrderActionCallback):
    """ ... """

    try:
        order = Order.select_by_id_joined(callback_data.order_id).get()
    except peewee.DoesNotExist:
        return rs.feedback(f'Заказа #{callback_data.order_id} нет в базе')

    return rs.edit_original(template.render('apps/order_processing/templates/op-message-order-detailed.xml', {
        'order': order
    }).extract())


__all__ = ('view_order_handler',)
