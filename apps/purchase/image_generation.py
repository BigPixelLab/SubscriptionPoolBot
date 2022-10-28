from __future__ import annotations

import datetime
from decimal import Decimal
from io import BytesIO

from PIL import Image, ImageFont, ImageDraw


def price(p: Decimal | None) -> str:
    value = abs(p)
    sign = round(p / value)

    int_part = int(value) * sign
    dec_part = int((value - int(value)) * 100)
    return f'{int_part}.{dec_part:0>2}р'


def render_bill(bill: list[tuple[str, Decimal]], total: Decimal):
    template = Image.open("apps/purchase/templates/image/bill2.png")

    content_font = ImageFont.truetype("apps/purchase/fonts/shtrixfr57.ttf", size=80)
    total_font = ImageFont.truetype("apps/purchase/fonts/shtrixfr57.ttf", size=120)
    draw = ImageDraw.Draw(template)

    # Date and time
    draw.text(
        (510, 855),
        datetime.datetime.now().strftime('%X %x'),
        fill=(45, 45, 45),
        anchor='ls',
        font=content_font
    )

    # Bill items
    content = '\n'.join(title for title, _ in bill)
    draw.multiline_text(
        (238, 1000),
        content,
        fill=(45, 45, 45),
        spacing=60,
        font=content_font
    )

    content = '\n'.join(price(_price) for _, _price in bill)
    draw.multiline_text(
        (1800, 1000),
        content,
        fill=(45, 45, 45),
        anchor='ra',
        align='right',
        spacing=60,
        font=content_font
    )

    # Total
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
