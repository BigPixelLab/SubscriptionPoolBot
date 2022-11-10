import datetime
from pathlib import Path

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandObject
from aiogram.types import FSInputFile, Message

import gls
import settings
from apps.pool_bot import queries
from utils import database, template, file
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
    user_models.User.add_user_last_interaction(message.chat.id, datetime.datetime.now())
    services = queries.get_services_ordered_by_popularity()
    await template.render(TEMPLATES / 'intro.xml', {
        'services': services,
        'user': message.from_user
    }).send(message.chat.id)


async def update_resources_handler(message: Message, command: CommandObject):
    chat = message.chat.id
    bot = Bot.get_current()
    methods = {
        'document': (gls.bot.send_document, lambda m: m.document.file_id),
        'photo': (gls.bot.send_photo, lambda m: m.photo[0].file_id)
    }

    try:
        assert command.args is not None
        resources = [next(res for res in settings.UPDATE_RESOURCES if res.index == command.args)]
    except AssertionError:
        resources = settings.UPDATE_RESOURCES
    except StopIteration:
        await message.answer('No such resource.')
        return

    for i, resource in enumerate(resources):
        await gls.bot.send_message(chat, f'UPLOADING "{resource.name}" ({i + 1}/{len(resources)})...')
        send, extract = methods[resource.type]

        try:
            message = await send(chat, FSInputFile(resource.path, resource.name))
        except TelegramBadRequest:
            await gls.bot.send_message(chat, 'Failed to upload resource')
            continue

        file_id = extract(message)
        database.execute(
            f"""
                insert into "File" (bot_id, {resource.index})
                values (%(bot_id)s, %(file_id)s)
                on conflict (bot_id) do update set
                    {resource.index} = excluded.{resource.index}
            """,
            f'Updating {resource.index=} to {file_id=}',
            file_id=file_id,
            bot_id=bot.id
        )

        # Cache needs to be cleared for changes to be visible
        file.clear_cache(file_index=resource.index)

        await gls.bot.send_message(chat, f'file_id=<code>{file_id}</code>')

    await gls.bot.send_message(chat, 'Done.')


async def support_handler(message: Message):
    await template.render(TEMPLATES / 'support.xml', {
        'support': queries.get_support()
    }).send(message.chat.id)


async def terms_handler(message: Message):
    await template.render(TEMPLATES / 'terms.xml', {}).send(message.chat.id)
