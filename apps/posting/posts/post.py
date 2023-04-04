import abc

from message_render import MessageRenderList


class Post(abc.ABC):

    def prepare(self, chat_ids: list[int]) -> None:
        """ Вызывается перед началом отправки поста """
        pass

    @abc.abstractmethod
    def send(self, chat_id: int) -> MessageRenderList:
        """ Собирает сообщение для отправки пользователю """
        raise NotImplementedError

    def cleanup(self) -> None:
        """ Вызывается после отправки поста всем пользователям """
        pass
