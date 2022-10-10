from pathlib import Path

from aiogram.types import CallbackQuery, Message

from aiogram.filters import CommandObject

from utils import template
from . import queries, callbacks
from ...orders import models as order_models
from ...search import models as search_models

TEMPLATES = Path('apps/operator/order/templates')


async def take_order_by_id(message: Message, command: CommandObject):
    print(command.args)
    order_id = int(command.args)
    order = order_models.Order.get(order_id)

    if not order:
        await message.answer(f'Заказ с id = {order_id} не найден')
        return

    order_models.Order.mark_as_taken(order_id, message.from_user.id)
    order.processed_by = message.from_user.id
    print(order)

    await template.render(TEMPLATES / 'notify/taken.xml', {
        'operator_id': message.from_user.id,
        'order_id': order.id
    }).send(order.customer_id)

    subscription = order.get_subscription()
    service = search_models.Service.get_name(subscription.service)

    activation_code = None
    if subscription.is_code_required:
        activation_code = queries.get_activation_code(order_id)

    await template.render(TEMPLATES / 'details.xml', {
        'order': order,
        'sub': subscription,
        'service': service,
        'activation_code': activation_code
    }).send(message.chat.id)


async def take_top_order_handler(query: CallbackQuery):
    order = order_models.Order.get_top()

    if not order:
        await query.answer('Нет активных заказов')
        return

    order_models.Order.mark_as_taken(order.id, query.from_user.id)
    # Instances are not updated automatically, so setting attribute
    # manually to avoid executing another database query
    order.processed_by = query.from_user.id

    await template.render(TEMPLATES / 'notify/taken.xml', {
        'operator_id': query.from_user.id,
        'order_id': order.id
    }).send(order.customer_id)

    subscription = order.get_subscription()
    service = search_models.Service.get_name(subscription.service)

    activation_code = None
    if subscription.is_code_required:
        activation_code = queries.get_activation_code(order.id)

    # TODO: Что если код активации не пришёл из базу

    await template.render(TEMPLATES / 'details.xml', {
        'order': order,
        'sub': subscription,
        'service': service,
        'activation_code': activation_code
    }).send(query.message.chat.id)


async def return_order_handler(query: CallbackQuery, callback_data: callbacks.OrderCallback):
    if not order_models.Order.is_taken_by(callback_data.order, query.from_user.id):
        await query.answer('Заказ может вернуть только взявший его оператор')
        return

    await query.message.delete()

    order_models.Order.return_to_queue(callback_data.order)

    await template.render(TEMPLATES / 'notify/returned.xml', {
        'operator_id': query.from_user.id,
        'order_id': callback_data.order
    }).send(callback_data.customer_id)

    await query.answer('Заказ успешно возвращён в очередь')


async def close_order_handler(query: CallbackQuery, callback_data: callbacks.OrderCallback):
    if not order_models.Order.is_taken_by(callback_data.order, query.from_user.id):
        await query.answer('Заказ может закрыть только взявший его оператор')
        return

    await query.message.delete()

    order_models.Order.close(callback_data.order, query.from_user.id)

    await template.render(TEMPLATES / 'notify/closed.xml', {
        'operator_id': query.from_user.id,
        'order_id': callback_data.order
    }).send(callback_data.customer_id)

    await query.answer('Заказ успешно закрыт')
