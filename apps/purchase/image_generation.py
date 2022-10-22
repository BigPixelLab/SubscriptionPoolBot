from __future__ import annotations

import datetime
from decimal import Decimal
from io import BytesIO

from PIL import Image, ImageFont, ImageDraw

from apps.coupons.models import Coupon
from apps.search.models import Service, Subscription


def price(p: Decimal | None) -> str:
    if p is None:
        return ''

    value = abs(p)
    sign = int(p / value)

    int_part = int(value) * sign
    dec_part = int((value - int(value)) * 100)
    return f'{int_part}.{dec_part:0>2}р'


def render_bill(total: Decimal, subscription: Subscription, service: Service, coupon: Coupon | None, coupon_discount: Decimal):
    template = Image.open("apps/purchase/templates/image/bill2.png")

    content_font = ImageFont.truetype("apps/purchase/fonts/shtrixfr57.ttf", size=80)
    total_font = ImageFont.truetype("apps/purchase/fonts/shtrixfr57.ttf", size=120)
    draw = ImageDraw.Draw(template)

    bill = [(f'Подписка {service.name.upper()} {subscription.name}', subscription.price)]

    if coupon is not None:
        bill.append((f'Купон "{coupon.code}" на -{coupon.discount}%', -coupon_discount))

    bill.append(('Компенсация комиссии qiwi', None))

    draw.text(
        (510, 855),
        datetime.datetime.now().strftime('%X %x'),
        fill=(45, 45, 45),
        anchor='ls',
        font=content_font
    )

    draw.multiline_text(
        (238, 1000),
        '\n'.join(i[0] for i in bill),
        fill=(45, 45, 45),
        spacing=60,
        font=content_font
    )

    draw.multiline_text(
        (1800, 1000),
        '\n'.join(price(i[1]) for i in bill),
        fill=(45, 45, 45),
        anchor='ra',
        align='right',
        spacing=60,
        font=content_font
    )

    draw.text(
        (1800, 1700),
        f'ИТОГО: {price(total)}',
        fill=(45, 45, 45),
        anchor='rs',
        align='right',
        font=total_font
    )

    template.save(buffered := BytesIO(), format="PNG")
    buffered.seek(0)
    return buffered
