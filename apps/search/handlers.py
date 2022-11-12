import itertools
import logging
from pathlib import Path

from aiogram import Bot
from aiogram.types import Message

import resources
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

    # Should be guaranteed to be sorted by type first
    sub_plans = queries.get_sub_plans(service.id)
    for _, sub_group in itertools.groupby(sub_plans, lambda x: x.type):
        sub_group = list(sub_group)

        for sub_plan in sub_group:
            sub_plan.monthly_price = round(sub_plan.price / sub_plan.duration.days * 30)

        example_plan = max(sub_group, key=lambda x: x.monthly_price)
        for sub_plan in sub_group:
            # Если план один в группе - скидка устанавливается в None
            # ибо скидка имеет смысл только когда она относительно чего-то
            sub_plan.discount = (
                100 - round(sub_plan.monthly_price / example_plan.monthly_price * 100)
                if len(sub_group) > 1 else None
            )

    show = score > 0.01

    render = template.render(TEMPLATES / 'suggestions.xml', {
        'sub_plans': sub_plans,
        'service': service,
        'show': show
    }).first()

    if show:
        render.photo = resources.get(service.banner, key=Bot.get_current().id)

    await render.send(message.chat.id)
