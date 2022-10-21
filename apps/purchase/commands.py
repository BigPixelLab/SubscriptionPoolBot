from aiogram import Router

from . import callbacks, handlers

router = Router()

router.callback_query(
    callbacks.BuySubscriptionCallback.filter()
)(handlers.buy_handler)

router.callback_query(
    callbacks.CheckBillCallback.filter()
)(handlers.check_bill_handler)

router.callback_query(
    callbacks.PosInQueueCallback.filter()
)(handlers.piq_update_handler)
