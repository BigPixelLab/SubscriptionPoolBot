import aiogram
from aiogram.filters import ContentTypesFilter
from aiogram.types import ContentType

from . import handlers

router = aiogram.Router()

# Search text
router.message(ContentTypesFilter(
    content_types=[ContentType.TEXT]
))(handlers.search_handler)

# # User chose to see subscription list
# router.callback_query(
#     callbacks.ShowMoreCallback.filter()
# )(handlers_.show_more_callback)
#
# # User purchased product
# router.pre_checkout_query()(handlers_.payment_verification_handler)
#
# router.message(ContentTypesFilter(
#     content_types=[ContentType.SUCCESSFUL_PAYMENT]
# ))(handlers_.successful_payment_handler)
#
# # User updates queue status
# router.callback_query(
#     callbacks.UpdateConfirmationCallback.filter()
# )(handlers_.update_confirmation_handler)
