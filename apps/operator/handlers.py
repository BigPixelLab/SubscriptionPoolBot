from aiogram.filters import CommandObject
from aiogram.types import Message

import settings
from apps.operator import models


async def set_notify_status_handler(message: Message, command: CommandObject):
	if command.args not in settings.OP_POSITIVE_ANSWER | settings.OP_NEGATIVE_ANSWER:
		...
		return

	status = command.args in settings.OP_POSITIVE_ANSWER
	models.Employee.set_notify_status(message.from_user.id, status)
