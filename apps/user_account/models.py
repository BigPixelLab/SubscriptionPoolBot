import datetime
import typing

from utils import database


class User(typing.NamedTuple):
    user_id: int
    """ Chat user ID """
    last_interaction: datetime.datetime
    """ Last user interaction with the bot """

    @classmethod
    def set_user_last_interaction(cls, user_id: int, time: datetime.datetime):
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
