from __future__ import annotations

import datetime
from pathlib import Path

from aiogram.types import CallbackQuery

import gls
from utils import database, template_
from . import callbacks

TEMPLATES = Path('apps/operator/order/templates')


async def take_top_order_handler(query: CallbackQuery):
    order = database.single_row("""
        select id, customer_id from "Order"
        where processed_by is null and closed_at is null
        order by created_at limit 1
    """)

    if order is None:
        await query.answer('Нет активных заказов')
        return

    order_id, customer = order

    take_order(order_id, query.from_user.id)

    await gls.bot.send_message(
        customer,
        **render_notification(
            TEMPLATES / 'taken_notification.html',
            order_id,
            query.from_user.id
        )
    )

    await query.message.answer(**render_order_details(order_id))
    await query.answer()


async def take_specific_order_handler(query: CallbackQuery, callback_data: callbacks.OrderCallback):
    take_order(callback_data.order, query.from_user.id)
    await gls.bot.send_message(
        callback_data.customer,
        **render_notification(
            TEMPLATES / 'taken_notification.html',
            callback_data.order,
            query.from_user.id
        )
    )
    await query.message.answer(**render_order_details(callback_data.order))
    await query.answer()


async def return_order_handler(query: CallbackQuery, callback_data: callbacks.OrderCallback):
    if not is_taken_by(callback_data.order, query.from_user.id):
        await query.answer('Заказ может вернуть только взявший его оператор')
    await query.message.delete()
    return_order(callback_data.order)
    await gls.bot.send_message(
        callback_data.customer,
        **render_notification(
            TEMPLATES / 'returned_notification.html',
            callback_data.order,
            query.from_user.id
        )
    )
    await query.answer('Заказ успешно возвращён в очередь')


async def close_order_handler(query: CallbackQuery, callback_data: callbacks.OrderCallback):
    if not is_taken_by(callback_data.order, query.from_user.id):
        await query.answer('Заказ может закрыть только взявший его оператор')
    await query.message.delete()
    close_order(callback_data.order, query.from_user.id)
    await gls.bot.send_message(
        callback_data.customer,
        **render_notification(
            TEMPLATES / 'closed_notification.html',
            callback_data.order,
            query.from_user.id
        )
    )
    await query.answer('Заказ успешно закрыт')


def render_order_details(order: int):
    (
        order_id, order_total, customer, taken_by, created_at, closed_at,
        sub_name, sub_length, sub_price,
        service,
        activation_code
    ) = database.single_row("""
        select
            O.id, O.total, O.customer_id, O.processed_by, O.created_at, O.closed_at,
            S.name, S.duration, S.price,
            E.name,
            AC.code
        from "Order" as O
            join "Subscription" S on S.id = O.subscription
            join "Service" E on E.id = S.service
            join "ActivationCodes" AC on AC.linked_order = O.id
        where O.id = %(order)s
    """, order=order)

    _customer = f'<a href="tg://openmessage?user_id={customer}">КЛИЕНТ</a>'

    _taken_by = f'<a href="tg://openmessage?user_id={taken_by}">ОПЕРАТОР</a>'\
        if taken_by else '<u>нет</u>'

    return template_.render(TEMPLATES / 'details.html', {
        'order_id': order_id,
        'order_total': order_total,
        'customer': _customer,
        'taken_by': _taken_by,
        'created_at': created_at.strftime('%x %X'),
        'closed_at': closed_at.strftime('%x %X') if closed_at else 'нет',
        'sub_name': sub_name,
        'sub_length': sub_length.days,
        'sub_price': sub_price,
        'service': service.upper(),
        'activation_code': activation_code if activation_code else 'нет',

        'Вернуть': {'callback_data': callbacks.OrderCallback(
            action='return',
            order=order,
            customer=customer
        )},
        'Закрыть': {'callback_data': callbacks.OrderCallback(
            action='close',
            order=order,
            customer=customer
        )}
    })


def render_notification(path, order: int, operator: int):
    return template_.render(path, {
        'order': order,
        'operator': operator,

        'Ок.': {'callback_data': 'remove-message'}
    })


def take_order(order: int, operator: int):
    database.execute("""
        update "Order" set
            processed_by = %s
        where id = %s
    """, operator, order)


def close_order(order: int, operator: int):
    database.execute("""
        update "Order" set
            processed_by = %s,
            closed_at = %s
        where id = %s
    """, operator, datetime.datetime.now(), order)


def is_taken_by(order: int, operator: int):
    result = database.single_value("""
        select count(*) from "Order"
        where id = %s and processed_by = %s
    """, order, operator)
    return bool(result)


def return_order(order: int):
    database.execute("""
        update "Order" set
            processed_by = null
        where id = %s
    """, order)
