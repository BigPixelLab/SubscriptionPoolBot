""" ... """
import aiogram.types

import datetime
import gls
import response_system as rs
import response_system_extensions as rse
from apps.botpiska.models import Client
from apps.coupons.models import Coupon
from apps.seasons.models import Season, SeasonPrize, SeasonPrizeBought
from apps.seasons.seasons import get_current_season
from apps.seasons import callbacks
from response_system.core import globals_
from settings import BOT_NAME


async def season_message_handler(_, user: aiogram.types.User):
    """ ... """
    client = Client.get_or_register(user.id)

    from datetime import timedelta, date
    today = date.today()
    last_day_of_month = today.replace(day=28) + timedelta(days=4)
    last_day_of_month = last_day_of_month - timedelta(days=last_day_of_month.day % 28 or 28)
    if last_day_of_month.day == 29:
        last_day_of_month -= timedelta(days=1)
    days_left_in_month = (last_day_of_month - today).days
    season_id = today.month % 12 // 3

    season = Season.get_season_id(season_id)
    season_points = client.season_points
    lst = [season.prize1, season.prize2, season.prize3]
    current_prize = lst[today.month % 12 % 3]
    lst.pop(today.month % 12 % 3)
    prize2, prize3 = lst

    # deep_link = f'https://t.me/{BOT_NAME}?start={coupon.code}'
    # return rse.tmpl_send('apps/seasons/templates/message-season-invite.xml', {
    #     'deep-link': deep_link
    # })
    # coupon_type_id
    print(f'today.month % 12 % 3 = {today.month % 12 % 3}')
    season_prize_bought = SeasonPrizeBought.get_season_prize_bought(user.id, current_prize.id)
    return rse.tmpl_send('apps/seasons/templates/message-season-general.xml', {
        'today': f'{date.today()}',
        'is_prize_bought': season_prize_bought,
        'prize_index': today.month % 12 % 3,
        'rating': client.get_rating_position(),
        'days_left_in_mont': days_left_in_month,
        'season_title': season.title,
        'prize': current_prize,
        'prize2': prize2,
        'prize3': prize3,
        'get_referrals': client.get_referrals(),
        'season_points': client.season_points,
    })


async def season_help(_):
    return rse.tmpl_send('apps/seasons/templates/message-season-help.xml', {
    })


async def season_invite(_, user: aiogram.types.User, callback_data: callbacks.GetSeasonPrizeCallbackData):
    # client = Client.get_or_register(user.id)
    # coupon = Coupon.from_type(type_id='invitation', sets_referral=user.id)
    # deep_link = f'https://t.me/{BOT_NAME}?start={coupon.code}'
    if not Coupon.is_coupon_type_id(user_id=user.id, coupon_type_id='invitation'):
        Coupon.from_type(type_id='invitation', sets_referral=user.id)

    coupon_id = Coupon.get_coupon_type_id(user_id=user.id, coupon_type_id='invitation')
    return rse.tmpl_send('apps/seasons/templates/message-season-invite.xml', {
        'deep-link': f'https://t.me/{BOT_NAME}?start={coupon_id}'
    })


async def get_season_prize(_, user: aiogram.types.User, callback_data: callbacks.GetSeasonPrizeCallbackData):
    client = Client.get_or_register(user.id)

    from datetime import timedelta, date
    today = date.today()
    last_day_of_month = today.replace(day=28) + timedelta(days=4)
    last_day_of_month = last_day_of_month - timedelta(days=last_day_of_month.day % 28 or 28)
    if last_day_of_month.day == 29:
        last_day_of_month -= timedelta(days=1)
    days_left_in_month = (last_day_of_month - today).days
    season_id = today.month % 12 // 3

    season = Season.get_season_id(season_id)
    season_points = client.season_points
    lst = [season.prize1, season.prize2, season.prize3]
    current_prize = lst[today.month % 12 % 3]
    print(f'current_prize = {current_prize}')
    lst.pop(today.month % 12 % 3)
    prize2, prize3 = lst

    season_prize_bought = SeasonPrizeBought.get_season_prize_bought(user.id, current_prize.id)
    season_prize_id = int(callback_data.season_prize_id)
    if season_prize_bought:
        return(
            rse.tmpl_edit('apps/seasons/templates/message-season-general.xml', {
                'today': f'{date.today()}',
                'is_prize_bought': season_prize_bought,
                'prize_index': today.month % 12 % 3,
                'rating': client.get_rating_position(),
                'days_left_in_mont': days_left_in_month,
                'season_title': season.title,
                'prize': current_prize,
                'season_prize_id': season_prize_id,
                'prize2': prize2,
                'prize3': prize3,
                'get_referrals': client.get_referrals(),
                'season_points': client.season_points,
            })
        )
    else:
        if current_prize.id != season_prize_id:
            return (
                rse.tmpl_send('apps/seasons/templates/message-season-already-bought.xml', {})
            )

        coupon = Coupon.from_type(type_id=callback_data.coupon_type_id)
        if client.season_points >= current_prize.cost:
            client.season_points -= current_prize.cost
            client.save()

        season_prize = SeasonPrizeBought()
        season_prize.create(client=user.id, season_prize=current_prize.id, created_at=rs.global_time.get())
        return (
            rse.tmpl_edit('apps/seasons/templates/message-season-general.xml', {
                'today': f'{date.today()}',
                'is_prize_bought': season_prize_bought,
                'prize_index': today.month % 12 % 3,
                'rating': client.get_rating_position(),
                'days_left_in_mont': days_left_in_month,
                'season_title': season.title,
                'prize': current_prize,
                'season_prize_id': season_prize_id,
                'prize2': prize2,
                'prize3': prize3,
                'get_referrals': client.get_referrals(),
                'season_points': client.season_points,
            })
            + rse.tmpl_send('apps/seasons/templates/message-season-prize.xml', {
                'coupon_id': coupon.code})
        )


__all__ = ('season_message_handler', 'season_help', 'season_invite', 'get_season_prize',)
