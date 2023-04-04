""" ... """
import aiogram.types

import response_system as rs
import template
from template.syntax.telegram import TELEGRAM


async def unhandled_callback_query(query: aiogram.types.CallbackQuery):
    """ ... """
    return rs.message(f'Unhandled query: {query.data}')


async def test_command_handler(message: aiogram.types.Message):
    render = template.render('apps/debug/templates/new_templater_test.xml', {}, syntax=TELEGRAM)
    return rs.message(render)
