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
)(handlers.season_general_message_handler)


seasons_router.callback_query(
    callbacks.GetSeasonButtonCallbackData.filter()
)(handlers.season_help_handler)


seasons_router.callback_query(
    callbacks.InviteFriendCallbackData.filter(),
    response_system.middleware.configure(
        waiting=MessageRender('⌛ Генерирую deep-link для приглашения друга'),
        lock='season:season_invite'
    )
)(handlers.season_invite_handler)

seasons_router.callback_query(
    callbacks.GetSeasonPrizeCallbackData.filter(),
    response_system.middleware.configure(
        waiting=MessageRender('⌛ Что-то происходит..'),
        lock='season:get_season_prize'
    )
)(handlers.season_buy_prize_handler)

