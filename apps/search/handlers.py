import logging
from pathlib import Path

from aiogram.types import Message

from utils import template
from . import queries
from . import utils

TEMPLATES = Path('apps/search/templates')
logger = logging.getLogger(__name__)


async def search_handler(message: Message):
    service, score = utils.get_suggested_service(
        search := utils.transliterate(message.text),
        queries.get_services()
    )
    logger.info(f'Searching: {search}')
    sub_plans = queries.get_sub_plans(service.id)

    await template.render(TEMPLATES / 'suggestions.xml', {
        'sub_plans': sub_plans,
        'service': service,
        'show': score > 0.01
    }).send(message.chat.id)
