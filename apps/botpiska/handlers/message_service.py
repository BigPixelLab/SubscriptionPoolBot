""" ... """
import itertools

import response_system_extensions as rse
from ..models import Subscription
from ..services import Service


async def service_message_handler(_, service: Service):
    """ ... """

    # Получаем список подписок данного сервиса в нужном порядке
    subscriptions = []
    if service.has_subscription_plans:
        subscriptions = Subscription.select_service_plans(service.id).execute()

    subscription_plans = _pair_with_calculated_discounts(subscriptions)
    return (
        rse.tmpl_send('apps/botpiska/templates/message-search-exact.xml', {})
        + rse.tmpl_send(service.showcase_template, {
            'subscription_plans': subscription_plans
        })
    )


def _pair_with_calculated_discounts(subscriptions: list[Subscription]) \
        -> list[tuple[Subscription, int]]:
    """ Рассчитывает скидку. Подписки должны быть предоставлены
       в отсортированном по группе виде """

    discounts = []

    for group, group_subscriptions in itertools.groupby(subscriptions, key=lambda x: x.category):
        # groupby возвращает итератор, сохраняем значения
        # в список, чтобы можно было пройтись повторно
        group_subscriptions = list(group_subscriptions)

        # Если в группе одна подписка, считать скидку не
        # имеет смысла
        if len(group_subscriptions) == 1:
            subscription, = group_subscriptions
            discounts.append((subscription, None))
            continue

        # Обычно, чем короче продолжительность подписки,
        # тем больше её месячная цена, находим самую
        # короткую подписку в группе
        reference = min(group_subscriptions, key=lambda x: x.duration)

        for subscription in group_subscriptions:
            portion = subscription.monthly_price / reference.monthly_price * 100
            discounts.append((subscription, 100 - int(portion)))

    return discounts


__all__ = (
    'service_message_handler',
)
