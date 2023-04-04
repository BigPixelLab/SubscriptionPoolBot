import template
from message_render import MessageRenderList
from .post import Post


class SimplePost(Post):
    def __init__(self, tmpl: str, context: dict):
        self.post = template.render(tmpl, context)

    def send(self, chat_id: int) -> MessageRenderList:
        return self.post
