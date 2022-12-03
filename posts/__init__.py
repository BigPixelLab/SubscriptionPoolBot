from __future__ import annotations

import copy
import typing

from aiogram import Router

from apps.coupons import models as coupon_models
from posts.daily import lottery_box
from utils import template as template_

Context = Data = dict[str, typing.Any]
TelegramChat = int


class Post(typing.NamedTuple):
    index: str
    """ Index by which post can be called then using /post command """
    template: str
    """ Path to the template file """
    context: Context
    """ Static part of the context provided to template """
    data: Data | None = None
    """ Post data. General difference with context is that data is mutable and shared
        across posts sent by one /post call """
    before_posting: typing.Callable[[Data], Context] | None = None
    """ Function to call before posting. Should return context. Can edit data """
    before_sending: typing.Callable[[TelegramChat, Data], Context] | None = None
    """ Function to call before sending post to user. Should return context. Can edit data """
    handlers: str | None = None
    """ Path to the handlers file """

    def prepared(self, chats: typing.Sequence[int]) \
            -> typing.Generator[None, tuple[TelegramChat, template_.MessageRenderList], None]:
        """ Prepares posts contexts for sending """
        data = copy.deepcopy(self.data) if self.data else {}
        context = copy.deepcopy(self.context)

        if self.before_posting:
            _ctx = self.before_posting(data)
            context.update(copy.deepcopy(_ctx) if _ctx else {})

        for chat in chats:
            local_context = copy.deepcopy(context)

            if self.before_sending:
                _ctx = self.before_sending(chat, data)
                local_context.update(copy.deepcopy(_ctx) if _ctx else {})

            tmpl = template_.render(self.template, local_context)
            yield chat, tmpl


# Posts that can be later send by /post command or automatically
POSTS = [
    # ONE PLUS ONE SPOTIFY
    Post(
        index='opo_spotify_3h',
        template='posts/manual/one_plus_one_spotify/one_plus_one_spotify_3h.xml',
        context={}
    ),
    Post(
        index='opo_spotify_10h',
        template='posts/manual/one_plus_one_spotify/one_plus_one_spotify_10h.xml',
        context={}
    ),

    # PROMO FOR FASTEST
    Post(
        index='promo_ff',
        template='posts/daily/promo_for_fastest_30.xml',
        context={},

        data={
            'discount': 30,
            'coupons': 3
        },
        before_posting=lambda data: {
            'coupons': [
                coupon_models.Coupon.generate(
                    discount=data['discount'],
                    is_one_time=True
                ) for _ in range(data['coupons'])
            ]
        }
    )
]

# For O(1) access by index
POSTS_INDEX_MAP = {p.index: p for p in POSTS}

DAILY_POSTS = [
    # POSTS_INDEX_MAP.get('')
]


def _load_handler_modules():
    """ Reloads posts handlers into HANDLER_REGISTER_FUNCTIONS """
    global HANDLER_REGISTER_FUNCTIONS
    import importlib.util

    HANDLER_REGISTER_FUNCTIONS = []
    paths = [post.handlers for post in POSTS if post.handlers]
    for path in paths:
        spec = importlib.util.spec_from_file_location('module', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Every "handlers" module must have "register" function
        HANDLER_REGISTER_FUNCTIONS.append(module.register)


# This list is made for specific purpose
# no need to use it anywhere else.
# Just leave it alone, okay??
HANDLER_REGISTER_FUNCTIONS: list[typing.Callable[[Router], None]] = []
_load_handler_modules()
