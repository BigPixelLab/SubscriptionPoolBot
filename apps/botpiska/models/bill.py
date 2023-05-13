import datetime
import typing

import peewee

import gls
from .client import Client
from .subscription import Subscription
from apps.coupons.models.coupon import Coupon


class Bill(gls.BaseModel):
    """ Модель счёта """

    client = peewee.ForeignKeyField(Client, on_delete='CASCADE', primary_key=True)
    """ ID клиента, сгенерировавшего счёт. При удалении клиента, счёт тоже удаляется. """
    subscription = peewee.ForeignKeyField(Subscription, on_delete='NO ACTION')
    """ Подписка, на которую был сгенерирован счёт """
    coupon = peewee.ForeignKeyField(Coupon, on_delete='NO ACTION', null=True)
    """ Купон, использованный при генерации счёта. Купон резервируется, пока счёт не станет просроченным """
    qiwi_id = peewee.CharField()
    """ Qiwi ID счёта """
    message_id = peewee.IntegerField()
    """ Телеграм ID сообщения, содержащего счёт """
    expires_at = peewee.DateTimeField()
    """ Дата и время, когда счёт становится просроченным """

    class Meta:
        table_name = 'Bill'

    @classmethod
    def get_legit_by_id(cls, pk: int) -> typing.Optional['Bill']:
        try:
            return cls.select_legit().where(Bill.client == pk).get()
        except peewee.DoesNotExist:
            return None

    @classmethod
    def select_legit(cls, *query, now: datetime.datetime = None):
        """ Возвращает запрос для получения действительных счетов """
        now = now or datetime.datetime.now()
        return Bill.select(*query).where(now <= Bill.expires_at)
