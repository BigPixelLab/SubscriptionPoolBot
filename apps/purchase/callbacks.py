from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class BuySubscriptionCallback(CallbackData, prefix='buy'):
    sub_id: int


class CheckBillCallback(CallbackData, prefix='check_bill'):
    bill_id: str

    # Passing service and subscription names to avoid unnecessary database queries
    sub_id: int
    coupon: str | None


class PosInQueueCallback(CallbackData, prefix='piq_update'):
    order_id: int
