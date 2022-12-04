from aiogram.filters.callback_data import CallbackData


class OpenButtonCallback(CallbackData, prefix='lottery'):
    coupon: str
    banner_index: str
