import uuid

import aiogram.types

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
