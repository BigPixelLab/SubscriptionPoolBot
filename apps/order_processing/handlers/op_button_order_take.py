import aiogram.types
import peewee

import gls
import response_system as rs
import template
from apps.botpiska.models import Order
from apps.order_processing import callbacks


async def take_order_handler(_, user: aiogram.types.User, callback_data: callbacks.OrderActionCallback):
    """ ... """

    try:
        order = Order.select_by_id_joined(callback_data.order_id).get()
    except peewee.DoesNotExist:
        return rs.feedback(f'Заказа #{callback_data.order_id} нет в базе')

    if order.processing_employee_id:
        return rs.feedback(f'Заказ #{order.id} уже обрабатывается')

    if order.closed_at:
        return rs.feedback(f'Нельзя взять в обработку закрытый заказ')

    order.processing_employee = user.id
    order.save()

    notification = rs.Notification(
        template.render('apps/order_processing/templates/order-status-notifications/taken.xml', {
            'operator': user,
            'order': order
        }),
        [order.client_id],
        bot=gls.bot
    )

    return rs.edit_original(template.render('apps/order_processing/templates/op-message-order-detailed.xml', {
        'order': order
    }).extract(), notify=notification)


__all__ = ('take_order_handler',)
