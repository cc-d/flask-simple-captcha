import os
import random as ran
from typing import Tuple, Optional, Union
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from base64 import b64encode
from .utils import gen_captcha_text, jwtencrypt
from .config import DEFAULT_CONFIG as _DEF
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


def draw_lines(im: Image, lines: int = 6) -> Image:
    """draws the background lines behind captcha text img"""
    draw = ImageDraw.Draw(im)
    x, y = im.size
    xinc = int(x / 10)
    yinc = int(y / 10)

    for i in range(lines):
        if i % 3 == 0:
            # ellipse
            x0 = ran.randint(-1 * xinc, x - (xinc * 1))
            x1 = ran.randint(x0 + xinc, x)
            y0 = ran.randint(-1 * y * 2, yinc * 2)
            y1 = ran.randint(y // 2 + yinc, y + (y // 2))
            draw.ellipse((x0, y0, x1, y1), width=3)
        else:
            x0 = ran.randint(0, x // 2)
            y0 = ran.randint(0, y // 2)
            x1 = ran.randint(0, x)
            y1 = ran.randint(y // 2, y)

            draw.line((x0, y0, x1, y1), width=ran.randint(3, 4))
    return im


def create_text_img(
    text: str,
    font_path: str,
    font_size: int = _DEF['TEXT_FONT_SIZE'],
    vary_font_size: bool = _DEF['VARY_FONT_SIZE'],
    vary_font_range: int = _DEF['VARY_FONT_RANGE'],
) -> Image:
    """Create a PIL image of the CAPTCHA text.
    Args:
        text (str): The CAPTCHA text to be drawn.
        font_path (str): The path to the font to be used.
        img_format (str): The image format to be used.
            Defaults to 'JPEG'
        font_size (int): The font size to be used.
            Defaults to 30
        vary_font_size (bool, optional): Should the font size be varied?
            Defaults to True
        vary_font_range (int, optional): The range of font size variation.
            Defaults to 2
    """
    width, height = (font_size * len(text), font_size * 2)
    ranx, rany = (ran.randint(0, font_size), ran.randint(0, font_size))
    if vary_font_size:
        font_size_range = tuple(
            i for i in range(-vary_font_range, vary_font_range + 1)
        )
        font_size = font_size + ran.choice(font_size_range)

    imgtxt = Image.new('RGB', (width, height), color=(0, 0, 0, 255))

    fnt = ImageFont.truetype(font_path, font_size)
    drawer = ImageDraw.Draw(imgtxt)

    drawer.text((ranx, rany), text, font=fnt, fill=(255, 255, 255, 255))

    imgtxt.resize((180, 60))
    out_img = draw_lines(imgtxt)

    return out_img
