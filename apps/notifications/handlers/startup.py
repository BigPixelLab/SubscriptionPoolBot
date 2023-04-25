import contextlib
import datetime

import aiogram.exceptions
import peewee

import gls
import settings
import template
from apps.botpiska.models import Subscription
from apps.botpiska.services import SERVICE_MAP, Service


async def startup_handler():
    """ ... """

    query = """
        UPDATE "Order" AS O SET
            notified_renew = True
        FROM "Subscription" AS S
        WHERE O.subscription_id = S.id
            AND NOT O.notified_renew
            AND O.closed_at IS NOT NULL
            AND %(now)s >= O.closed_at + S.duration - %(notify_before)s
        RETURNING O.client_id, O.subscription_id
    """
    args = {
        'notify_before': settings.NOTIFY_BEFORE,
        'now': datetime.datetime.now()
    }

    chats_to_notify = gls.db.execute_sql(query, args)

    notified, total = 0, 0
    for chat_id, subscription_id in chats_to_notify:
        try:
            subscription = Subscription.get_by_id(subscription_id)
        except peewee.DoesNotExist:
            continue

        try:
            service: Service = SERVICE_MAP[subscription.service_id]
        except KeyError:
            continue

        featured_id = service.featured_subscription_id
        featured = None

        if featured_id != subscription_id:
            with contextlib.suppress(peewee.DoesNotExist):
                featured = Subscription.get_by_id(featured_id)

        message = template.render('apps/notifications/templates/message-renew.xml', {
            'subscription': subscription,
            'featured': featured
        })

        with contextlib.suppress(aiogram.exceptions.AiogramError):
            await message.send(chat_id, bot=gls.bot)
            notified += 1
        total += 1

    print(f'Оповещено о продлении {notified}/{total}')

    if not total:
        return

    with contextlib.suppress(aiogram.exceptions.AiogramError):
        await gls.operator_bot.send_message(
            settings.TECH_SUPPORT_CHAT_ID,
            f'Оповещено о продлении {notified}/{total}'
        )


__all__ = ('startup_handler',)
