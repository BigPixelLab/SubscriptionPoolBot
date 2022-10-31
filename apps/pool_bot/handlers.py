import datetime
from pathlib import Path

import aiogram.types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile

import gls
import settings
from apps.pool_bot import queries
from utils import database, template
from ..orders import models as order_models
from ..search import models as search_models

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


async def command_start(message: aiogram.types.Message):
    services = queries.get_services_ordered_by_popularity()
    await template.render(TEMPLATES / 'intro.xml', {
        'services': services,
        'user': message.from_user
    }).send(message.chat.id)


async def update_resources_handler(message: aiogram.types.Message):
    chat = message.chat.id
    methods = {
        'document': (gls.bot.send_document, lambda m: m.document.file_id),
        'photo': (gls.bot.send_photo, lambda m: m.photo[0].file_id)
    }

    for i, (_type, path, name, query) in enumerate(settings.UPDATE_RESOURCES):
        await gls.bot.send_message(chat, f'UPLOADING "{name}" ({i + 1}/{len(settings.UPDATE_RESOURCES)})...')
        send, extract = methods[_type]

        try:
            message = await send(chat, FSInputFile(path, name))
        except TelegramBadRequest:
            await gls.bot.send_message(chat, 'Failed to upload resource')
            continue

        file_id = extract(message)

        if query:
            database.execute(query, query % {'file_id': file_id}, file_id=file_id)

        await gls.bot.send_message(chat, f'<code>{file_id}</code>')

    await gls.bot.send_message(chat, 'Done.')


async def support_handler(message: aiogram.types.Message):
    await template.render(TEMPLATES / 'support.xml', {
        'support': queries.get_support()
    }).send(message.chat.id)


async def terms_handler(message: aiogram.types.Message):
    await template.render(TEMPLATES / 'terms.xml', {}).send(message.chat.id)
