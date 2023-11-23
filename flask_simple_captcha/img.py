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


RGBAType = Union[Tuple[int, int, int, int], Tuple[int, int, int]]


def draw_lines(
    im: Image,
    noise: int = 12,
    text_color: RGBAType = (255, 255, 255),
    **kwargs,
) -> Image:
    """Draws complex background noise on the image."""
    draw = kwargs.get('draw', None)
    if draw is None:
        draw = ImageDraw.Draw(im)

    w, h = im.size

    line_starts = [
        (ran.randint(0, w), ran.randint(0, h))
        for _ in range(int(noise * 0.66) * 2)
    ]

    # Draw lines
    for i in range(0, len(line_starts) - 1, 2):
        x0, y0 = line_starts[i]
        x1, y1 = line_starts[i + 1]
        draw.line((x0, y0, x1, y1), fill=text_color, width=2)

    ellipse_centers = [
        (ran.randint(0, w), ran.randint(0, h))
        for _ in range(int(noise * 0.33))
    ]

    # Draw ellipses
    for center_x, center_y in ellipse_centers:
        radius_x = ran.randint(4, w // 4)
        radius_y = ran.randint(4, h // 4)
        upper_left = (center_x - radius_x, center_y - radius_y)
        lower_right = (center_x + radius_x, center_y + radius_y)
        draw.ellipse((upper_left + lower_right), outline=text_color, width=2)

    return im


def create_text_img(
    text: str,
    font_path: str,
    font_size: int = FONTSIZE,
    back_color: RGBAType = (0, 0, 0, 255),
    text_color: RGBAType = (255, 255, 255),
) -> Image:
    """Create a PIL image of the CAPTCHA text.
    Args:
        text (str): The CAPTCHA text to be drawn.
        font_path (str): The path to the font to be used.
        img_format (str): The image format to be used.
            Defaults to 'JPEG'
        back_color (RGBAType): The background color to be used.
            Defaults to (0, 0, 0, 255)
        text_color (RGBAType): The text color to be used.
            Defaults to (255, 255, 255)
    Returns:
        Image: The PIL image of the CAPTCHA text.
    """
    # roboto mono assumed to be 0.6x width of $size * char width
    char_w = round(font_size * 0.6)
    actual_txt_w = len(text) * char_w
    txt_w = font_size * len(text)
    txt_h = font_size

    fnt = ImageFont.truetype(font_path, font_size)

    # background should be slightly larger than text
    back_w, back_h = (round(actual_txt_w * 1.25), round(txt_h * 1.5))

    # each char is randomly placed in a segment of the background
    txt_seg_w = int(back_w / len(text))  # rounds down

    # gap between background h/w and text h/w
    seg_gap_h = int(back_h - txt_h)  # rounds down

    # create background image
    back_img = Image.new('RGB', (back_w, back_h), color=back_color)

    # only initialize drawer once
    drawer = ImageDraw.Draw(back_img)

    char_chords = []

    for i, c in enumerate(text):
        startx = i * txt_seg_w
        endx = startx + (txt_seg_w - char_w)
        # roboto mono seems to appear slightly under the baseline
        starty = -5
        endy = seg_gap_h - 5

        ranx = ran.randint(startx, endx)
        rany = ran.randint(starty, endy)

        char_chords.append((ranx, rany))

        drawer.text((ranx, rany), c, font=fnt, fill=text_color)

    # 6 minimum
    back_img = draw_lines(
        back_img, noise=12, draw=drawer, text_color=text_color
    )

    back_img = back_img.resize((IMGWIDTH, IMGHEIGHT))

    return back_img
