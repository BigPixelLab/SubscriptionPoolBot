"""
Модели Botpiska::

    Employee
    - chat_id: bigint primary key

    Order
    - id: integer autoinc primary key
    - client: Client foreign key
    - subscription: Subscription foreign key
    - coupon: Coupon? foreign key
    - paid_amount: numeric
    - processing_employee: Employee? foreign key = null
    - created_at: timestamp
    - closed_at: timestamp? = null
    - notified_renew: boolean = false

    Bill
    - client: Client foreign primary key
    - subscription: Subscription foreign key
    - coupon: Coupon? foreign key
    - qiwi_id: text
    - message_id: integer
    - expires_at: timestamp

"""
import datetime
import typing

import peewee

import ezqr
import gls
from .models_shared import Client, Subscription
from ..coupons.models import Coupon


class Employee(gls.BaseModel):
    """ Модель сотрудника """

    chat_id = peewee.BigIntegerField(primary_key=True)
    """ Телеграм ID чата с сотрудником """

    class Meta:
        table_name = 'Employee'

    @classmethod
    def is_employee(cls, user_id: int):
        query = """ SELECT count(*) = 1 FROM "Employee" WHERE chat_id = %(user_id)s """
        return ezqr.single_value(query, {'user_id': user_id})

    @classmethod
    def get_to_notify_on_purchase(cls) -> list[int]:
        return ezqr.fetch_values(""" SELECT chat_id FROM "Employee" """, {})


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


__all__ = (
    'Subscription',
    'Client',
    'Employee',
    'Order',
    'Bill'
)
