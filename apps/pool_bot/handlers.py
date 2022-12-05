import datetime
from pathlib import Path

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import CommandObject
from aiogram.types import FSInputFile, Message

import gls
import posts
import resources
import settings
from apps.pool_bot import queries
from utils import database, template
import utils.misc
from ..orders import models as order_models
from ..search import models as search_models
from ..user_account import models as user_models

TEMPLATES = Path('apps/pool_bot/templates')


async def on_startup():
    """This command will run each time on startup. Hopefully everyday"""

    notify = database.fetch(
        order_models.Order,
        """
            update "Order" set
                is_cont_notified = true
            where id = (
                select O.id from "Order" O
                    join "Subscription" S on O.subscription = S.id
                where
                    not O.is_cont_notified and 
                    O.closed_at + S.duration - %(interval)s <= %(now)s
            )
            returning *
        """,
        'Getting orders that need to be notified',
        interval=settings.NOTIFY_CUSTOMER_BEFORE_DAYS,
        now=datetime.datetime.now()
    )

    for order in notify:
        subscription = search_models.Subscription.get(order.subscription)
        service = search_models.Service.get(subscription.service)

        await template.render(TEMPLATES / 'notification.xml', {
            'order': order,
            'subscription': subscription,
            'service': service
        }).send(order.customer_id, bot=gls.bot)


async def command_start(message: Message):
    user_models.User.set_user_last_interaction(message.chat.id, datetime.datetime.now())
    services = queries.get_services_ordered_by_popularity()
    await template.render(TEMPLATES / 'intro.xml', {
        'services': services,
        'user': message.from_user
    }).send(message.chat.id)


async def post_handler(message: Message, command: CommandObject):
    """ /post <index>[ chat1 chat2 ...] """
    post_index, *chats = command.args.split()
    post: posts.Post = posts.POSTS_INDEX_MAP.get(post_index)

    if post is None:
        await message.answer('❌ Введено неверное название события. '
                             'Попробуйте ещё раз')
        return

    if chats:
        chats = list(map(int, chats))
    elif chats == ['me']:
        chats = [message.from_user.id]
    else:
        chats = user_models.User.get_all()

    successes = 0
    for chat, render in post.prepared(chats):  # type: int, template.MessageRenderList
        try:
            await render.send(chat, silence_errors=False)
            successes += 1
        except (TelegramBadRequest, TelegramForbiddenError) as error:
            print(error)
    else:
        await message.answer(f'✔ Пост отправлен успешно, получателей: '
                             f'{successes}/{len(chats)}')


async def update_resources_handler(message: Message, command: CommandObject):
    chat = message.chat.id
    bot = Bot.get_current()
    methods = {
        # ResourceType: (send_file_method, extract_file_id_method)
        resources.ResourceType.DOCUMENT: (
            gls.bot.send_document,
            lambda m: m.document.file_id
        ),
        resources.ResourceType.PHOTO: (
            gls.bot.send_photo,
            lambda m: m.photo[0].file_id
        )
    }

    if command.args is None:
        _resources = resources.UPLOADED_RESOURCES
    elif res := utils.misc.find(command.args, resources.UPLOADED_RESOURCES, key=lambda x: x.index):
        _resources = [res]
    else:
        await message.answer('No such resource.')
        return

    for i, res in enumerate(_resources):
        await gls.bot.send_message(chat, f'UPLOADING "{res.name}" ({i + 1}/{len(_resources)})...')
        send, extract = methods[res.type]

        try:
            message = await send(chat, FSInputFile(res.path, res.name))
        except (TelegramBadRequest, TelegramForbiddenError):
            await gls.bot.send_message(chat, 'Failed to upload resource')
            continue

        file_id = extract(message)
        resources.update(res.index, file_id, key=bot.id)

        await gls.bot.send_message(chat, f'file_id=<code>{file_id}</code>')

    await gls.bot.send_message(chat, 'Done.')


async def support_handler(message: Message):
    await template.render(TEMPLATES / 'support.xml', {
        'support': queries.get_support()
    }).send(message.chat.id)


async def terms_handler(message: Message):
    await template.render(TEMPLATES / 'terms.xml', {}).send(message.chat.id)


async def send_message_handler(message: Message, command: CommandObject):
    try:
        chat_id = int(command.args)
    except ValueError:
        await message.answer('Число нада')
        return

    try:
        await gls.bot.send_message(
            chat_id,
            "Привет! У тебя приватный профиль, поэтому мы не можем "
            "тебе написать сами. Пожалуйста напиши нашему оператору "
            "@dshuryshkin"
        )
    except TelegramBadRequest:
        await message.answer('Лох, чат не верный')
