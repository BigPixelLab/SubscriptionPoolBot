from aiogram.filters.callback_data import CallbackData


class OrderGetUnprocessedCallback(CallbackData, prefix="order-get-unprocessed"):
    pass


class OrderActions:
    VIEW = 'view'
    TAKE = 'take'
    RETURN = 'return'
    CLOSE = 'close'


class OrderActionCallback(CallbackData, prefix="order"):
    action: str
    order_id: int


class SendTextCallback(CallbackData, prefix="send-text"):
    chat_id: int


class OrderListUpdateCallback(CallbackData, prefix="order-list-update"):
    pass
