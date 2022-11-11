from pathlib import Path

from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandObject

from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from ...user_account import models as user_models

import settings
from apps.operator.control_panel import queries
from utils import template
from utils.feedback import send_feedback

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


async def send_mailing(message: Message, command: CommandObject):
    post_template = settings.POST_TEMPLATES.get(command.args)
    if post_template is None:
        await send_feedback('Введено неверное название события. Попробуйте ещё раз', message.chat.id)
        return

    render = template.render(post_template, {}).first()
    users = user_models.User.get_users()
    for user in users:
        with suppress(TelegramBadRequest, TelegramForbiddenError):
            await render.send(user)
