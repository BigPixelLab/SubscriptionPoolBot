"""
Этот файл существует, для того чтобы разрешить циклический импорт.
Все модели этого файла могут быть доступны из models.py

Модели::

    Subscription
    - id: varchar(INDEX_MAX_LENGTH) primary key
    - service_id: varchar(INDEX_MAX_LENGTH)
    - title: varchar(255)
    - short_title: varchar(255)
    - order_template: text
    - duration: interval
    - price: numeric
    - is_queuing_required: boolean = false  # TODO: Избавиться
    - is_special_offer: boolean = false  # TODO: Избавиться
    - group: varchar(INDEX_MAX_LENGTH) = ''
    - display: boolean = true

    Client
    - chat_id: bigint primary key
    - season_bonuses: integer = 0
    - referral: Client? foreign key = null
    - terms_message_id: integer? = null

"""
import datetime
import decimal

import peewee
from playhouse.postgres_ext import IntervalField

import gls
import settings
from apps.botpiska.services import SERVICE_MAP, Service


class Subscription(gls.BaseModel):
    """ ... """

    id = peewee.CharField(max_length=settings.INDEX_MAX_LENGTH, primary_key=True)
    """ Текстовый ID подписки """
    service_id = peewee.CharField(max_length=settings.INDEX_MAX_LENGTH)
    """ Индекс сервиса, которому принадлежит подписка. Модель сервиса не определена в базе """
    title = peewee.CharField()
    """ Полное наименование подписки, с названием сервиса, типом и длительностью """
    short_title = peewee.CharField()
    """ Короткое наименование подписки, для отображения в кнопках """
    order_template = peewee.TextField()
    """ Индекс шаблона заказа. Появляется после покупки """
    duration = IntervalField()
    """ Продолжительность подписки """
    price = peewee.DecimalField(max_digits=1000, decimal_places=2)
    """ Цена подписки """
    is_queuing_required = peewee.BooleanField(default=False)
    """ Есть ли необходимость ставить пользователя в очередь после покупки.
        Полезно для подписок, требующих времени для покупки ключа и активации """
    is_special_offer = peewee.BooleanField(default=False)
    """ Выделять ли подписку особым образом в списке """
    group = peewee.CharField(max_length=settings.INDEX_MAX_LENGTH, default='')
    """ Группа подписки, используется для сортировки и расчёта скидки (скидка считается в пределах группы) """
    display = peewee.BooleanField(default=True)
    """ Показывать ли подписку в списке подписок """

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        table_name = 'Subscription'

    @property
    def monthly_price(self):
        """ Цена за подписку в месяц """
        self.duration: datetime.timedelta
        return self.price / decimal.Decimal(self.duration.days / 30)

    @property
    def is_featured(self):
        service: Service = SERVICE_MAP.get(self.service_id)
        return service is not None and self.id == service.featured_subscription_id

    @classmethod
    def select_service_plans(cls, service_id: str):
        """ Возвращает список подписок указанного сервиса,
            отсортированный по группе и длительности """
        return cls.select()\
            .where(cls.service_id == service_id, cls.display)\
            .order_by(cls.group, cls.duration.desc())


class Client(gls.BaseModel):
    """ ... """

    chat_id = peewee.BigIntegerField(primary_key=True)
    """ Телеграм ID чата с пользователем """
    season_bonuses = peewee.IntegerField(default=0)
    """ Количество полученных пользователем бонусов в сезоне """
    referral = peewee.ForeignKeyField('self', on_delete='SET NULL', null=True, default=None)
    """ Пользователь, по ссылке которого перешёл данный пользователь """
    terms_message_id = peewee.IntegerField(null=True, default=None)
    """ Телеграм ID сообщения, содержащего условия """

    # noinspection PyMissingOrEmptyDocstring
    class Meta:
        table_name = 'Client'

    @classmethod
    def get_or_register(cls, user_id: int, referral: int = None) -> 'Client':
        """ Пытается получить пользователя из базы и, если не найден,
           добавить его """

        client, is_created = cls.get_or_create(chat_id=user_id, defaults={'referral': referral})

        if is_created:
            ...  # TODO: Записать в таблицу статистики, что был зарегистрирован новый пользователь

        if not client.referral_id and referral:
            client.referral = referral
            client.save()

        return client
