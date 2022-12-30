from __future__ import annotations

import random
import typing
from dataclasses import dataclass, field

from apps.coupons import models as coupon_models
from . import callbacks

Context = dict[str, typing.Any]


@dataclass
class CouponSettings:
    discount: int
    subscription: int
    count: int
    is_one_time: bool = True

    def __post_init__(self):
        self.validate()

    def validate(self):
        assert 100 >= self.discount > 0
        assert self.count > 0


class Coupon(typing.NamedTuple):
    code: str
    """ Coupon code as in database """
    is_reusable: bool
    """ If not set, after use coupon will be removed from the prize list """


@dataclass
class Prize:
    template: str
    """ Resource index of template for the answer """
    coupon_settings: CouponSettings | None = None
    """ If set, required number of coupons will be generated """
    coupons: list[Coupon] = field(default_factory=list)
    """ List of coupons to use, fills up automatically if coupon_settings are set """
    weight: int = 1
    """ Weight of choice for a random number generator. Less is more rare """

    def __post_init__(self):
        self.validate()

    def validate(self):
        assert self.weight > 0


SHARED_DATA = {
    'prizes': [
        Prize(
            # Месяц SPOTIFY PREMIUM бесплатно
            template='lottery_box_prize_spotify_pr_month_free',
            coupon_settings=CouponSettings(
                discount=100,
                subscription=3,
                count=10
            ),
            weight=5
        ),
        Prize(
            # 30% SPOTIFY PREMIUM на год
            template='lottery_box_prize_spotify_pr_year_30',
            coupon_settings=CouponSettings(
                discount=30,
                subscription=4,
                count=10
            ),
            weight=15
        ),
        Prize(
            # 30% NETFLIX 4K
            template='lottery_box_prize_netflix_4k_month_30',
            coupon_settings=CouponSettings(
                discount=30,
                subscription=5,
                count=10
            ),
            weight=15
        ),
        Prize(
            # 25% на любую подписку
            template='lottery_box_prize_any_25',
            coupons=[
                Coupon('A87LS3', is_reusable=True),
                Coupon('UMU8Z4', is_reusable=True),
                Coupon('3H22BE', is_reusable=True),
                Coupon('455VI0', is_reusable=True),
                Coupon('G60G58', is_reusable=True),
            ],
            weight=35
        ),
        Prize(
            # 20% на любую подписку
            template='lottery_box_prize_any_20',
            coupons=[
                Coupon('I4ZULV', is_reusable=True),
                Coupon('TZYJ99', is_reusable=True),
                Coupon('BP-HZ0', is_reusable=True),
                Coupon('H4IX4U', is_reusable=True),
                Coupon('91PL3W', is_reusable=True),
            ],
            weight=30
        )
    ]
}


def before_posting(data: Context) -> Context:
    """ Called on /post. Edits shared_data """
    prizes = data['prizes']

    # Дополнительная валидация в момент постинга.
    # При запуске бота некоторые ресурсы могут
    # быть ещё не загружены, но при отправке всё
    # обязательно должно быть на месте

    for prize in prizes:  # type: Prize
        settings = prize.coupon_settings

        if settings is None:
            continue

        # Генерируем купоны
        for _ in range(settings.count):
            coupon_code = coupon_models.Coupon.generate(
                discount=settings.discount,
                subscription=settings.subscription,
                is_one_time=settings.is_one_time
            )
            prize.coupons.append(
                Coupon(coupon_code, is_reusable=False)
            )

    return {}


def before_sending(_, data: Context) -> Context:
    """ Called for every user post sent to """
    prizes: list = data['prizes']
    available_prizes = list(filter(lambda i: i.coupons, prizes))

    prize, = random.choices(
        available_prizes,
        [p.weight for p in available_prizes],
        k=1
    )  # type: Prize

    coupon = random.choice(prize.coupons)
    if not coupon.is_reusable:
        prize.coupons.remove(coupon)

    open_btn_callback = callbacks.OpenButtonCallback(
        coupon=coupon.code,
        result_template=prize.template
    )

    return {
        'open_button': {'callback_data': open_btn_callback.pack()}
    }
