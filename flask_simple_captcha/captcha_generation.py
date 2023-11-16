import base64
import random
import string
import os
import sys
import json
from random import randint
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple
from uuid import uuid4
from werkzeug.security import check_password_hash, generate_password_hash
from .config import DEFAULT_CONFIG

from .utils import (
    jwtencrypt,
    jwtdecrypt,
    gen_captcha_text,
    CHARPOOL,
    exclude_similar_chars,
    convert_b64img,
)


class CAPTCHA:
    """CAPTCHA class to generate and validate CAPTCHAs."""

    def __init__(self, config: dict):
        """Initialize CAPTCHA with default configuration."""
        self.config = {**DEFAULT_CONFIG, **config}

        self.verified_captchas = set()
        self.secret = self.config['SECRET_CAPTCHA_KEY']

        if 'EXPIRE_NORMALIZED' in config:
            self.expire_secs = config['EXPIRE_NORMALIZED']
        elif 'EXPIRE_SECONDS' in config:
            self.expire_secs = config['EXPIRE_SECONDS']
        elif 'EXPIRE_MINUTES' in config and 'EXPIRE_SECONDS' not in config:
            self.expire_secs = config['EXPIRE_MINUTES'] * 60
        else:
            self.expire_secs = DEFAULT_CONFIG['EXPIRE_SECONDS']

        if 'CHARACTER_POOL' in self.config:
            chars = self.config['CHARACTER_POOL']
        else:
            chars = ''.join(CHARPOOL)

        if (
            'ONLY_UPPERCASE' in self.config
            and self.config['ONLY_UPPERCASE'] is False
        ):
            chars = ''.join(set(c for c in chars))
            self.only_upper = False
        else:
            chars = ''.join(set(c.upper() for c in chars))
            self.only_upper = True

        if self.config['CAPTCHA_DIGITS']:
            chars += string.digits

        if (
            'EXCLUDE_VISUALLY_SIMILAR' not in self.config
            or self.config['EXCLUDE_VISUALLY_SIMILAR']
        ):
            chars = exclude_similar_chars(chars)

        self.characters = tuple(set(chars))

    def get_background(self, text_size: Tuple[int, int]) -> Image:
        """Generate a background image based on text img size
        Args:
            text_size (Tuple[int, int]): size of text img
        Returns:
            Image: background image for the text img
        """
        return Image.new(
            'RGBA',
            (int(text_size[0] * 1.25), int(text_size[1] * 1.5)),
            color=(0, 0, 0, 255),
        )

    def draw_lines(self, im: Image, lines: int = 6):
        """draws the background lines behind captcha text img"""
        draw = ImageDraw.Draw(im)
        x, y = im.size
        xinc = int(x / 10)
        yinc = int(y / 10)

        for i in range(lines):
            if i % 3 == 0:
                # ellipse
                x0 = randint(-1 * xinc, x - (xinc * 1))
                x1 = randint(x0 + xinc, x)
                y0 = randint(-1 * y * 2, yinc * 2)
                y1 = randint(y // 2 + yinc, y + (y // 2))
                draw.ellipse((x0, y0, x1, y1), width=3)
            else:
                x0 = randint(0, x)
                y0 = randint(0, y)
                x1 = randint(0, x)
                y1 = randint(0, y)
                draw.line((x0, y0, x1, y1), width=3)
        return im

    def create(self, length=None, digits=None) -> str:
        """Create a new CAPTCHA dict and add it to self.captchas"""
        length = self.config['CAPTCHA_LENGTH'] if length is None else length
        add_digits = (
            self.config['CAPTCHA_DIGITS'] if digits is None else digits
        )

        text = gen_captcha_text(
            length=length, add_digits=add_digits, charpool=self.characters
        )

        size = 30
        width, height = length * size, size

        base = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))

        txt = Image.new('RGBA', base.size, color=(0, 0, 0, 255))

        f_path = os.path.dirname(os.path.realpath(__file__))
        f_path = os.path.join(f_path, 'arial.ttf')
        fnt = ImageFont.truetype(f_path, size)

        d = ImageDraw.Draw(txt)

        d.text((0, 0), text, font=fnt, fill=(255, 255, 255, 255))

        text_img = Image.alpha_composite(base, txt)

        text_size = (int(text_img.size[0] * 0.75), int(text_img.size[1] * 1))

        background = self.get_background(text_size)

        background.paste(
            text_img,
            box=(
                random.randint(0, background.size[0] - text_size[0]),
                random.randint(0, background.size[1] - text_size[1]),
            ),
        )

        out_img = background.resize((200, 60))
        out_img = self.draw_lines(out_img)

        return {
            'img': convert_b64img(out_img),
            'text': text,
            'hash': jwtencrypt(
                text, self.secret, expire_seconds=self.expire_secs
            ),
        }

    def verify(self, c_text: str, c_hash: str) -> bool:
        """Verify CAPTCHA response. Return True if valid, False if invalid.

        Args:
            c_text (str): The CAPTCHA text to verify.
            c_hash (str): The jwt to verify (from the hidden input field)

        Returns:
            bool: True if valid, False if invalid.
        """
        # handle parameter reversed order
        if len(c_text.split('.')) == 3:
            # jwt was passed as 1st arg correct
            c_text, c_hash = c_hash, c_text

        if c_hash in self.verified_captchas:
            return False

        decoded_text = jwtdecrypt(
            c_hash, c_text, self.config['SECRET_CAPTCHA_KEY']
        )

        # token expired or invalid
        if decoded_text is None:
            return False

        if self.only_upper:
            decoded_text, c_text = decoded_text.upper(), c_text.upper()

        if decoded_text == c_text:
            self.verified_captchas.add(c_hash)
            return True
        return False

    def captcha_html(self, captcha: dict) -> str:
        """
        Generate HTML for the CAPTCHA image and input fields.

        Args:
            captcha (dict): captcha dict with hash/img keys

        Returns:
            str: HTML string containing the CAPTCHA image and input fields.
        """
        img = (
            '<img class="simple-captcha-img" '
            + 'src="data:image/png;base64, %s" />' % captcha['img']
        )

        inpu = (
            '<input type="text" class="simple-captcha-text"'
            + 'name="captcha-text">\n'
            + '<input type="hidden" name="captcha-hash" '
            + 'value="%s">' % captcha['hash']
        )

        return '%s\n%s' % (img, inpu)

    def init_app(self, app):
        app.jinja_env.globals.update(captcha_html=self.captcha_html)

        return app

    def __repr__(self):
        return '<CAPTCHA %r>' % self.config
