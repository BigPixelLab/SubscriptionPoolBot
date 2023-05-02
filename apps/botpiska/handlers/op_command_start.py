import response_system_extensions as rse


async def op_start_command_handler(_):
    """ ... """
    return rse.tmpl_send('apps/botpiska/templates/op-message-start.xml', {})


__all__ = ('op_start_command_handler',)
