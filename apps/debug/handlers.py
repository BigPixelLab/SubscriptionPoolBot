""" ... """
import aiogram.types

import response_system as rs


async def unhandled_callback_query(query: aiogram.types.CallbackQuery):
    """ ... """
    return rs.message(f'Unhandled query: {query.data}')
