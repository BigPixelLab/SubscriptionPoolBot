from pathlib import Path

from aiogram.types import Message, CallbackQuery

import settings
from apps.operator.control_panel import queries
from utils import template

TEMPLATES = Path('apps/operator/control_panel/templates')


async def show_operator_panel_handler(message: Message):
    top_orders = queries.get_top_open_orders(settings.OP_PANEL_ORDERS_LIMIT)
    orders_count, total_count = queries.get_orders_count()
    await template.render(TEMPLATES / 'control_panel.xml', {
        'count': orders_count,
        'total_count': total_count,
        'orders': top_orders
    }).send(message.chat.id)


async def update_operator_panel_handler(query: CallbackQuery):
    top_orders = queries.get_top_open_orders(settings.OP_PANEL_ORDERS_LIMIT)
    orders_count, total_count = queries.get_orders_count()
    await template.render(TEMPLATES / 'control_panel.xml', {
        'count': orders_count,
        'total_count': total_count,
        'orders': top_orders
    }).first().edit(query.message)
    await query.answer('Панель оператора обновлена')
