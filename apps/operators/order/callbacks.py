from aiogram.filters.callback_data import CallbackData


class OrderCallback(CallbackData, prefix='order'):
    action: str
    order: int

    # Customer is part of the "Order" table.
    # Sending it separately to save on call
    # to the database
    customer: int
