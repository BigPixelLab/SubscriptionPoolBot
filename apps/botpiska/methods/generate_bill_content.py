import decimal

import settings
from apps.botpiska.models import Subscription
from apps.coupons.models import Coupon


def generate_bill_content(subscription: Subscription, coupon: Coupon = None) \
        -> tuple[list[tuple[str, decimal.Decimal]], decimal.Decimal]:
    """ Возвращает содержимое счёта и подсчитывает конечную
        сумму к оплате. Сумма к оплате гарантированно
        больше единицы """

    items = [(subscription.title, subscription.price)]
    total = subscription.price

    if coupon is not None:
        amount = -total * coupon.discount_value
        items.append((f'Купон "{coupon.code}"', amount))
        total += amount

    amount = -total * settings.QIWI_COMMISSION
    items.append(('Компенсация комиссии Qiwi', amount))
    total += amount

    total = max(decimal.Decimal(1), total)
    return items, total


__all__ = ('generate_bill_content',)
