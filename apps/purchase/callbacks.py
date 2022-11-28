from __future__ import annotations

import typing

from aiogram.filters.callback_data import CallbackData


class BuySubscriptionCallback(CallbackData, prefix='buy'):
    sub_id: int


class TermsCallback(CallbackData, prefix='terms'):
    service_term: str


class CheckBillCallback(CallbackData, prefix='check_bill'):
    bill_id: str

    # Passing service and subscription names to avoid unnecessary database queries
    sub_id: int
    coupon: typing.Optional[str]


class PosInQueueCallback(CallbackData, prefix='piq_update'):
    order_id: int
