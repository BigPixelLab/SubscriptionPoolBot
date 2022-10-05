from pathlib import Path

import settings
from . import queries
from utils import template

TEMPLATES = Path('apps/operators/control_panel/templates')


def render_operator_panel():
    top_orders = queries.get_top_open_orders(settings.OP_PANEL_ORDERS_LIMIT)

    top_orders_rendered = [
        template.render_as_text('apps/operators/order/templates/preview.html', {
            'id': order_info.order_id,
            'date': order_info.created_at.strftime('%x %X'),
            'service': order_info.service.upper(),
            'subscription': order_info.subscription,
            'price': order_info.sub_price,
            'taken': 'taken' * order_info.is_taken
        })
        for order_info in top_orders
    ]

    if not top_orders_rendered:
        top_orders_rendered = ['Нет активных заказов.']

    return template.render(TEMPLATES / 'panel.html', {
        'count': queries.get_total_orders(),
        'orders': '\n'.join(top_orders_rendered),

        'Обновить': {'callback_data': 'opp:update'},
        'Взять заказ': {'callback_data': 'order:take_top'}
    })
