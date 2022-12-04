from __future__ import annotations

import random
import typing
from dataclasses import dataclass, field

import resources
from apps.coupons import models as coupon_models

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
    title: str
    """ Name of the prize to display """
    photo: str
    """ Resource index of banner for this prize """
    is_special: bool
    """ Is prize should be highlighted """
    coupon_settings: CouponSettings | None = None
    """ If set, required number of coupons will be generated """
    coupons: list[Coupon] = field(default_factory=list)
    """ List of coupons to use, fills up automatically if coupon_settings are set """
    weight: int = 1
    """ Weight of choice for a random number generator. Less is more rare """

    def __post_init__(self):
        self.validate()

    def validate(self, *, final: bool = False):
        assert not final or self.photo in resources.UPLOADED_RESOURCE_INDEXES
        assert self.weight > 0


SHARED_DATA = {
    'prizes': [
        Prize(
            title='Крутой купон',
            photo='lottery_box_50',
            is_special=True,
            coupon_settings=CouponSettings(
                discount=50,
                subscription=7,
                count=1
            )
        ),
        Prize(
            title='Тупой купон',
            photo='lottery_box_10',
            is_special=False,
            coupons=[
                Coupon('KAIF10', is_reusable=True)
            ]
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
    for prize in prizes:
        prize.validate(final=True)

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

    return {
        'prizes': prizes
    }


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

    return {
        'banner_index': prize.photo,
        'coupon': coupon.code
    }
