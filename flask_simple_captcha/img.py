import os
import random as ran
from typing import Tuple, Optional, Union
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from base64 import b64encode
from .utils import gen_captcha_text, jwtencrypt
from .config import DEFAULT_CONFIG as _DEF, IMGHEIGHT, IMGWIDTH, FONTSIZE
from .text import CaptchaFont


def convert_b64img(
    captcha_img: Image, img_format: str = _DEF['CAPTCHA_IMG_FORMAT']
) -> str:
    """Convert PIL image to base64 string
    Args:
        captcha_img (Image): The PIL image to be converted
        img_format (str, optional): The image format to be used.
            Defaults to 'JPEG'
    Returns:
        str: The base64 encoded image string
    """
    byte_array = BytesIO()
    # JPEG is about ~3x faster
    if img_format == 'JPEG':
        captcha_img.save(byte_array, format=img_format, quality=85)
    else:
        captcha_img.save(byte_array, format=img_format)

    return b64encode(byte_array.getvalue()).decode()


def draw_lines(
    im: Image, lines: int = 6, draw: Optional[ImageDraw.ImageDraw] = None
) -> None:
    """draws the background lines behind captcha text img"""
    if draw is None:
        draw = ImageDraw.Draw(im)

    w, h = im.size
    xinc = w // lines
    yinc = h // 10

    max_circles = ran.randint(1, 2)
    max_lines = lines - max_circles

    ranmap = ['c' for c in range(0, max_circles)] + [
        'l' for l in range(0, max_lines)
    ]
    ran.shuffle(ranmap)

    for i, v in enumerate(ranmap):
        startx = xinc * i
        # 1/3 chance of drawing an ellipse
        if v == 'c':
            x0 = ran.randint(startx, startx + xinc)
            y0 = ran.randint(0, h // 2)

            x1 = ran.randint(x0 + xinc, x0 + xinc * 2)
            y1 = ran.randint(h - yinc * 2, h + yinc * 2)

            draw.ellipse((x0, y0, x1, y1), width=3)
        # 2/3 chance of drawing a line
        else:
            x0 = ran.randint(startx - xinc, startx + xinc)
            y0 = ran.randint(0, h // 3)

            xdist = ran.randint(-xinc * 1, xinc * 1)

            x1 = x0 + xdist
            y1 = ran.randint(h // 2, h)

            draw.line((x0, y0, x1, y1), width=3)
    return im


def create_text_img(
    text: str, font_path: str, font_size: int = FONTSIZE
) -> Image:
    """Create a PIL image of the CAPTCHA text.
    Args:
        text (str): The CAPTCHA text to be drawn.
        font_path (str): The path to the font to be used.
        img_format (str): The image format to be used.
            Defaults to 'JPEG'
    """
    # roboto mono assumed to be 0.75x width of $size * char width
    txt_w, txt_h = (int((font_size * len(text)) * 0.6), int(font_size))
    fnt = ImageFont.truetype(font_path, font_size)

    # background should be slightly larger than text
    back_w, back_h = (int(txt_w * 1.25), int(txt_h * 1.5))

    back_img = Image.new('RGB', (back_w, back_h), color=(0, 0, 0))
    drawer = ImageDraw.Draw(back_img)

    ranx = ran.randint(0, back_w - txt_w)
    rany = ran.randint(0, back_h - txt_h - 5)

    drawer.text((ranx, rany), text, font=fnt, fill=(255, 255, 255, 255))

    back_img = draw_lines(back_img, draw=drawer)

    back_img = back_img.resize((IMGWIDTH, IMGHEIGHT))

    return back_img
