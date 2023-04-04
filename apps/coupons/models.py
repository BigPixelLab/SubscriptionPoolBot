"""
Модели::

    SubscriptionGroup
    - id: varchar(INDEX_MAX_LENGTH) primary key

    SubscriptionGroupToSubscription
    - subscription_group: SubscriptionGroup foreign primary key
    - subscription: Subscription foreign primary key

    Coupon
    - code: varchar(COUPON_MAX_LENGTH) primary key
    - subscription_group: SubscriptionGroup foreign key
    - discount: numeric
    - sets_referral: Client? foreign key
    - max_usages: integer?
    - expires_after: timestamp?
    - is_gifts_allowed: boolean = true
    - note: text

"""
import datetime
import decimal
import random

import peewee

import gls
import settings
from ..botpiska.models import Client, Subscription


class SubscriptionGroup(gls.BaseModel):
    """ ... """

    id = peewee.CharField(max_length=settings.INDEX_MAX_LENGTH, primary_key=True)

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        table_name = 'SubscriptionGroup'


class SubscriptionGroupToSubscription(gls.BaseModel):
    """ ... """

    subscription_group = peewee.ForeignKeyField(SubscriptionGroup, on_delete='CASCADE')
    subscription = peewee.ForeignKeyField(Subscription, on_delete='CASCADE')

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        primary_key = peewee.CompositeKey('subscription_group', 'subscription')
        table_name = 'SubscriptionGroupToSubscription'


class Coupon(gls.BaseModel):
    """ ... """

    code = peewee.CharField(max_length=settings.COUPON_MAX_LENGTH, primary_key=True)
    """ Код купона """
    subscription_group = peewee.ForeignKeyField(SubscriptionGroup, on_delete='NO ACTION')
    """ Группа подписок, на которую действует купон """
    discount = peewee.DecimalField(max_digits=1000, decimal_places=2)
    """ Скидка, которую предоставляет купон """
    sets_referral = peewee.ForeignKeyField(Client, on_delete='NO ACTION', null=True)
    """ Клиент, к которому необходимо привязать любого воспользовавшегося
        купоном пользователя. Также данный клиент не может воспользоваться 
        собственным купоном """
    max_usages = peewee.IntegerField(null=True)
    """ Если указано, купон может быть использован данное число раз, в 
        заказе или сгенерированном счёте """
    expires_after = peewee.DateTimeField(null=True)
    """ Если указано, купон не может быть использован после данных даты и времени """
    is_gifts_allowed = peewee.BooleanField(default=True)
    """ Возможно ли покупать в подарок, после активации этого купона. Например,
        при активации подарочного купона, покупать в подарок не имеет смысла """
    note = peewee.TextField()
    """ Текстовая заметка о ток как был создан купон. Необходимо в основном для
        статистики и ручного удаления, в случае чего """

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        table_name = 'Coupon'

    @property
    def discount_value(self) -> decimal.Decimal:
        """ Возвращает discount в виде значения от 0 до 1 """
        return decimal.Decimal(self.discount / 100)

    def _select_allowed_subscriptions(self, *query, where=True):
        """ Возвращает query выделяющий подписки на которые действует купон """

        return Subscription\
            .select(*query)\
            .join(SubscriptionGroupToSubscription)\
            .join(SubscriptionGroup)\
            .join(Coupon)\
            .where((Coupon.code == self.code) & where)

    def is_allowed_for_subscription(self, subscription_id: str) -> bool:
        """ Возвращает True, если купон может использоваться
            для покупки подписки с указанным ID """

        return self._select_allowed_subscriptions(
            where=(Subscription.id == subscription_id)
        ).count() > 0

    def get_allowed_subscription_ids(self) -> set[str]:
        """ Возвращает множество ID подписок, на которые действует купон """
        return set(self._select_allowed_subscriptions(Subscription.id))

    def get_total_uses(self) -> int:
        """ Возвращает фактическое общее число использований купона """

        query = """
            select (select count(*) from "Order" O where O.coupon_id = %(coupon)s)
                + (select count(*) from "Bill" B where B.coupon_id = %(coupon)s)
        """
        args = {'coupon': self.code}

        cursor = gls.db.execute_sql(query, args)
        value, = cursor.fetchone()
        return value

    def is_already_used_by(self, user_id: int) -> bool:
        """ Возвращает True, если купон уже был ранее использован
            указанным пользователем """

        query = """ select count(*) > 0 from "Order" O where O.client_id = %(client)s and O.coupon_id = %(coupon)s """
        args = {'client': user_id, 'coupon': self.code}

        cursor = gls.db.execute_sql(query, args)
        value, = cursor.fetchone()
        return value

    @classmethod
    def get_random_code(cls):
        """ Возвращает случайный код купона. Уникальность не гарантируется """
        return ''.join(random.choices(
            settings.COUPON_ALLOWED_SYMBOLS,
            k=settings.COUPON_MAX_LENGTH
        ))

    @classmethod
    def generate(cls, **kwargs):
        """ Генерирует купон с указанными параметрами (код выбирается случайно)
            и добавляет его в базу """

        while True:
            code = cls.get_random_code()
            coupon = Coupon(code=code, **kwargs)
            try:
                coupon.save(force_insert=True)
            except peewee.IntegrityError:
                continue
            break
        return coupon

    @classmethod
    def generate_gift(
            cls,
            subscription_id: str,
            gift_from_user_id: int,
            now: datetime.datetime = None,
            note: str = None
    ):
        """ Генерирует подарочный купон """

        now = now or datetime.datetime.now()
        expires_after = now + settings.GIFT_COUPON_VALID_INTERVAL

        # Предполагается, что в базе есть SubscriptionGroup для
        # каждой подписки с соответствующими ID
        return cls.generate(
            subscription_group=subscription_id,
            discount=100,
            max_usages=1,
            expires_after=expires_after,
            is_gifts_allowed=False,
            sets_referral=gift_from_user_id,
            note=note,
        )
