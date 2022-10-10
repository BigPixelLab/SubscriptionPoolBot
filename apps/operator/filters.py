from __future__ import annotations

import aiogram.types

from utils import database


def is_employee(message: aiogram.types.Message | aiogram.types.CallbackQuery) -> bool:
    user = message.from_user.id
    return database.single_value(
        # Count of employees with given telegram-id, zero if no such employee
        """ select count(*) > 0 from "Employee" where chat_id = %(user)s """,
        f'Checking if the user {user} is an employee',
        user=user
    )
