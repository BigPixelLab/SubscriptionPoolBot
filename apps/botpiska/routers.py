"""
Callbacks:
    buy:<subscription-id>
    get-for-self
    get-as-gift

Commands:
    /start

Messages:
    "Поддержка"
    Сервис

"""
import aiogram.filters
from aiogram import F

import response_system.middleware
from message_render import MessageRender
from . import handlers, filters, callbacks

botpiska_router = aiogram.Router()

# Бот запущен через ссылку с аргументом (t.me/botpiska_bot?start=COUPON)
botpiska_router.message(
    aiogram.filters.CommandStart(deep_link=True)
)(handlers.start_command_handler)

# Бот запущен командой /start
botpiska_router.message(
    aiogram.filters.CommandStart()
)(handlers.start_command_handler)

# Запрос "Назад"
botpiska_router.message(
    F.text.lower() == "назад"
)(handlers.previous_state_handler)

# Запрос "Поддержка"
botpiska_router.message(
    F.text.lower() == "поддержка"
)(handlers.support_message_handler)

# Запрос "Купон"
botpiska_router.message(
    F.text.lower() == "купон"
)(handlers.coupon_message_handler)

# Деактивация купона
botpiska_router.callback_query(
    F.data == 'coupon-deactivate'
)(handlers.coupon_deactivate_handler)

# Вывод полного списка товаров
botpiska_router.message(
    F.text.lower() == "список товаров"
)(handlers.service_list_message_handler)

# Производится поиск сервиса
botpiska_router.message(
    filters.service_filter
)(handlers.service_message_handler)

# Выбран план подписки для покупки ( buy:<subscription_id> )
botpiska_router.callback_query(
    callbacks.BuyButtonCallbackData.filter(),
    response_system.middleware.configure(
        waiting=MessageRender('⌛ Выставляем счёт...'),
        lock='botpiska:buy_button_handler'
    )
)(handlers.buy_button_handler)

# Покупка для себя ( get-for-self )
botpiska_router.callback_query(
    callbacks.GetForSelfButtonCallbackData.filter(),
    response_system.middleware.configure(
        waiting=MessageRender('⌛ Открываем заказ...'),
        lock='botpiska:get_for_self_button_handler'
    )
)(handlers.get_for_self_button_handler)

# Покупка в подарок ( get-as-gift )
botpiska_router.callback_query(
    callbacks.GetAsGiftButtonCallbackData.filter(),
    response_system.middleware.configure(
        waiting=MessageRender('⌛ Создаём подарочную карту...'),
        lock='botpiska:get_as_gift_button_handler'
    )
)(handlers.get_as_gift_button_handler)


op_botpiska_router = aiogram.Router()

# Запущен операторский бот
op_botpiska_router.message(
    aiogram.filters.CommandStart(),
    filters.employee_filter
)(handlers.op_start_command_handler)
