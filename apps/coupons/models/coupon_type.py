import peewee
from playhouse.postgres_ext import IntervalField

import gls
from .subscription_group import SubscriptionGroup


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
    is_promo = peewee.BooleanField(default=False)
    """ Является ли купон рекламным """

    class Meta:
        table_name = 'CouponType'
