""" ... """
import response_system_extensions as rse


async def support_message_handler(_):
    """ ... """
    return rse.tmpl_send('apps/botpiska/templates/message-support.xml', {})


__all__ = ('support_message_handler',)
