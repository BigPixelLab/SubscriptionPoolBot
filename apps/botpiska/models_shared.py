"""
Этот файл существует, для того чтобы разрешить циклический импорт.
Все модели этого файла могут быть доступны из models.py

Модели::

    Subscription
    - id: varchar primary key
    - service_id: varchar
    - gift_coupon_type: CouponType? foreign key
    - title: varchar
    - short_title: varchar
    - order_template: text
    - duration: interval
    - price: numeric
    - category: varchar = ''

    Client
    - chat_id: bigint primary key
    - season_bonuses: integer = 0
    - referral: Client? foreign key = null
    - terms_message_id: integer? = null

"""
import datetime
import decimal
import typing

import peewee
from playhouse.postgres_ext import IntervalField

import gls
from apps.botpiska.services import Service
from apps.coupons.models_shared import CouponType


class Subscription(gls.BaseModel):
    """ ... """

    id = peewee.CharField(primary_key=True)
    """ Текстовый ID подписки """
    gift_coupon_type = peewee.ForeignKeyField(CouponType, on_delete='SET NULL', null=True)
    """ Тип купона, который будет использован при покупке подарка """
    service_id = peewee.CharField()
    """ Индекс сервиса, которому принадлежит подписка. Модель сервиса не определена в базе """
    short_title = peewee.CharField()
    """ Короткое наименование подписки, для отображения в кнопках """
    title = peewee.CharField()
    """ Полное наименование подписки, с названием сервиса, типом и длительностью """
    # order_template = peewee.TextField()
    # """ Индекс шаблона заказа. Появляется после покупки """
    duration = IntervalField()
    """ Продолжительность подписки """
    price = peewee.DecimalField(max_digits=1000, decimal_places=2)
    """ Цена подписки """
    category = peewee.CharField(default='')
    """ Группа подписки, используется для сортировки и расчёта скидки (скидка считается в пределах группы) """

    class Meta:
        table_name = 'Subscription'

    @property
    def service(self) -> typing.Optional[Service]:
        """ Сервис """
        self.service_id: str
        return Service.get_by_id(self.service_id)

    @property
    def monthly_price(self) -> decimal.Decimal:
        """ Цена за подписку в месяц """
        self.duration: datetime.timedelta
        return self.price / decimal.Decimal(self.duration.days / 30)

    @property
    def is_featured(self) -> bool:
        self.service_id: str
        service = Service.get_by_id(self.service_id)
        return service is not None \
            and self.id == service.featured_subscription_id

    @classmethod
    def select_service_plans(cls, service_id: str):
        """ Возвращает список подписок указанного сервиса,
            отсортированный по группе и длительности """
        return cls.select()\
            .where(cls.service_id == service_id)\
            .order_by(cls.category, cls.duration.desc())


class Client(gls.BaseModel):
    """ ... """

    chat_id = peewee.BigIntegerField(primary_key=True)
    """ Телеграм ID чата с пользователем """
    referral = peewee.ForeignKeyField('self', on_delete='SET NULL', null=True, default=None)
    """ Пользователь, по ссылке которого перешёл данный пользователь """
    season_points = peewee.IntegerField(default=0)
    """ Количество полученных пользователем бонусов в сезоне """
    terms_message_id = peewee.IntegerField(null=True, default=None)
    """ Телеграм ID сообщения, содержащего условия """

    class Meta:
        table_name = 'Client'

    @classmethod
    def get_or_register(cls, user_id: int, referral: int = None, force_referral: bool = False) -> 'Client':
        """ Пытается получить пользователя из базы и, если не найден,
           добавить его """

        client, _ = cls.get_or_create(chat_id=user_id, defaults={'referral': referral})

        if force_referral and referral and not client.referral_id:
            client.referral = referral
            client.save()

        return client


class Message(gls.BaseModel):
    id = peewee.CharField(primary_key=True)
    banner = peewee.CharField(null=True)
    banner_bot_id = peewee.BigIntegerField(null=True)
    title = peewee.CharField()
    content = peewee.TextField()

    class Meta:
        table_name = 'Message'
