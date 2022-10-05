from __future__ import annotations

import aiogram.types

from utils import database


def is_employee(message: aiogram.types.Message | aiogram.types.CallbackQuery):
    employee = database.single_value(
        # Count of employees with given telegram-id, zero if no such employee
        'select count(*) from "Employee" where chat_id = %s',
        message.from_user.id
    )
    return bool(employee)
