import datetime
import decimal
import random
import typing
from typing import Optional

import peewee

import ezqr
import gls
import settings
from apps.botpiska.models.client import Client
from .coupon_type import CouponType

if typing.TYPE_CHECKING:
    from apps.botpiska.models.subscription import Subscription


class Coupon(gls.BaseModel):
    """ ... """

    code = peewee.CharField(max_length=settings.COUPON_MAX_LENGTH, primary_key=True)
    """ Код купона """
    type = peewee.ForeignKeyField(CouponType, on_delete='NO ACTION')
    """ Тип созданного купона """
    sets_referral = peewee.ForeignKeyField(Client, on_delete='NO ACTION', null=True)
    """ Клиент, к которому необходимо привязать любого воспользовавшегося
        купоном пользователя. Также данный клиент не может воспользоваться 
        собственным купоном """
    created_at = peewee.DateTimeField()
    """ Дата и время создания купона """

    class Meta:
        table_name = 'Coupon'

    @property
    def discount_value(self) -> decimal.Decimal:
        """ Возвращает discount в виде значения от 0 до 1.
            Желательно иметь join с CouponType """
        return decimal.Decimal(self.type.discount / 100)

    def is_allowed_for_subscription(self, subscription_id: str) -> bool:
        """ Возвращает True, если купон может использоваться
            для покупки подписки с указанным ID """

        return ezqr.single_value("""
            SELECT count(*) != 0 FROM "CouponSubscriptionView"
            WHERE subscription = %(subscription)s
                and code = %(code)s
        """, dict(subscription=subscription_id, code=self.code))

    def get_sub_single(self) -> Optional['Subscription']:
        """ Если купон доступен для единственной подписки - вернёт её,
            иначе None """

        return ezqr.single_value("""
            WITH subs AS (
                SELECT subscription FROM "CouponSubscriptionView" SC WHERE SC.code = %(code)s
            ) SELECT CASE
                WHEN (SELECT count(*) FROM subs) = 1
                    THEN (SELECT * FROM subs LIMIT 1)
                END;
        """, dict(code=self.code))

    def get_total_uses(self) -> int:
        """ Возвращает фактическое общее число использований купона """

        return ezqr.single_value("""
            SELECT (SELECT count(*) FROM "Order" O WHERE O.coupon_id = %(code)s)
                + (SELECT count(*) FROM "Bill" B WHERE B.coupon_id = %(code)s)
        """, dict(code=self.code))

    def is_already_used_by(self, user_id: int) -> bool:
        """ Возвращает True, если купон уже был ранее использован
            указанным пользователем """

        return ezqr.single_value("""
            SELECT count(*) > 0 FROM "Order" O
            WHERE O.client_id = %(client)s
                and O.coupon_id = %(coupon)s
        """, dict(client=user_id, coupon=self.code))

    @classmethod
    def get_coupon_type_id(cls, user_id: int, coupon_type_id: str):
        query = """ SELECT code FROM "Coupon" 
                WHERE sets_referral_id=%(user_id)s 
                    and type_id=%(coupon_type_id)s"""
        return ezqr.single_value(query, {'user_id': user_id, 'coupon_type_id': coupon_type_id})

    @classmethod
    def is_coupon_type_id(cls, user_id: int, coupon_type_id: str):
        query = """ SELECT type_id FROM "Coupon" 
        WHERE sets_referral_id=%(user_id)s 
            and type_id=%(coupon_type_id)s"""
        response = ezqr.fetch_values(query, {'user_id': user_id, 'coupon_type_id': coupon_type_id})
        if coupon_type_id in response:
            return True
        return False

    @classmethod
    def get_random_code(cls):
        """ Возвращает случайный код купона. Уникальность не гарантируется """
        return ''.join(random.choices(
            settings.COUPON_ALLOWED_SYMBOLS,
            k=settings.COUPON_MAX_LENGTH
        ))

    @classmethod
    def from_type(cls, type_id: str, sets_referral: int = None, now: datetime.datetime = None,
                  no_error: bool = False) -> Optional['Coupon']:
        """
        Создаёт в базе купон с указанным типом.

        :param type_id: ID типа.
        :param sets_referral: Должен ли купон устанавливать реферала. Реферал должен быть в базе.
        :param now: Время создания купона, если не указано - будет установлено на момент вызова функции.
        :param no_error: В случае отсутствия типа или реферала в базе - тихо вернёт None.
        :return: Созданный купон.
        """
        now = now or datetime.datetime.now()
        coupon = None

        while True:
            try:
                coupon = Coupon.create(
                    code=cls.get_random_code(),
                    type=type_id,
                    sets_referral=sets_referral,
                    created_at=now
                )

            # Ключей type_id или sets_referral не существует
            except peewee.DoesNotExist:
                if no_error:
                    return
                raise

            # Купон с таким кодом уже есть в базе
            except peewee.IntegrityError:
                continue

            break

        return coupon
