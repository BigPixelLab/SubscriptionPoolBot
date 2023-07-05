import peewee

import gls
from apps.coupons.models import CouponType


class Lottery(gls.BaseModel):
    id = peewee.CharField(primary_key=True)
    banner = peewee.CharField()
    title = peewee.CharField()
    description = peewee.TextField()

    class Meta:
        table_name = 'Lottery'


class LotteryPrize(gls.BaseModel):
    id = peewee.IntegerField(primary_key=True)
    lottery = peewee.ForeignKeyField(Lottery, backref='prizes', on_delete='CASCADE')
    coupon_type = peewee.ForeignKeyField(CouponType, on_delete='NO ACTION')
    weight = peewee.IntegerField()
    count = peewee.IntegerField(null=True)
    banner = peewee.CharField()
    title = peewee.CharField()
    description = peewee.TextField()

    class Meta:
        table_name = 'LotteryPrize'
