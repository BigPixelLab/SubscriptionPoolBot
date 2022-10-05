from __future__ import annotations

from pathlib import Path

import aiogram.types
from aiogram.fsm.context import FSMContext

from utils import template_, manage_message
from . import models, queries

TEMPLATES = Path('apps/coupons/templates')


async def coupon_handler(message: aiogram.types.Message, coupon_code: str, state: FSMContext):
    coupon: models.Coupon = models.Coupon.get(coupon_code)

    if not coupon:
        await message.answer(**template_.render(TEMPLATES / 'no_coupon.html', {}))
        return

    context = {
        'coupon': coupon,
    }

    if coupon.is_promo and coupon.is_expired:
        await message.answer(**template_.render(TEMPLATES / 'expired_promo.html', context))
        return

    if queries.is_promo_used_by_customer(coupon_code, message.from_user.id):
        await message.answer(**template_.render(TEMPLATES / 'used_coupon.html', context))
        return

    data = await state.get_data()

    if old_coupon := data.get('coupon'):
        await message.answer(**template_.render(TEMPLATES / 'had_activated.html', {
            'old_coupon': old_coupon,
            **context
        }))

    elif coupon.is_promo:
        await message.answer(**template_.render(TEMPLATES / 'activated_promo.html', context))

    else:
        await message.answer(**template_.render(TEMPLATES / 'activated_coupon.html', context))

    await manage_message.delete_marked(state=state, group='search')
    await state.update_data({'coupon': coupon_code})
