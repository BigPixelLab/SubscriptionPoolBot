import aiogram
from aiogram import F

# import response_system
import response_system.middleware
from message_render import MessageRender
from . import handlers, callbacks


seasons_router = aiogram.Router()

# Запрос "Сезон"
seasons_router.message(
    F.text.lower() == "сезон"
)(handlers.season_message_handler)


seasons_router.callback_query(
    callbacks.GetSeasonButtonCallbackData.filter()
)(handlers.season_help)

# seasons_router.callback_query(
#     callbacks.GetSeasonButtonCallbackData.filter(F.action == callbacks.SeasonActions.CLOSE)
# )(handlers.season_func_сlose_test)

seasons_router.callback_query(
    # callbacks.GetSeasonButtonCallbackData.filter(F.coupon_id == callbacks.SeasonActions.REFERRAL_LINK)
    callbacks.InviteFriendCallbackData.filter(),
    response_system.middleware.configure(
        waiting=MessageRender('⌛ Генерирую deep-link для приглашения друга'),
        lock='season:season_invite'
    )
)(handlers.season_invite)

seasons_router.callback_query(
    callbacks.GetSeasonPrizeCallbackData.filter(),
    response_system.middleware.configure(
        waiting=MessageRender('⌛ Что-то происходит..'),
        lock='season:get_season_prize'
    )
)(handlers.get_season_prize)

