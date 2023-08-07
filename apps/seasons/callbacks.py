from aiogram.filters.callback_data import CallbackData


class SeasonActions:
    HELP = 'help'


class GetSeasonButtonCallbackData(CallbackData, prefix='season-help'):
    """ ... """
    pass


class InviteFriendCallbackData(CallbackData, prefix='referral-link'):
    """ ... """
    pass


class GetSeasonPrizeCallbackData(CallbackData, prefix='season-prize'):
    """ ... """
    coupon_type_id: str
    season_prize_id: str
