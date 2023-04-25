""" ... """
import datetime
import decimal

import qrcode
from PIL import ImageDraw, ImageFont, Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

from image_renderer import image_renderer

ITEMS_STYLE = dict(
    font=ImageFont.truetype('apps/botpiska/templates/resources/BILL-FONT.ttf', size=80),
    fill=(45, 45, 45)
)
TOTAL_STYLE = dict(
    font=ImageFont.truetype('apps/botpiska/templates/resources/BILL-FONT.ttf', size=120),
    fill=(45, 45, 45)
)

format_time = '{0:%X MSK+00 %x}'.format
format_total = 'ИТОГО: {0:.2f}p'.format
format_price = '{0:.2f}p'.format
multiline = '\n'.join


@image_renderer('apps/botpiska/templates/resources/BILL.png')
def render_bill_image(
        _: Image.Image,
        draw: ImageDraw.ImageDraw,
        bill_items: list[tuple[str, decimal.Decimal]],
        total: decimal.Decimal,
        time: datetime.datetime
):
    """ ... """

    item_prompts, item_prices = zip(*bill_items)
    item_prices = map(format_price, item_prices)

    draw.text(
        (510, 855), format_time(time),
        anchor='ls',
        **ITEMS_STYLE
    )
    draw.multiline_text(
        (238, 1000), multiline(item_prompts),
        spacing=60,
        **ITEMS_STYLE
    )
    draw.multiline_text(
        (1800, 1000), multiline(item_prices),
        anchor='ra', align='right',
        spacing=60,
        **ITEMS_STYLE
    )
    draw.text(
        (1800, 1700), format_total(total),
        anchor='rs', align='right',
        **TOTAL_STYLE
    )


@image_renderer('apps/botpiska/templates/resources/GIFT-CARD.png')
def render_gift_card_image(
        image: Image.Image,
        _: ImageDraw.ImageDraw,
        link: str
):
    """ ... """

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q)
    qr.add_data(link)

    qr_width = 200
    qr_image = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        embeded_image_path="apps/botpiska/templates/resources/QR-ICON.png",
        back_color="transparent"
    )
    qr_image.thumbnail((qr_width, qr_width), Image.ANTIALIAS)

    image.paste(qr_image, (
        (image.width - qr_width) // 2,
        (image.height - qr_width) // 2 + 80)
    )
