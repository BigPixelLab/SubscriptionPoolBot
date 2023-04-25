import typing

import aiogram

glob = ...


def delete(message_id: int, chat_id: int, bot: aiogram.Bot = None):
    async def _delete_message():
        await bot.delete_message(chat_id, message_id)

    response = Response()
    response.add_action(_delete_message(), priority=0)
    return response


def delete_original():
    message = glob.message.get()
    return delete(message.message_id, message.chat.id)


def function(func: typing.Callable):
    return Response(calls=[func])


class Response:
    def __init__(self, actions: typing.Iterable[tuple[int, typing.Awaitable]]):
        self.actions = dict(actions)

    def add_action(self, action: typing.Awaitable, priority: int = 0):
        self.actions.setdefault(priority, [])
        self.actions[priority].append(action)

