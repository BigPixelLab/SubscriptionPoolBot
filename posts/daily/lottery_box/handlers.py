from aiogram import Router
from aiogram.types import CallbackQuery

import resources
from apps.coupons.models import Coupon
from utils import template
from posts.daily.lottery_box import callbacks


async def open_button_handler(query: CallbackQuery, callback_data: callbacks.OpenButtonCallback):
    tmpl = resources.resolve(callback_data.result_template).path
    coupon = Coupon.get(callback_data.coupon)
    await template.render(tmpl, {
        'coupon': coupon
    }).first().edit(query.message)


def register(router: Router):
    router.callback_query(
        callbacks.OpenButtonCallback.filter()
    )(open_button_handler)
