""" ... """
from io import BytesIO

from PIL import Image, ImageDraw


def image_renderer(base_image_path: str):
    """ ... """

    def _decorator(function):

        def _wrapper(*args, **kwargs):
            base = Image.open(base_image_path)
            draw = ImageDraw.Draw(base)

            function(base, draw, *args, **kwargs)

            base.save(buffer := BytesIO(), format="PNG")
            buffer.seek(0)
            return buffer

        return _wrapper

    return _decorator
