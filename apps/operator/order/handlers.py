from pathlib import Path

from aiogram.types import CallbackQuery

from utils import template
from . import queries, callbacks
from ...orders import models as order_models
from ...search import models as search_models

TEMPLATES = Path('apps/operator/order/templates')


async def take_top_order_handler(query: CallbackQuery):
    query_result = queries.get_top_order_info()
    if not query_result:
        await query.answer('Нет активных заказов')
        return

    order_id, customer_id = query_result

    order_models.Order.mark_as_taken(order_id, query.from_user.id)

    await template.render(TEMPLATES / 'notify/taken.xml', {
        'order_id': order_id,
    }).send(customer_id)

    order = order_models.Order.get(order_id)
    subscription = search_models.Subscription.get(order.subscription)
    service = search_models.Service.get_name(subscription.service)

    activation_code = None
    if subscription.is_code_required:
        activation_code = queries.get_activation_code(order.id)

    await template.render(TEMPLATES / 'details.xml', {
        'order': order,
        'subscription': subscription,
        'service': service,
        'activation_code': activation_code
    }).send(query.message.chat.id)


async def return_order_handler(query: CallbackQuery, callback_data: callbacks.OrderCallback):
    ...
