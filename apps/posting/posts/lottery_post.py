import dataclasses
from functools import reduce

from message_render import MessageRender, MessageRenderList
from .post import Post
from apps.coupons.models import Coupon


@dataclasses.dataclass
class CommonPrize:
    message: MessageRender
    """ Сообщение, на которое меняется оригинальный пост после получения приза """
    coupons: list[Coupon]
    """ Список купонов, которые используются для данного приза (с указанным кодом, 
        для создания, если не присутствуют в базе) """
    weight: int
    """ Шанс выпадения этого приза, если не выпал особый """


@dataclasses.dataclass
class SpecialPrize:
    message: MessageRender
    """ Сообщение, на которое меняется оригинальный пост после получения приза """
    coupon: Coupon
    """ Купон, используемый в качестве шаблона (без указания кода) """
    count: int
    """ Количество призов данного типа, которое должно быть роздано за один пост """


class LotteryPost(Post):
    prize_tables = {}

    def __init__(self, ptk: str, special: list[SpecialPrize], common: list[CommonPrize]):
        if ptk in self.prize_tables:
            raise ValueError(f'PrizeTable key "{ptk}" is already in use')

        for _ in filter(lambda p: p.coupon.code, special):
            raise ValueError('SpecialPrize coupon should NOT have a code specified')

        coupons = reduce(lambda s, p: s + p.coupons, common, [])
        for _ in filter(lambda c: not c.code, coupons):
            raise ValueError('CommonPrize coupon SHOULD have a code specified')

        self.prize_tables[ptk] = special, common
        self.ptk = ptk

    def prepare(self, chat_ids: list[int]) -> None:
        ...

    def send(self, chat_id: int) -> MessageRenderList:
        ...

    def cleanup(self) -> None:
        ...
