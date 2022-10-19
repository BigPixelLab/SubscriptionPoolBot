from dataclasses import dataclass

from aiogram import Router
from aiogram.types import CallbackQuery

from . import callbacks, handlers

router = Router()

router.callback_query(
    callbacks.BuySubscriptionCallback.filter()
)(handlers.buy_handler)


def check_substitution(query: CallbackQuery):
    @dataclass
    class Amount:
        value: int

    @dataclass
    class Bill:
        amount: Amount

    return {'bill': Bill(Amount(500))}


# router.callback_query(
#     callbacks.CheckBillCallback.filter()
# )(handlers.check_bill_handler)

router.callback_query(
    callbacks.CheckBillCallback.filter(),
    check_substitution
)(handlers.bill_paid_handler)

router.callback_query(
    callbacks.PosInQueueCallback.filter()
)(handlers.piq_update_handler)
