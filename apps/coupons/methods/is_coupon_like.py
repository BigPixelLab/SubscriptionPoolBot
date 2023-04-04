import settings


def is_coupon_like(code: str):
    """ Возвращает True если переданная строка похожа на купон.
        Не совершает никаких дополнительных проверок в базе """

    return len(code) == settings.COUPON_MAX_LENGTH \
        and set(code).issubset(settings.COUPON_ALLOWED_SYMBOLS)


__all__ = ('is_coupon_like',)
