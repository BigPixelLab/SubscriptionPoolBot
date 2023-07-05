""" ... """
from __future__ import annotations

import aiogram.types

from ..methods.buy import buy_for_user, buy_as_gift_by_user


async def get_for_self_button_handler(_, user: aiogram.types.User):
    """ Открывает заказ, который после будет обработан оператором """
    return await buy_for_user(user)


async def get_as_gift_button_handler(_, user: aiogram.types.User):
    """
    Отправляет сообщение со сгенерированной подарочной картой.
    Для этого генерируется купон со скидкой 100% на выбранную
    подписку.
    Купон при покупке зарегистрирует пользователя как реферала,
    также не позволит передарить подписку.
    """
    return await buy_as_gift_by_user(user)


__all__ = (
    'get_for_self_button_handler',
    'get_as_gift_button_handler'
)
