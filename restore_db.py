import datetime
import decimal

import peewee

import gls
import settings

db = peewee.PostgresqlDatabase(settings.DATABASE_URI)


class BaseModel(peewee.Model):
    """ Базовая модель """

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        database = db


gls.BaseModel = BaseModel


class Action:
    def __init__(self, prompt: str):
        self.prompt = prompt

    def __enter__(self):
        print(f'{self.prompt}...', end=' ', flush=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print('', flush=True)
            return
        print('Done.', flush=True)


# DATABASE CONTENTS -------------------------------------------------
from apps.botpiska import models as models_botpiska
from apps.coupons import models as models_coupons
from apps.maintenance import models as models_maintenance

with Action('Creating tables'):
    # Должно быть 8
    db.create_tables([
        models_botpiska.Subscription,
        models_botpiska.Client,
        models_botpiska.Employee,
        models_coupons.SubscriptionGroup,
        models_coupons.SubscriptionGroupToSubscription,
        models_coupons.Coupon,
        models_botpiska.Order,
        models_botpiska.Bill,
        models_maintenance.Resource
    ])

with Action('Adding subscriptions'):
    subscriptions = [
        models_botpiska.Subscription(
            id='netflix_4k_1m',
            service_id='netflix',
            title='NETFLIX 4K 30 дней',
            short_title='4K 30 дней',
            order_template='apps/botpiska/templates/services/netflix/order-default.xml',
            duration=datetime.timedelta(days=30),
            price=decimal.Decimal('999.00'),
            is_queuing_required=True,
            group='4k'
        ),
        models_botpiska.Subscription(
            id='netflix_HD_1m',
            service_id='netflix',
            title='NETFLIX HD 30 дней',
            short_title='HD 30 дней',
            order_template='apps/botpiska/templates/services/netflix/order-default.xml',
            duration=datetime.timedelta(days=30),
            price=decimal.Decimal('699.00'),
            is_queuing_required=True,
            group='HD'
        ),
        models_botpiska.Subscription(
            id='spotify_ind_1m',
            service_id='spotify',
            title='SPOTIFY 1 месяц',
            short_title='1 месяц',
            order_template='apps/botpiska/templates/services/spotify/order-default.xml',
            duration=datetime.timedelta(days=30),
            price=decimal.Decimal('199.00')
        ),
        models_botpiska.Subscription(
            id='spotify_ind_3m',
            service_id='spotify',
            title='SPOTIFY 3 месяца',
            short_title='3 месяца',
            order_template='apps/botpiska/templates/services/spotify/order-default.xml',
            duration=datetime.timedelta(days=30 * 3),
            price=decimal.Decimal('549.00')
        ),
        models_botpiska.Subscription(
            id='spotify_ind_6m',
            service_id='spotify',
            title='SPOTIFY 6 месяцев',
            short_title='6 месяцев',
            order_template='apps/botpiska/templates/services/spotify/order-default.xml',
            duration=datetime.timedelta(days=30 * 6),
            price=decimal.Decimal('999.00')
        ),
        models_botpiska.Subscription(
            id='spotify_ind_1y',
            service_id='spotify',
            title='SPOTIFY 1 год',
            short_title='1 год',
            order_template='apps/botpiska/templates/services/spotify/order-default.xml',
            duration=datetime.timedelta(days=30 * 12),
            price=decimal.Decimal('1499.00'),
            is_special_offer=True
        ),
    ]

    for subscription in subscriptions:
        # force_insert чтобы peewee понял, что значение необходимо
        # именно добавить в таблицу, а не обновить (необходимо для
        # всех таблиц с не-integer pk)
        subscription.save(force_insert=True)

with Action('Adding subscription groups'):
    subscription_groups = [
        (models_coupons.SubscriptionGroup(id='all'),
         ['spotify_ind_1m', 'spotify_ind_3m', 'spotify_ind_6m',
          'spotify_ind_1y', 'netflix_4k_1m', 'netflix_HD_1m']),

        (models_coupons.SubscriptionGroup(id='spotify'),
         ['spotify_ind_1m', 'spotify_ind_3m', 'spotify_ind_6m',
          'spotify_ind_1y']),

        (models_coupons.SubscriptionGroup(id='spotify_ind_1m'),
         ['spotify_ind_1m']),
        (models_coupons.SubscriptionGroup(id='spotify_ind_3m'),
         ['spotify_ind_3m']),
        (models_coupons.SubscriptionGroup(id='spotify_ind_6m'),
         ['spotify_ind_6m']),
        (models_coupons.SubscriptionGroup(id='spotify_ind_1y'),
         ['spotify_ind_1y']),

        (models_coupons.SubscriptionGroup(id='netflix'),
         ['netflix_4k_1m', 'netflix_HD_1m']),

        (models_coupons.SubscriptionGroup(id='netflix_4k_1m'),
         ['netflix_4k_1m']),
        (models_coupons.SubscriptionGroup(id='netflix_HD_1m'),
         ['netflix_HD_1m']),
    ]

    for subscription_group, subscriptions in subscription_groups:
        # force_insert чтобы peewee понял, что значение необходимо
        # именно добавить в таблицу, а не обновить (необходимо для
        # всех таблиц с не-integer pk)
        subscription_group.save(force_insert=True)

        for subscription_id in subscriptions:
            models_coupons.SubscriptionGroupToSubscription(
                subscription_group=subscription_group,
                subscription=subscription_id
            ).save(force_insert=True)

with Action('Adding employees'):
    models_botpiska.Employee.insert(
        chat_id=1099569178
    ).execute()

print('Done.')
