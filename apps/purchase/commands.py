from aiogram import Router, F

from . import callbacks, handlers

router = Router()

router.callback_query(
    callbacks.BuySubscriptionCallback.filter()
)(handlers.purchase_handler)

router.callback_query(
    callbacks.TermsCallback.filter()
)(handlers.service_terms_handler)

router.callback_query(
    F.data == 'delete'
)(handlers.delete_term_message_handler)

router.callback_query(
    callbacks.CheckBillCallback.filter()
)(handlers.done_button_handler)

router.callback_query(
    callbacks.PosInQueueCallback.filter()
)(handlers.position_in_queue_update_handler)
