import functools
from datetime import date, timedelta
from typing import Optional

import peewee

import ezqr
import gls
from apps.botpiska.models import Client
from apps.coupons.models import CouponType


class SeasonPrize(gls.BaseModel):
    """ ... """

    id = peewee.IntegerField(primary_key=True)
    """ID приза сезона"""
    coupon_type_id = peewee.ForeignKeyField(CouponType, on_delete='NO ACTION')
    """ ID типа купона"""
    banner = peewee.CharField()
    """ Фото """
    title = peewee.CharField()
    """ Наименование """
    cost = peewee.BigIntegerField()
    """ Цена """

    class Meta:
        table_name = 'SeasonPrize'

    def is_bought_by_client(self, user_id: int):
        query = """
            SELECT count(1)
            FROM "SeasonPrizeBought"
            WHERE client_id = %(user_id)s
                AND season_prize_id = %(season_prize_id)s
        """
        result = ezqr.single_value(query, {
            'season_prize_id': self.id,
            'user_id': user_id
        })
        return bool(result)


class Season(gls.BaseModel):
    """ ... """

    id = peewee.IntegerField(primary_key=True)
    """ ID сезона """
    title = peewee.CharField()
    """ Название сезона """
    prize1 = peewee.ForeignKeyField(SeasonPrize, on_delete='NO ACTION')
    """ 1-ый месяц сезона """
    prize2 = peewee.ForeignKeyField(SeasonPrize, on_delete='NO ACTION')
    """ 2-ой месяц сезона """
    prize3 = peewee.ForeignKeyField(SeasonPrize, on_delete='NO ACTION')
    """ 3-ий месяц сезона """
    description = peewee.TextField()
    """ Описание сезона """

    class Meta:
        table_name = 'Season'

    @functools.cached_property
    def current_prize(self) -> Optional[SeasonPrize]:
        month = date.today().month

        if month % 12 // 3 != self.id:
            return None

        # Чтобы не делать два отдельных запроса, заодно кешируем призы
        return self.prizes[self.current_prize_index]

    @functools.cached_property
    def prizes(self) -> tuple[SeasonPrize, SeasonPrize, SeasonPrize]:
        # noinspection PyTypeChecker
        return self.prize1, self.prize2, self.prize3

    @property
    def current_prize_index(self) -> int:
        return date.today().month % 12 % 3

    @property
    def current_prize_days_left(self) -> int:
        today = date.today()
        # The day 28 exists in every month. 4 days later, it's always next month
        next_month = today.replace(day=28) + timedelta(days=4)
        # subtracting the number of the current day brings us back one month
        end_of_the_month = next_month - timedelta(days=next_month.day)
        # and to get days left we can subtract current date from it
        return (end_of_the_month - today).days

    @classmethod
    def get_current(cls) -> Optional['Season']:
        season_id = date.today().month % 12 // 3
        try:
            return cls.get_by_id(season_id)
        except peewee.DoesNotExist:
            return None


class SeasonPrizeBought(gls.BaseModel):
    """ ... """

    client = peewee.ForeignKeyField(Client, on_delete='NO ACTION')
    """ Покупатель """
    season_prize = peewee.ForeignKeyField(SeasonPrize, on_delete='NO ACTION')
    """ ID приза сезона """
    created_at = peewee.DateTimeField()
    """ Дата создания """

    class Meta:
        table_name = 'SeasonPrizeBought'
        primary_key = peewee.CompositeKey('client', 'season_prize')
