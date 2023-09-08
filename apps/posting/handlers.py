import logging

import aiogram.types
import aiogram.exceptions
import peewee
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

import gls
import response_system as rs
import response_system_extensions as rse
import template
from apps.botpiska.models import Client
from apps.posting import callbacks, methods
from apps.posting.methods import generate_lottery_prize
from apps.posting.models import Lottery, LotteryPrize
from apps.posting.states import PostStates
from message_render import MessageRenderList
from template_for_aiogram.scopes import ELEMENT

logger = logging.getLogger(__name__)


async def post_command_handler(_, state: FSMContext):
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
    methods.remove_post(callback_data.reference_id)

    receivers = Client.get_all_chats()

    try:
        receivers.remove(0)
    except ValueError:
        pass

    def on_completion(succeeded, total):
        return gls.bot.send_message(user.id, f'Успешно отправлено: {succeeded} / {total}')

    return (
        rs.delete()
        + rs.notify(message, receivers, on_completion=on_completion)
    )


class NoLotteryFound(rs.UserFriendlyException):
    """ Лотереи с указанным id нет в базе """


async def lottery_command_handler(_, command: CommandObject):
    if command.args is None:
        return rs.feedback('Формат команды: <code>/lottery &lt;lottery_id&gt;</code>')

    try:
        lottery = Lottery.get_by_id(command.args)
    except peewee.DoesNotExist:
        raise NoLotteryFound(f'Лотереи {command.args} нет в базе')

    content = template.render_string(lottery.description, {
        'prizes': lottery.prizes
    }, syntax=ELEMENT)

    receivers = Client.get_all_chats()
    prize_generator = generate_lottery_prize(lottery.prizes, len(receivers))

    succeeded = 0

    for chat_id in receivers:
        messages: MessageRenderList = template.render('apps/posting/templates/message-lottery.xml', {
            'banner': lottery.banner,
            'content': content,
            'prize': next(prize_generator)
        })

        try:
            await messages.send(chat_id)
        except aiogram.exceptions.TelegramAPIError:
            pass
        else:
            succeeded += 1

    return rs.send(f'Отправлено {succeeded}/{len(receivers)}')


class LotteryPrizeNotFound(rs.UserFriendlyException):
    """ Приз лотереи не найден в базе """


async def lottery_open_button_handler(_, callback_data: callbacks.LotteryOpenCallback):
    try:
        prize = LotteryPrize.get_by_id(callback_data.prize_id)
    except peewee.DoesNotExist:
        return (
            rs.delete()
            + rs.feedback('Данная лотерея больше не действует')
        )

    return rse.tmpl_edit('apps/posting/templates/message-lottery-open.xml', {
        'prize': prize
    })
