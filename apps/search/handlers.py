from pathlib import Path

from aiogram.types import Message

import gls
from utils import template
from . import queries
from . import utils

TEMPLATES = Path('apps/search/templates')


async def search_handler(message: Message):
    service, score = utils.get_suggested_service(
        utils.transliterate(message.text),
        queries.get_services()
    )
    # Перед получением списка подписок необходимо снять резервацию
    # с ключей для которых она истекла, иначе, если для заказа
    # подписки требуется свободный ключ, его может не оказаться
    queries.update_reserved_activation_codes()
    sub_plans = queries.get_sub_plans(service.id)

    await template.render(TEMPLATES / 'suggestions.xml', {
        'sub_plans': sub_plans,
        'service': service,
        'show': score != 0
    }).send(message.chat.id)
