import gls
import response_system as rs
import template
from apps.order_processing import callbacks


async def send_text_handler(_, callback_data: callbacks.SendTextCallback):
    """ ... """
    return rs.notify(
        template.render('apps/order_processing/templates/op-message-profile-private.xml', {}),
        [callback_data.chat_id],
        bot=gls.bot
    )


__all__ = ('send_text_handler',)
