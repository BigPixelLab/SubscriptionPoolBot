import gls
import response_system_extensions as rse
from apps.order_processing import callbacks


async def send_text_handler(_, callback_data: callbacks.SendTextCallback):
    """ ... """
    return rse.tmpl_send(
        'apps/order_processing/templates/op-message-profile-private.xml', {},
        chat=callback_data.chat_id,
        bot=gls.bot
    )


__all__ = ('send_text_handler',)
