from aiogram.filters.callback_data import CallbackData


class BuySubscriptionCallback(CallbackData, prefix='buy'):
    sub_id: int
