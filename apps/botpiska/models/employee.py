import peewee

import ezqr
import gls


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
