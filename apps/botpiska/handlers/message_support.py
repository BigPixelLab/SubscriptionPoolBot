""" ... """
import response_system as rs
import template


async def support_message_handler(_):
    """ ... """
    return rs.message(template.render('apps/botpiska/templates/message-support.xml', {}))


__all__ = ('support_message_handler',)
