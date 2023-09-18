import datetime
import json
import peewee
import gls

from typing import Optional, Any
from apps.botpiska.models import Client


class JSONField(peewee.TextField):
    def db_value(self, value: Optional[Any]):
        if value is None:
            return None
        return json.dumps(value)

    def python_value(self, value: Optional[str]) -> Any:
        if value is not None:
            return json.loads(value)


class StatisticsTypeAction(gls.BaseModel):
    """ ... """

    """ ID типа действия """
    id = peewee.CharField(primary_key=True)
    """ Название действия """
    title = peewee.CharField()

    class Meta:
        table_name = 'StatisticsTypeAction'


class Statistics(gls.BaseModel):
    """ ... """

    client = peewee.ForeignKeyField(Client, on_delete='NO ACTION')
    """ Тип действия """
    action = peewee.ForeignKeyField(StatisticsTypeAction, backref='statistics', on_delete='NO ACTION')
    """ Данные действия """
    # data = peewee.CharField(null=True)
    data = JSONField()
    """ Дата создания """
    created_at = peewee.DateTimeField()


    class Meta:
        table_name = 'Statistics'
        primary_key = False


    @classmethod
    def record(cls, action: str, user_id: int = 0, /, **data):
        """ Запись активности пользователя
        :param user_id: ID пользователя.
        :param action: тип действия
        :param data: данные, которые были получены при действии пользователя
        :param now: дата создания
        """

        # if not cls.is_user_action(user_id, action):
        try:
            new_object = Statistics.create(
                client=user_id,
                action=action,
                data=data,
                created_at=datetime.datetime.now()
            )
            return new_object
        except peewee.IntegrityError:
            pass

