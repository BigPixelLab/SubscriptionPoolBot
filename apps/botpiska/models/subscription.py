import datetime
import decimal
import typing

import peewee
from playhouse.postgres_ext import IntervalField

import gls
from apps.botpiska.services import Service
from apps.coupons.models.coupon_type import CouponType


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
    duration = IntervalField(null=True)
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
        self.price: decimal.Decimal

        if self.duration is None:
            return self.price
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
