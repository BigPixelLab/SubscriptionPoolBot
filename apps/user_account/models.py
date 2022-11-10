import datetime
import typing

from utils import database


class User(typing.NamedTuple):
    user_id: int
    """ Chat user ID """
    last_interaction: datetime.datetime
    """ Last user interaction with the bot """

    @classmethod
    def add_user_last_interaction(cls, user_id: int, time: datetime.datetime):
        return database.execute(
            """
                insert into "User" (user_id, last_interaction)
                values (%(user_id)s, %(last_interaction)s)
                on conflict (user_id) do update set
                    last_interaction = excluded.last_interaction
            """,
            user_id=user_id,
            last_interaction=time
        )

    @classmethod
    def get_users_to_mailing(cls) -> list[int]:
        return database.fetch_values(
            """
                select user_id from "User"
            """,
            'Getting list of user_id to mailing'
        )

    @classmethod
    def get_user(cls, user_id: int):
        return database.single(
            User,
            """
                select user_id, last_interaction from "User"
                where user_id = %(user_id)s
            """,
            f'Getting user by id = {user_id}',
            user_id=user_id
        )

    @classmethod
    def update_last_interaction(cls, user_id: int, time: datetime.datetime):
        database.execute(
            """
                update "User" set
                    last_interaction = %(time)s
                where user_id = %(user_id)s
            """,
            f'Updating last_interaction for user with {user_id} id',
            user_id=user_id,
            time=time
        )
