from pathlib import Path

from aiogram.filters import CommandObject
from aiogram.types import Message

import settings
from apps.operator import models
from utils import template

TEMPLATES = Path('apps/operator/templates')
NOTIFICATION_STATUS_ANSWERS = (
	'Бот больше не будет отправлять вам оповещения',
	'Бот теперь будет отправлять вам оповещения'
)


async def set_notify_status_handler(message: Message, command: CommandObject):
	if command.args not in settings.OP_POSITIVE_ANSWER | settings.OP_NEGATIVE_ANSWER:
		await template.render(TEMPLATES / 'help/notify.xml', {}).send(message.from_user.id)
		return

	status = command.args in settings.OP_POSITIVE_ANSWER
	models.Employee.set_notify_status(message.from_user.id, status)
	await message.answer(NOTIFICATION_STATUS_ANSWERS[status])
