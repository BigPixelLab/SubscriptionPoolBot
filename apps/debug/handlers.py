""" ... """
import aiogram.types

import response_system as rs
import response_system_extensions as rse


async def unhandled_callback_query(query: aiogram.types.CallbackQuery):
    """ ... """
    return rs.send(f'Unhandled query: {query.data}')


async def test_handler(_):
    return rse.tmpl_send('apps/debug/templates/test.xml', {'a': 5})
