from io import BytesIO

from PIL import Image, ImageFont, ImageDraw


def render_bill(total, subscription, service, coupon, coupon_discount):
    image = Image.new('RGB', (2700, 2160), (255, 255, 0))

    font = ImageFont.truetype("apps/purchase/fonts/Roboto-Regular.ttf", size=200)
    draw = ImageDraw.Draw(image)

    draw.text((20, 20), 'Hello', fill=(0, 0, 0), font=font)

    image.save(buffered := BytesIO(), format="PNG")
    buffered.seek(0)
    return buffered
