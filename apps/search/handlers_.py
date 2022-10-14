from __future__ import annotations

import datetime
import typing
from contextlib import suppress
from pathlib import Path

import aiogram
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PreCheckoutQuery, CallbackQuery
from fuzzywuzzy import fuzz

import gls
import settings
from . import models
from . import callbacks
from .utils import transliterate
from utils import database, template_, manage_message
from ..coupons.models import Coupon

TEMPLATES = Path('apps/search/templates')


# SEARCH REQUEST ----------------------

async def search_handler(message: Message, state: FSMContext):
    services = database.fetch(models.Service, """
        select * from "Service"
    """, 'Getting services from Service')

    suggestions = search_suggestions(
        transliterate(message.text),
        services,
        settings.SUGGESTION_SCORE_THRESHOLD,
        settings.MAX_SUGGESTIONS_SHOWN
    )

    if not suggestions:
        await message.answer('Мы пока не работаем с этим сервисом')
        return

    await manage_message.mark_for_deletion(message, state=state, group='search')

    for service in suggestions:
        _message = template_.render(TEMPLATES / 'service.html', {
            'service': service.name.upper(),
            'description': service.description,

            'Посмотреть планы': {'callback_data': callbacks.ShowMoreCallback(service_id=service.id)}
        }, as_caption=True)

        sent_message = await message.answer_photo(service.banner, **_message)
        await manage_message.mark_for_deletion(sent_message, state=state, group='search')


def search_suggestions(request: str,
                       services: list[models.Service],
                       threshold: int,
                       max_suggestions: int) -> list[models.Service]:

    class ServiceSearchMatch(typing.NamedTuple):
        service: models.Service
        score: int

    if not services:
        return []

    match_table = [
        ServiceSearchMatch(service, fuzz.ratio(request, service.name))
        for service in services
    ]

    match_table.sort(key=lambda x: x.score, reverse=True)

    max_score = match_table[0].score
    results = filter(
        lambda x: max_score - x.score <= threshold and x.score > 0,
        match_table
    )

    return [
        result.service
        for _, result in zip(range(max_suggestions), results)
    ]


# SHOW MORE BUTTON PRESSED ------------

async def show_more_callback(query: CallbackQuery,
                             callback_data: callbacks.ShowMoreCallback,
                             state: FSMContext):

    sub_info_list = get_subscriptions_in_stock(callback_data.service_id)

    data = await state.get_data()
    coupon_code = data.get('coupon')

    coupon: Coupon | None = None
    if coupon_code:
        coupon = database.single(Coupon, """
            select * from "Coupon" where code = %(code)s limit 1
        """, 'Getting one coupon from Coupon', code=coupon_code)

    buttons = []
    for sub_info in sub_info_list:
        sub_price = int(sub_info.subscription_price * 100)  # Перевод в копейки
        service_name = sub_info.service_name.upper()

        bill = [aiogram.types.LabeledPrice(
            label=f'Подписка {service_name} {sub_info.subscription_name}',
            amount=sub_price
        )]

        if coupon:
            # Discount in range from 0 to 1
            discount = coupon.discount / 100

            bill.append(aiogram.types.LabeledPrice(
                label=f'Купон "{coupon.code}" на скидку {coupon.discount}%',
                amount=int(-sub_price * discount)
            ))

        total = sum(p.amount for p in bill) / 100

        payload = callbacks.SubscriptionPayload(
            subscription=sub_info.subscription_id,
            coupon=coupon_code,
            total=total
        )

        invoice_link = await gls.bot.create_invoice_link(
            title=service_name,
            description=sub_info.short,
            payload=payload.pack(),
            provider_token=settings.PAYMENTS_TOKEN,
            currency='rub',
            prices=bill,
            photo_url=sub_info.service_logo,
            photo_width=1000,
            photo_height=1000
        )

        button = aiogram.types.InlineKeyboardButton(
            text=f'{sub_info.subscription_name} - {total}₽' + (f' ({sub_info.subscription_price}₽)' if coupon else ''),
            url=invoice_link
        )

        buttons.append([button])
        # if len(buttons[-1]) >= 3:
        #     buttons.append([])

    if not buttons:
        buttons = [aiogram.types.InlineKeyboardButton(
            text='Нет подписок в наличии',
            callback_data='skip'
        )]

    await query.message.edit_reply_markup(
        aiogram.types.InlineKeyboardMarkup(inline_keyboard=buttons)
    )

    await query.answer()


class SubscriptionInfo(typing.NamedTuple):
    subscription_id: int
    subscription_name: str
    subscription_price: float
    service_name: str
    service_description: str
    service_logo: str
    short: str


def get_subscriptions_in_stock(service_id: int) -> list[SubscriptionInfo]:
    sub_info_list = database.fetch_rows("""
        select
            S.id, S.name, S.price, E.name, E.description, E.logo, E.short
        from "Subscription" as S
            join "Service" E on E.id = S.service
        where S.service = %(service_id)s and (
            -- Count of activation codes for current subscription
            select count(*) from "ActivationCode" as AC
            where AC.subscription = S.id and AC.linked_order is null
        ) >= 1
        order by S.duration
    """, 'Getting subscription info that has service_id', service_id=service_id)

    return [
        SubscriptionInfo(*sub_info)
        for sub_info in sub_info_list
    ]


# USER ENTERED CARD DETAILS -----------

async def payment_verification_handler(query: PreCheckoutQuery):
    order_info = callbacks.SubscriptionPayload.unpack(query.invoice_payload)

    if not is_subscription_in_stock(order_info.subscription):
        await query.answer(ok=False, error_message='Временно нет в наличии, средства не будут списаны')
        return

    if order_info.coupon and not is_coupon_valid(order_info.coupon):
        await query.answer(ok=False, error_message='Купон больше не действителен, средства не будут списаны')
        return

    await query.answer(ok=True)


def is_subscription_in_stock(sub_id: int):
    return database.single_value("""
        select count(*) from "ActivationCode"
        where subscription = %(sub_id)s and linked_order is null
    """, 'Getting the number of subscription in stock', sub_id=sub_id)


def is_coupon_valid(coupon: str):
    return database.single_value("""
        select count(*) from "Coupon"
        where code = %(coupon)s and (
            is_promo = true and is_expired = false or 
            is_promo = false
        )
    """, 'Getting a valid coupon from Coupon', coupon=coupon)


# MONEY TRANSFERRED -------------------

async def successful_payment_handler(message: Message, state: FSMContext):
    order_info = callbacks.SubscriptionPayload.unpack(
        message.successful_payment.invoice_payload
    )

    created_at, order_id = place_order(
        order_info.subscription,
        order_info.coupon,
        order_info.total,
        message.from_user.id,
    )

    claim_activation_code(
        order_id,
        order_info.subscription
    )

    await state.update_data({'coupon': None})
    if order_info.coupon:
        use_coupon(order_info.coupon)

    await manage_message.delete_marked(state=state, group='search')

    banner, content = render_confirmation(order_id, as_caption=True)

    await gls.bot.send_photo(
        message.from_user.id,
        banner,
        **content
    )


async def update_confirmation_handler(query: CallbackQuery, callback_data: callbacks.UpdateConfirmationCallback):
    with suppress(TelegramBadRequest):
        _, content = render_confirmation(
            callback_data.order_id,
            as_caption=True
        )
        await query.message.edit_caption(**content)
    await query.answer('Статус очереди обновлён')


def render_confirmation(order_id: int, *, as_caption: bool = False):
    queue_length = get_order_queue_length(datetime.datetime.now())

    banner, service_name, sub_name = database.single_row("""
        select E.bought, E.name, S.name from "Order" O
            join "Subscription" S on S.id = O.subscription
            join "Service" E on E.id = S.service
        where O.id = %(id)s
    """, id=order_id)

    return banner, template_.render(TEMPLATES / 'confirmation.html', {
        'order': order_id,
        'queue_length': queue_length,
        'service': service_name.upper(),
        'subscription': sub_name,

        'Обновить': {
            'callback_data': callbacks.UpdateConfirmationCallback(
                order_id=order_id
            )
        }
    }, as_caption=as_caption)


def place_order(sub_id, coupon, total, user_id):
    created_at = datetime.datetime.now()
    return created_at, database.single_value("""
        insert into "Order" (subscription, coupon, total, customer_id, created_at)
        values (%(sub_id)s, %(coupon)s, %(total)s, %(customer_id)s, %(created_at)s) returning id
    """, sub_id=sub_id, coupon=coupon, total=total, customer_id=user_id, created_at=created_at)


def get_order_queue_length(at_time: datetime.datetime):
    return database.single_value("""
        select count(*) from "Order" where created_at <= %(created_at)s and closed_at is null
    """, created_at=at_time)


def claim_activation_code(order_id: int, sub_id: int):
    database.execute("""
        update "ActivationCode" set
            linked_order = %(linked_order)s
        where id = (
            -- First unclaimed activation code for given subscription
            select AC.id from "ActivationCode" as AC
            where AC.linked_order is null and AC.subscription = %(sub_id)s
            order by AC.id limit 1
        )
    """, linked_order=order_id, sub_id=sub_id)


def use_coupon(coupon: str):
    # Delete coupon if it is not promo
    database.execute("""
        delete from "Coupon"
        where is_promo = false and id = (
            select C.id from "Coupon" C
            where C.code = %(coupon)s limit 1
        )
    """, coupon=coupon)
