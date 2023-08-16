""" ... """
import aiogram.types

import response_system as rs
import response_system_extensions as rse
from apps.seasons.models import Season


async def unhandled_callback_query(query: aiogram.types.CallbackQuery):
    """ ... """
    return rs.send(f'Unhandled query: {query.data}')


async def test_handler(_):
    prizes = Season.get_current().prizes
    print(prizes)
    # return rs.send(f'<code>{prizes}</code>')
    # return rse.tmpl_send('apps/debug/templates/test.xml', {'a': False, 'b': False})
