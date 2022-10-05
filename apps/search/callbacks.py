import typing

from aiogram.filters.callback_data import CallbackData


class SubscriptionPayload(CallbackData, prefix='sub'):
    subscription: int
    coupon: typing.Optional[str]
    total: int


class ShowMoreCallback(CallbackData, prefix='show_more'):
    service_id: int


class UpdateConfirmationCallback(CallbackData, prefix='upd_conf'):
    order_id: int
