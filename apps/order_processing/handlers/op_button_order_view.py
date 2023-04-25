import peewee

import response_system as rs
import template
from apps.botpiska.models import Order, Subscription
from apps.coupons.models import Coupon
from apps.coupons.models_shared import CouponType
from apps.order_processing import callbacks


async def view_order_handler(_, callback_data: callbacks.OrderActionCallback):
    """ ... """

    try:
        order = Order.select_by_id(callback_data.order_id) \
            .join(Subscription) \
            .switch(Order) \
            .join(Coupon, peewee.JOIN.LEFT_OUTER) \
            .join(CouponType).get()

    except peewee.DoesNotExist:
        return rs.feedback(f'Заказа #{callback_data.order_id} нет в базе')

    return rs.edit_original(template.render('apps/order_processing/templates/op-message-order-detailed.xml', {
        'order': order
    }).extract())


__all__ = ('view_order_handler',)
