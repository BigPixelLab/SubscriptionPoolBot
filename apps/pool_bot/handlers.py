import datetime
from pathlib import Path

import aiogram.types

import settings
from apps.pool_bot import queries
from utils import database, template
from ..orders import models as order_models
from ..search import models as search_models

TEMPLATES = Path('apps/pool_bot/templates')


async def on_startup():
    """This command will run each time on startup. Hopefully everyday"""

    notify = database.fetch(order_models.Order, """
        select * from "Order" O
            join "Subscription" S on O.subscription = S.id
        where
            not O.is_cont_notified and 
            O.closed_at + S.duration - %(temp1)s <= %(temp2)s
    """, temp1=settings.NOTIFY_CUSTOMER_BEFORE_DAYS, temp2=datetime.datetime.now())

    for order in notify:
        subscription = search_models.Subscription.get(order.id)
        service = search_models.Service.get(subscription.id)

        await template.render(..., {
            'order': order,
            'subscription': subscription,
            'service': service
        }).send(order.customer_id)

    # notifications = database.fetch_rows("""
    #     select
    #         O.id,
    #         O."user",
    #         S.name,
    #         E.name
    #     from "Notification" N
    #         join "Order" O on O.id = N."order"
    #         join "Subscription" S on S.id = O.subscription
    #         join "Service" E on E.id = S.service
    #     where
    #         (N.created_at + S.duration - '3 days'::interval)::date <= %s
    # """, datetime.date.today())
    #
    # for order_id, customer, subscription, service in notifications:
    #     await gls.bot.send_photo(
    #         customer,
    #         'https://i.postimg.cc/0NkBYtzb/INTRO-BANNER.jpg',
    #         **template_.render('apps/notifications/templates/notification.html', {
    #             'order_id': order_id,
    #             'subscription': subscription,
    #             'service': service
    #         })
    #     )


async def command_start(message: aiogram.types.Message):
    services = queries.get_services_ordered_by_popularity()
    await template.render(TEMPLATES / 'intro.xml', {
        'services': services,
        'user': message.from_user
    }).send(message.chat.id)


async def support_handler(message: aiogram.types.Message):
    await template.render(TEMPLATES / 'support.xml', {
        'support': queries.get_support()
    }).send(message.chat.id)


async def terms_handler(message: aiogram.types.Message):
    await template.render(TEMPLATES / 'terms.xml', {}).send(message.chat.id)
