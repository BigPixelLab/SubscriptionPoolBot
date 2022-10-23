import typing

from utils import database


class Employee(typing.NamedTuple):
    id: int
    """ Employee ID """
    name: str
    """ Name of the employee, how to call him """
    chat_id: int
    """ Telegram user ID of the employee """
    notify_on_purchase: bool
    """ Is bot going to notify operator every time someone makes a purchase """

    @classmethod
    def set_notify_status(cls, user_id: int, status: bool):
        database.execute(
            """ 
                update "Employee" set
                    notify_on_purchase = %(status)s
                where chat_id = %(user_id)s
            """,
            f'Setting notify status for user {user_id} to ' + ('enable' if status else 'disable'),
            status=status,
            user_id=user_id
        )

    @classmethod
    def get_to_notify(cls) -> list[int]:
        return database.fetch_values(
            """
                select chat_id from "Employee" where notify_on_purchase
            """,
            'Getting list of employees to notify',
        )
