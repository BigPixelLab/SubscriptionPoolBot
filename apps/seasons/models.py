from datetime import date

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

    @classmethod
    def get_season_prize_id(cls, prize_id: int):
        return cls.select() \
            .where(cls.id == prize_id).get()


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

    @classmethod
    def get_season_id(cls, season_id: int):
        return cls.select() \
                        .where(cls.id == season_id).get()

    @classmethod
    def get_season_title(cls, season_title: str):
        return cls.select() \
            .where(cls.title == season_title).get()

    @classmethod
    def select_seasons(cls):
        """ Возвращает все сезоны"""
        return list(cls.select())

    @classmethod
    def get_current_season_id(cls):
        return date.today().month % 12 // 3


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

    @classmethod
    def get_season_prize_bought(cls, user_id: int, season_prize_id: int):
        query = """ SELECT season_prize_id FROM "SeasonPrizeBought" WHERE client_id= %(user_id)s """
        response = ezqr.fetch_values(query, {'user_id': user_id})
        if season_prize_id in response:
            return True
        return False
