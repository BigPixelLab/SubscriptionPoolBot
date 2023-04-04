""" ... """
import response_system as rs
import template


async def terms_message_handler(_):
    """ ... """
    return rs.message(template.render('apps/botpiska/templates/message-terms.xml', {}))


__all__ = ('terms_message_handler',)
