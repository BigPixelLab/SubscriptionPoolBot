""" ... """
from __future__ import annotations

import aiogram.types

from . import services
from .models import Employee


async def service_filter(message: aiogram.types.Message) -> dict | bool:
    """ ... """
    text = message.text or message.caption
    if not text:
        return False

    try:
        _services = services.Service.get_search_titles_map()
        service = _services[text]
    except KeyError:
        return False

    return {"service": service}


async def employee_filter(message: aiogram.types.Message) -> dict | bool:
    """ ... """

    return Employee.is_employee(message.from_user.id)


__all__ = ('service_filter', 'employee_filter')
