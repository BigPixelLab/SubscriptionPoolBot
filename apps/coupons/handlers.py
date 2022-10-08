from __future__ import annotations

from pathlib import Path

import aiogram.types
from aiogram.fsm.context import FSMContext

from utils import manage_message, template
from . import models, queries

TEMPLATES = Path('apps/coupons/templates')


async def coupon_handler(message: aiogram.types.Message, coupon_code: str, state: FSMContext):
    coupon: models.Coupon = models.Coupon.get(coupon_code)

    if not coupon:
        await template.render(TEMPLATES / 'invalid.xml', {}).send(message.chat.id)
        return

    if coupon.is_expired:
        await template.render(TEMPLATES / 'expired.xml', {
            'coupon': coupon
        }).send(message.chat.id)
        return

    if queries.is_promo_used_by_customer(coupon_code, message.from_user.id):
        await template.render(TEMPLATES / 'used_by_customer.xml', {
            'coupon': coupon
        }).send(message.chat.id)
        return

    data = await state.get_data()

    if activated_coupon := data.get('coupon'):
        await template.render(TEMPLATES / 'already_have_active.xml', {
            'activated_coupon': activated_coupon,
            'coupon': coupon
        }).send(message.chat.id)

    else:
        await template.render(TEMPLATES / 'activated.xml', {
            'coupon': coupon
        }).send(message.chat.id)

    await manage_message.delete_marked(state=state, group='search')
    await state.update_data({'coupon': coupon_code})
