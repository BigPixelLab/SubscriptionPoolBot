import peewee

import gls
from .subscription import Subscription
from .client import Client
from .employee import Employee
from apps.coupons.models.coupon import Coupon
from apps.coupons.models.coupon_type import CouponType


class Order(gls.BaseModel):
    """ Модель заказа """

    id = peewee.IntegerField(primary_key=True)
    """ Номер заказа """
    client = peewee.ForeignKeyField(Client, backref='orders', on_delete='NO ACTION')
    """ Клиент, сделавший заказ. Удаление клиента, сделавшего хоть один заказ, 
        вызовет ошибку! """
    subscription = peewee.ForeignKeyField(Subscription, on_delete='NO ACTION')
    """ Подписка, на которую был сделан заказ. Удаление подписки, на которую 
        был сделан хоть один заказ, вызовет ошибку! """
    coupon = peewee.ForeignKeyField(Coupon, on_delete='NO ACTION', null=True)
    """ Купон, использованный при совершении покупки. Удаление купона, использованного
        хоть при одной покупке, вызовет ошибку! """
    processing_employee = peewee.ForeignKeyField(Employee, on_delete='NO ACTION', null=True, default=None)
    """ Оператор, обрабатывающий заказ. Если не указан - заказ считается находящимся в ожидании """
    paid_amount = peewee.DecimalField(max_digits=1000, decimal_places=2)
    """ Сумма, оплаченная пользователем """
    created_at = peewee.DateTimeField()
    """ Дата и время открытия заказа """
    closed_at = peewee.DateTimeField(null=True, default=None)
    """ Дата и время закрытия заказа. Если не указано, но указан processing_employee - 
        заказ считается взятым в обработку """
    notified_renew = peewee.BooleanField(default=False)
    """ Оповещён ли пользователь о том, что его подписка заканчивается. """

    class Meta:
        table_name = 'Order'

    @property
    def is_free(self):
        """ Заказ открыт и никем не обрабатывается """
        return self.processing_employee_id is None and self.closed_at is None

    @property
    def is_processed(self):
        """ Заказ обрабатывается оператором """
        return self.processing_employee_id is not None and self.closed_at is None

    @property
    def is_closed(self) -> bool:
        """ Заказ закрыт """
        return self.closed_at is not None

    @classmethod
    def select_open(cls, *query):
        """ Возвращает Query открытых заказов """
        return cls.select(*query).where(cls.closed_at.is_null(True))

    @classmethod
    def select_by_id_joined(cls, pk: int):
        return cls.select_by_id(pk) \
            .join(Subscription) \
            .switch(Order) \
            .join(Coupon, peewee.JOIN.LEFT_OUTER) \
            .join(CouponType, peewee.JOIN.LEFT_OUTER)

    @classmethod
    def select_open_joined(cls):
        return cls.select_open() \
            .join(Subscription) \
            .switch(Order) \
            .join(Coupon, peewee.JOIN.LEFT_OUTER) \
            .join(CouponType, peewee.JOIN.LEFT_OUTER)
