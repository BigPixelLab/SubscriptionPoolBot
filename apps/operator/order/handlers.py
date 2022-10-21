from pathlib import Path

from aiogram.types import CallbackQuery, Message

from aiogram.filters import CommandObject

from utils import template
from . import callbacks
from ...orders import models as order_models
from ...search import models as search_models
from ...purchase import models as purchase_models

TEMPLATES = Path('apps/operator/order/templates')


async def view_order_by_id_handler(message: Message, command: CommandObject):
    try:
        order_id = int(command.args)
    except ValueError:
        await template.render(TEMPLATES / 'help/view.xml', {}).send(message.from_user.id)
        return

    order = order_models.Order.get(order_id)

    if not order:
        await message.answer(f'Заказ #{order_id} не найден')
        return

    await order_handler(
        message.chat.id,
        message.from_user.id,
        order,
        take_order=False
    )


async def take_order_by_id_handler(message: Message, command: CommandObject):
    try:
        order_id = int(command.args)
    except ValueError:
        await template.render(TEMPLATES / 'help/take.xml', {}).send(message.from_user.id)
        return

    order = order_models.Order.get(order_id)

    if not order:
        await message.answer(f'Заказ #{order_id} не найден')
        return

    if order.processed_by is not None:
        await message.answer(f'Заказ #{order_id} уже обрабатывается другим оператором')
        return

    await order_handler(
        message.chat.id,
        message.from_user.id,
        order,
        take_order=True
    )


async def take_top_order_handler(query: CallbackQuery):
    order = order_models.Order.get_top()

    if not order:
        await query.answer('Нет активных заказов')
        return

    await order_handler(
        query.message.chat.id,
        query.from_user.id,
        order,
        take_order=True
    )

    await query.answer()


async def order_handler(chat_id: int, user_id: int, order: order_models.Order, *, take_order: bool):
    if take_order:
        order_models.Order.mark_as_taken(order.id, user_id)
        # Instances are not updated automatically, so setting attribute
        # manually to avoid executing another database query
        order.processed_by = user_id

        await template.render(TEMPLATES / 'notify/taken.xml', {
            'operator_id': user_id,
            'order_id': order.id
        }).send(order.customer_id)

    subscription = order.get_subscription()
    service = search_models.Service.get_name(subscription.service)

    activation_code = None
    if subscription.is_code_required:
        activation_code = purchase_models.ActivationCode.get_linked(order.id)

    render = template.render(TEMPLATES / 'details.xml', {
        'order': order,
        'sub': subscription,
        'service': service,
        'activation_code': activation_code,
        'is_activation_code_error': subscription.is_code_required and not activation_code
    }).first()

    if not take_order:
        render.keyboard = None

    await render.send(chat_id)


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
