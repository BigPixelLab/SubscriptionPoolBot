""" ... """
import aiogram.types

import settings
import response_system as rs
import response_system_extensions as rse
from apps.botpiska.models import Client
from apps.coupons.models import Coupon
from apps.seasons.models import Season, SeasonPrizeBought
from apps.seasons import callbacks
from apps.statistics.models import Statistics
from response_system import UserFriendlyException


async def season_general_message_handler(_, user: aiogram.types.User):
    """ ... """

    client, _ = Client.get_or_register(user.id)
    season = Season.get_current()

    if season is None or season.current_prize is None:
        return rse.tmpl_send('apps/seasons/templates/message-season-not-found.xml', {})

    is_prize_bought = season.current_prize.is_bought_by_client(client.chat_id)
    Statistics.record('open_season', client.chat_id)
    return rse.tmpl_send('apps/seasons/templates/message-season-general.xml', {
        'is_prize_bought': is_prize_bought,
        'client': client,
        'season': season
    })


async def season_open_message_handler(_, user: aiogram.types.User):
    """ ... """

    client, _ = Client.get_or_register(user.id)
    season = Season.get_current()

    if season is None or season.current_prize is None:
        return rse.tmpl_send('apps/seasons/templates/message-season-not-found.xml', {})

    is_prize_bought = season.current_prize.is_bought_by_client(client.chat_id)
    Statistics.record('open_season', client.chat_id)
    return rse.tmpl_edit('apps/seasons/templates/message-season-general.xml', {
        'is_prize_bought': is_prize_bought,
        'client': client,
        'season': season
    })


async def season_buy_prize_handler(_, user: aiogram.types.User, callback_data: callbacks.GetSeasonPrizeCallbackData):
    """ ... """

    client, _ = Client.get_or_register(user.id)
    season = Season.get_current()

    if season is None or season.current_prize is None or season.current_prize.id != callback_data.season_prize_id:
        raise UserFriendlyException('Сообщение устарело.')

    is_prize_bought = season.current_prize.is_bought_by_client(client.chat_id)

    if is_prize_bought:
        return UserFriendlyException('Приз уже куплен.')

    if client.season_points < season.current_prize.cost:
        return UserFriendlyException('Недостаточно бонусов.')

    coupon = Coupon.from_type(type_id=callback_data.coupon_type_id)
    client.season_points -= season.current_prize.cost
    client.save()

    SeasonPrizeBought.create(
        client=user.id,
        season_prize=season.current_prize.id,
        created_at=rs.global_time.get()
    )

    Statistics.record('bought_season_prize', user.id, season_prize=season.current_prize.id)

    return (
        rse.tmpl_edit('apps/seasons/templates/message-season-general.xml', {
            'is_prize_bought': True,
            'client': client,
            'season': season
        })
        + rse.tmpl_send('apps/seasons/templates/message-season-prize.xml', {
            'deep-link': f'https://t.me/{settings.BOT_NAME}?start={coupon.code}',
            'prize': season.current_prize
        })
    )


async def season_help_handler(_, user: aiogram.types.User):
    """ ... """

    Statistics.record('open_season_about', user.id)
    return rse.tmpl_send('apps/seasons/templates/message-season-help.xml', {})


async def season_invite_handler(_, user: aiogram.types.User):
    """ ... """

    coupon = Coupon.get_clients_invitation(user.id)
    Statistics.record('open_referral_link', user.id, coupon=coupon.code)
    return rse.tmpl_send('apps/seasons/templates/message-season-invite.xml', {
        'deep-link': f'https://t.me/{settings.BOT_NAME}?start={coupon.code}'
    })


__all__ = (
    'season_general_message_handler',
    'season_open_message_handler',
    'season_help_handler',
    'season_invite_handler',
    'season_buy_prize_handler',
)
