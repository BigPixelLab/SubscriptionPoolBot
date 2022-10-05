from aiogram import Router

from . import callbacks, handlers

router = Router()

router.callback_query(callbacks.BuySubscriptionCallback.filter())(handlers.buy_handler)
