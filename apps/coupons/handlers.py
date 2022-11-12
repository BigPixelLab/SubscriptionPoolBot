from __future__ import annotations

from pathlib import Path

import aiogram.types
from aiogram.fsm.context import FSMContext

from utils import template
from . import models
from ..purchase import handlers as purchase_handlers, callbacks as purchase_callbacks

TEMPLATES = Path('apps/coupons/templates')


async def coupon_handler(message: aiogram.types.Message, coupon_code: str, state: FSMContext):
    coupon: models.Coupon = models.Coupon.get(coupon_code)

    if not coupon:
        await template.render(TEMPLATES / 'invalid.xml', {}).send(message.chat.id)
        return

    models.Coupon.update_expired(coupon.code)

    if coupon.is_expired:
        await template.render(TEMPLATES / 'expired.xml', {
            'coupon': coupon
        }).send(message.chat.id)
        return

    if coupon.referer is not None and coupon.referer == message.from_user.id:
        await template.render(TEMPLATES / 'used_by_referer.xml', {}).send(message.chat.id)
        return

    if models.Coupon.is_used(coupon_code, message.from_user.id):
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

    await state.update_data({'coupon': coupon_code})

    if coupon.subscription:
        await purchase_handlers.buy_view(
            message.chat.id,
            purchase_callbacks.BuySubscriptionCallback(
                sub_id=coupon.subscription
            ),
            state
        )
