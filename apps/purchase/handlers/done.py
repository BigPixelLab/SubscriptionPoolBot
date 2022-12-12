from __future__ import annotations

from contextlib import suppress
from pathlib import Path

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, WebAppInfo, Message
from glQiwiApi.qiwi.exceptions import QiwiAPIError

import gls
import settings
from utils import template, database
from utils.feedback import send_feedback
from apps.search import models as search_models
from .paid import bill_is_paid_handler
from .. import callbacks

TEMPLATES = Path('apps/purchase/templates')


async def done_button_handler(
        query: CallbackQuery,
        callback_data: callbacks.CheckBillCallback,
        state: FSMContext
):
    """ ... """
    await query.answer()
    await check_if_bill_is_paid(
        query.message.chat.id,
        query.message,
        callback_data.bill_id,
        callback_data.sub_id,
        callback_data.coupon,
        state
    )


async def check_if_bill_is_paid(
        chat_id: int,
        message: Message,
        bill_id: str,
        subscription_id: int,
        coupon: str | None,
        state: FSMContext
):
    """ ... """

    try:
        bill = await gls.qiwi.get_bill_by_id(bill_id)
    except QiwiAPIError:
        await qiwi_api_error_feedback(chat_id, bill_id)
        return

    if bill.status.value == 'EXPIRED':
        with suppress(TelegramBadRequest):
            await gls.bot.delete_message(chat_id, message.message_id)
        await bill_expired_error_feedback(chat_id)
        return

    if bill.status.value == 'PAID' or settings.DEBUG:
        await bill_is_paid_handler(
            chat_id,
            chat_id,
            message,
            subscription_id,
            coupon,
            bill,
            state
        )
        return

    service, subscription = search_models.Subscription.get_full_name_parts(subscription_id)
    terms = database.single_value(""" select terms from "Service" where name = %(name)s """, name=service)  # TODO: Это было быстрое исправление, эту хрень нужно удалить нахрен, её тут быть не должно вообще
    check_callback = callbacks.CheckBillCallback(
        sub_id=subscription_id,
        bill_id=bill_id,
        coupon=coupon
    )
    terms_callback = callbacks.TermsCallback(
        terms=terms
    )

    render = template.render(TEMPLATES / 'bill.xml', {
        'subscription': subscription,
        'service': service,
        'bill': bill,

        'waiting': bill.status.value == 'WAITING',
        'minimized': False,  # True после оплаты

        'buy_button': {'web_app': WebAppInfo(url=bill.pay_url)},
        'terms_button': {'callback_data': terms_callback.pack()},
        'done_button': {'callback_data': check_callback.pack()}
    }).first()

    await render.edit(message)


# MISC STUFF ##################################################################

async def qiwi_api_error_feedback(chat_id, bill_id):
    await send_feedback(
        f'Ошибка QIWI API (bill_id: {bill_id}), '
        f'пожалуйста, обратитесь в поддержку',
        chat_id
    )


async def bill_expired_error_feedback(chat_id):
    await send_feedback(
        'Срок действия счёта истёк',
        chat_id
    )
