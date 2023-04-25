"""
Модели::

    SubscriptionGroup
    - id: varchar primary key
    - parent_id: SubscriptionGroup? foreign key
    - subscription_id: Subscription? foreign key

    CouponType
    - id: varchar primary key
    - subscription_group: SubscriptionGroup foreign key
    - discount: numeric
    - max_usages: integer?
    - lifespan: timeinterval?
    - allows_gifts: boolean = true

"""
import peewee
from playhouse.postgres_ext import IntervalField

import gls


class SubscriptionGroup(gls.BaseModel):
    """ ... """

    id = peewee.CharField(primary_key=True)
    parent = peewee.ForeignKeyField('self', on_delete='CASCADE', null=True)
    subscription = peewee.DeferredForeignKey('Subscription', on_delete='CASCADE', null=True)

    class Meta:
        table_name = 'SubscriptionGroup'


class CouponType(gls.BaseModel):
    """ ... """

    id = peewee.CharField(primary_key=True)
    """ ID типа """
    subscription_group = peewee.ForeignKeyField(SubscriptionGroup, on_delete='NO ACTION')
    """ Группа подписок, на которую действует купон """
    discount = peewee.DecimalField(max_digits=1000, decimal_places=2)
    """ Скидка, которую предоставляет купон """
    max_usages = peewee.BigIntegerField(null=True)
    """ Если указано, купон может быть использован данное число раз, в 
        заказе или сгенерированном счёте """
    lifespan = IntervalField(null=True)
    """ Если указано, купон будет действителен указанное количество 
        времени с момента создания """
    allows_gifts = peewee.BooleanField(default=True)
    """ Возможно ли покупать в подарок, после активации этого купона. Например,
        при активации подарочного купона, покупать в подарок не имеет смысла """

    class Meta:
        table_name = 'CouponType'
