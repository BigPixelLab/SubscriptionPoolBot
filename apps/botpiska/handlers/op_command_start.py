import response_system as rs
import template


async def op_start_command_handler(_):
    """ ... """
    return rs.message(template.render('apps/botpiska/templates/op-message-start.xml', {}))


__all__ = ('op_start_command_handler',)
