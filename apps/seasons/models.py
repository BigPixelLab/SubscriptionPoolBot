import peewee
import gls
from apps.botpiska.models import Client
from apps.coupons.models import CouponType


class SeasonPrize(gls.BaseModel):
    """ ... """

    id = peewee.IntegerField(primary_key=True)
    """ID приза сезона"""
    coupon_type_id = peewee.ForeignKeyField(CouponType, on_delete='NO ACTION')
    """ ID типа купона"""
    banner = peewee.CharField() # для чего это?
    """ Фото """
    title = peewee.CharField()
    """ Наименование """
    cost = peewee.BigIntegerField()
    """ Цена """

    class Meta:
        table_name = 'SeasonPrize'

    @classmethod
    def get_prize_id(cls, prize_id: str):
        """ Возвращает сезон по id """
        return cls.select() \
            .where(cls.id == prize_id).get()


class Season(gls.BaseModel):
    """ ... """

    id = peewee.IntegerField(primary_key=True)
    """ ID сезона """
    title = peewee.CharField()
    """ Название сезона """
    price1 = peewee.ForeignKeyField(SeasonPrize, on_delete='NO ACTION')
    """ 1-ый месяц сезона """
    price2 = peewee.ForeignKeyField(SeasonPrize, on_delete='NO ACTION')
    """ 2-ой месяц сезона """
    price3 = peewee.ForeignKeyField(SeasonPrize, on_delete='NO ACTION')
    """ 3-ий месяц сезона """
    description = peewee.TextField()
    """ Описание сезона """
    # title = peewee.CharField()
    # """ Наименование сезона """

    class Meta:
        table_name = 'Season'

    @classmethod
    def select_seasons(cls):
        """ Возвращает все сезоны"""
        return list(cls.select())

    @classmethod
    def get_season_id(cls, season_id: str):
        """ Возвращает сезон по id """
        return cls.select()\
            .where(cls.id == season_id)


class SeasonPrizeBought(gls.BaseModel):
    """ ... """

    client = peewee.ForeignKeyField(Client, on_delete='NO ACTION')
    """ Покупатель """
    season_prize = peewee.ForeignKeyField(SeasonPrize, on_delete='NO ACTION')
    """ ID приза сезона """
    created_at = peewee.DateTimeField()
    """ Дата создани """

    class Meta:
        table_name = 'SeasonPrizeBought'
        primary_key = ('client', 'season_prize')

