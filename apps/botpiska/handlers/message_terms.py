""" ... """
import response_system_extensions as rse


async def terms_message_handler(_):
    """ ... """
    return rse.tmpl_send('apps/botpiska/templates/message-terms.xml', {})


__all__ = ('terms_message_handler',)
