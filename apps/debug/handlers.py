""" ... """
import aiogram.types

import response_system as rs


async def unhandled_callback_query(query: aiogram.types.CallbackQuery):
    """ ... """
    return rs.send(f'Unhandled query: {query.data}')
