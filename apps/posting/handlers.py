import logging

import aiogram.types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

import gls
import response_system as rs
import response_system_extensions as rse
from apps.botpiska.models import Client
from apps.posting import callbacks, methods
from apps.posting.states import PostStates

logger = logging.getLogger(__name__)


async def post_handler_command(_, state: FSMContext):
    await state.set_state(PostStates.WAITING_FOR_POST)
    return rse.tmpl_send('apps/posting/templates/message-post-request.xml', {})


async def post_received_handler(message: aiogram.types.Message, state: FSMContext):
    await state.set_state(default_state)

    key = methods.load_post(message)
    return rse.tmpl_send('apps/posting/templates/message-post-received.xml', {
        'reference_id': key
    })


async def post_button_handler(_, user: aiogram.types.User, callback_data: callbacks.PostCallback) -> rs.Response:
    message = methods.get_post(callback_data.reference_id)
    receivers = Client.get_all_chats()

    def on_completion(succeeded, total):
        return gls.bot.send_message(user.id, f'Успешно отправлено: {succeeded} / {total}')

    return (
        rs.delete()
        + rs.notify(message, receivers, on_completion=on_completion)
    )
