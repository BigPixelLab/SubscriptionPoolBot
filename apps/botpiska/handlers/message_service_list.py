import response_system as rs
import response_system_extensions as rse


async def service_list_message_handler(_) -> rs.Response:
    return rse.tmpl_send('apps/botpiska/templates/message-service-list.xml', {})


__all__ = ('service_list_message_handler',)
