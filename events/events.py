"""
Как использовать cron для описания времени, когда действует
событие: https://www.baeldung.com/cron-expressions

Базовый синтаксис::

    <minute> <hour> <day-of-month> <month> <day-of-week>

"""
import response_system as rs
import response_system_extensions as rse
from apps.botpiska.methods.buy import SelfOrderEvent

from apps.coupons.models import Coupon
from libs.events import embedded_event, Cron


@embedded_event(trigger='SELF_ORDERED', on=Cron('0 0 19 6 *', days=7))
async def event_1p1(event: SelfOrderEvent):

    # Подписка должна быть куплена по полной стоимости,
    # чтобы учавствовать в акции
    if event.bill.coupon_id is not None:
        return rs.no_response()

    # Если в подписке не указан тип подарочного купона - эту
    # подписку нельзя дарить
    coupon_type = event.subscription.gift_coupon_type_id
    if coupon_type is None:
        return rs.no_response()

    coupon = Coupon.from_type(coupon_type)

    return rse.tmpl_send('events/templates/message-1p1-gift.xml', {
        'coupon': coupon
    })
