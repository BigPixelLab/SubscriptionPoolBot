"""
Callbacks:
  - order-list-update
  - order-get-unprocessed
  - order:view:<order-id>
  - order:take:<order-id>
  - order:return:<order-id>
  - order:close:<order-id>
  - send-text:<chat-id>

Commands:
  - /view <oder-id>

Messages:
  - Список заказов

"""
import aiogram
from aiogram import F
from aiogram.filters import Command

from . import handlers, callbacks

op_order_processing_router = aiogram.Router()

# Оператор ввёл "Список Заказов"
op_order_processing_router.message(
    F.text.lower() == "список заказов"
)(handlers.get_orders_handler)

# Обновление списка заказов (order-list-update)
op_order_processing_router.callback_query(
    callbacks.OrderListUpdateCallback.filter()
)(handlers.update_orders_handler)

# Список необработанных заказов (order-get-unprocessed)
op_order_processing_router.callback_query(
    callbacks.OrderGetUnprocessedCallback.filter()
)(handlers.get_unprocessed_order_handler)

# Просмотр заказа командой (/view <order-id>)
op_order_processing_router.message(
    Command(commands=['view']),
)(handlers.view_command_handler)

# Просмотр заказа (order:view:<order-id>)
# noinspection PyTypeChecker
op_order_processing_router.callback_query(
    callbacks.OrderActionCallback.filter(F.action == callbacks.OrderActions.VIEW)
)(handlers.view_order_handler)

# Взятие заказа в обработку (order:take:<order-id>)
# noinspection PyTypeChecker
op_order_processing_router.callback_query(
    callbacks.OrderActionCallback.filter(F.action == callbacks.OrderActions.TAKE)
)(handlers.take_order_handler)

# Возврат заказа в очередь (order:return:<order-id>)
# noinspection PyTypeChecker
op_order_processing_router.callback_query(
    callbacks.OrderActionCallback.filter(F.action == callbacks.OrderActions.RETURN)
)(handlers.return_order_handler)

# Закрытие заказа (order:close:<order-id>)
# noinspection PyTypeChecker
op_order_processing_router.callback_query(
    callbacks.OrderActionCallback.filter(F.action == callbacks.OrderActions.CLOSE)
)(handlers.close_order_handler)

# Просьба пользователю отправить сообщение первым (send-text:<chat-id>)
# noinspection PyTypeChecker
op_order_processing_router.callback_query(
    callbacks.SendTextCallback.filter()
)(handlers.send_text_handler)
