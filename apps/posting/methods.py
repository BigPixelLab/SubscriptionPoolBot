import random
import uuid

import aiogram.types

from apps.posting.models import LotteryPrize
from message_render import MessageRender
from response_system import UserFriendlyException


class PostKeyNotFound(UserFriendlyException):
    """ Пост с указанным id не найден в stored_posts """


stored_posts = {}


def load_post(message: aiogram.types.Message) -> str:
    """ Saves post and returns its key """
    global stored_posts

    post_key = str(uuid.uuid4())  # Can be any unique key
    stored_posts[post_key] = message

    return post_key


def get_post(key: str) -> MessageRender:
    global stored_posts

    try:
        reference: aiogram.types.Message = stored_posts[key]
    except KeyError:
        raise PostKeyNotFound('Не удалось найти пост')

    photo = None
    if reference.photo:
        photo = reference.photo[0].file_id

    animation = None
    if reference.animation:
        animation = reference.animation.file_id

    return MessageRender(
        reference.text or reference.caption,
        photo=photo,
        animation=animation
    )


def remove_post(key: str):
    global stored_posts

    try:
        del stored_posts[key]
    except KeyError:
        pass


def generate_lottery_prize(prizes: list[LotteryPrize], count: int):
    if len(prizes) == 0:
        raise ValueError('Cannot pick a prize when there is no prizes')

    for prize in prizes:
        if prize.count is None:
            continue

        for _ in range(prize.count):
            yield prize
            count -= 1

    weights_and_prizes = ((prize.weight, prize) for prize in filter(lambda x: x.weight, prizes))
    weights, prizes = zip(*weights_and_prizes)

    yield from random.choices(prizes, weights, k=count)
