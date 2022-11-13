from __future__ import annotations

import typing

from apps.coupons import models as coupon_models

Context = dict[str, typing.Any]


class Post(typing.NamedTuple):
    index: str
    path: str
    context: Context | typing.Callable[[], Context] = lambda: {}

    def get_context(self) -> Context:
        if hasattr(self.context, '__call__'):
            return self.context()
        return self.context


# Posts that can be later send by /post command or automatically
POSTS = [
    # ONE PLUS ONE SPOTIFY
    Post(
        index='opo_spotify_3h',
        path='posts/manual/one_plus_one_spotify/one_plus_one_spotify_3h.xml'
    ),
    Post(
        index='opo_spotify_10h',
        path='posts/manual/one_plus_one_spotify/one_plus_one_spotify_10h.xml'
    ),

    # PROMO FOR FASTEST
    Post(
        index='promo_ff',
        path='posts/daily/promo_for_fastest_30.xml',
        context=lambda: {
            'coupons': [
                coupon_models.Coupon.generate(30, is_one_time=True)
                for _ in range(3)
            ]
        }
    )
]

# For O(1) access by index
POSTS_INDEX_MAP = {p.index: p for p in POSTS}

DAILY_POSTS = [
    # POSTS_INDEX_MAP.get('')
]
