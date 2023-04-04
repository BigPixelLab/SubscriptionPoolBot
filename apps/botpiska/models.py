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
    - open_at: timestamp
    - closed_at: timestamp? = null
    - is_notified_to_renew: boolean = false

    Bill
    - client: Client foreign primary key
    - subscription: Subscription foreign key
    - coupon: Coupon? foreign key
    - qiwi_id: text
    - message_id: integer
    - expires_after: timestamp

"""
import datetime
import typing

import peewee

import gls
from .models_shared import Client, Subscription
from ..coupons.models import Coupon


class Employee(gls.BaseModel):
    """ Модель сотрудника """

    chat_id = peewee.BigIntegerField(primary_key=True)
    """ Телеграм ID чата с сотрудником """

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        table_name = 'Employee'

    @classmethod
    def is_employee(cls, user_id: int):
        query = """ select count(*) = 1 from "Employee" where chat_id = %(user_id)s """
        args = {'user_id': user_id}
        value, = gls.db.execute_sql(query, args).fetchone()
        return value

    @classmethod
    def get_to_notify_on_purchase(cls) -> list[int]:
        return list(map(lambda x: x.chat_id, Employee.select(Employee.chat_id)))


class Order(gls.BaseModel):
    """ Модель заказа """

    id = peewee.AutoField(primary_key=True)
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
    paid_amount = peewee.DecimalField(max_digits=1000, decimal_places=2)
    """ Сумма, оплаченная пользователем """
    processing_employee = peewee.ForeignKeyField(Employee, on_delete='NO ACTION', null=True, default=None)
    """ Оператор, обрабатывающий заказ. Если не указан - заказ считается находящимся в ожидании """
    open_at = peewee.DateTimeField()
    """ Дата и время открытия заказа """
    closed_at = peewee.DateTimeField(null=True, default=None)
    """ Дата и время закрытия заказа. Если не указано, но указан processing_employee - 
        заказ считается взятым в обработку """
    is_notified_to_renew = peewee.BooleanField(default=False)
    """ Оповещён ли пользователь о том, что его подписка заканчивается. """

    # noinspection PyMissingOrEmptyDocstring
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
    def is_closed(self):
        """ Заказ закрыт """
        return self.closed_at is not None

    @classmethod
    def get_open(cls, *query):
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
    expires_after = peewee.DateTimeField()
    """ Дата и время, когда счёт становится просроченным """

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        table_name = 'Bill'

    @classmethod
    def get_legit_by_id(cls, pk: int) -> typing.Optional['Bill']:
        try:
            return cls.select_legit_where(Bill.client == pk).get()
        except peewee.DoesNotExist:
            return None

    @classmethod
    def select_legit_where(cls, *query, now: datetime.datetime = None):
        """ Возвращает запрос для получения действительных счетов """
        now = now or datetime.datetime.now()
        return Bill.select().where(*query, now <= Bill.expires_after)


__all__ = (
    'Subscription',
    'Client',
    'Employee',
    'Order',
    'Bill'
)
