from aiogram import Router
from aiogram.types import CallbackQuery

from utils import template
from posts.daily.lottery_box import callbacks

OPEN_TEMPLATE_PATH = 'posts/daily/lottery_box/lottery_box_open.xml'


async def open_button_handler(query: CallbackQuery, callback_data: callbacks.OpenButtonCallback):
    await template.render(OPEN_TEMPLATE_PATH, {
        'banner_index': callback_data.banner_index,
        'coupon': callback_data.coupon
    }).first().edit(query.message)


def register(router: Router):
    router.callback_query(
        callbacks.OpenButtonCallback.filter()
    )(open_button_handler)
