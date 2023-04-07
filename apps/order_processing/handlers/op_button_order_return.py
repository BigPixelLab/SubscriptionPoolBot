import peewee

import gls
import response_system as rs
import template
from apps.botpiska.models import Order, Subscription
from apps.coupons.models import Coupon
from apps.order_processing import callbacks


async def return_order_handler(_, callback_data: callbacks.OrderActionCallback):
    """ ... """

    try:
        order = Order.select().where(Order.id == callback_data.order_id) \
            .join(Subscription) \
            .switch(Order) \
            .join(Coupon, peewee.JOIN.LEFT_OUTER).get()

    except peewee.DoesNotExist:
        return rs.feedback(f'Заказа #{callback_data.order_id} нет в базе')

    if not order.processing_employee_id:
        return rs.feedback(f'Можно вернуть только взятый заказ')

    if order.closed_at:
        return rs.feedback(f'Нельзя вернуть закрытый заказ')

    order.processing_employee = None
    order.save()

    notification = rs.Notification(
        template.render('apps/order_processing/templates/order-status-notifications/returned.xml', {
            'order': order
        }),
        [order.client_id],
        bot=gls.bot
    )

    return rs.edit_original(template.render('apps/order_processing/templates/op-message-order-detailed.xml', {
        'order': order
    }).extract(), notify=notification)


__all__ = ('return_order_handler',)