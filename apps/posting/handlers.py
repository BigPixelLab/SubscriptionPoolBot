import uuid

import aiogram.types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

import response_system as rs
import response_system_extensions as rse
import userdata
from apps.botpiska.models import Client
from apps.posting import callbacks
from apps.posting.states import PostStates
from message_render import MessageRender


async def post_handler_command(_, state: FSMContext):
    await state.set_state(PostStates.WAITING_FOR_POST)
    return rse.tmpl_send('apps/posting/templates/message-post-request.xml', {})


async def post_received_handler(message: aiogram.types.Message, user: aiogram.types.User, state: FSMContext):
    await state.set_state(default_state)

    stored_messages, = await userdata.get_data(user.id, ['stored_messages'])
    stored_messages = stored_messages or {}

    message_key = uuid.uuid4()
    stored_messages[message_key] = message

    await userdata.set_data(user.id, {'stored_messages': stored_messages})

    return rse.tmpl_send('apps/posting/templates/message-post-received.xml', {
        'reference_id': message_key
    })


async def post_button_handler(_, user: aiogram.types.User, callback_data: callbacks.PostCallback) -> rs.Response:
    stored_messages, = await userdata.get_data(user.id, ['stored_messages'])
    stored_messages = stored_messages or {}

    reference: aiogram.types.Message = stored_messages.get(callback_data.reference_id)
    if reference is None:
        return rs.no_response()

    message = MessageRender(
        reference.text or reference.caption,
        photo=reference.photo[0].file_id if reference.photo else None,
        animation=reference.animation.file_id if reference.animation else None
    )

    return (
        rs.delete()
        + rs.notify(message, Client.get_all_chats())
    )
