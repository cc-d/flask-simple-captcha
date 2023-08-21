import base64
import random
import string
import os
import sys
import json
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple
from uuid import uuid4
from werkzeug.security import check_password_hash, generate_password_hash
from .config import DEFAULT_CONFIG
from myfuncs import default_repr

from .utils import jwtencode, jwtdecode, CHARPOOL, gen_captcha_text


class CAPTCHA:
    """CAPTCHA class to generate and validate CAPTCHAs."""

    def __init__(self, config: dict):
        """Initialize CAPTCHA with default configuration."""
        self.config = {**DEFAULT_CONFIG, **config}
        self.characters = CHARPOOL

    def get_background(self, text_size: Tuple[int, int]) -> Image:
        """Generate a background image."""
        return Image.new(
            'RGBA',
            (int(text_size[0] * 1.25), int(text_size[1] * 1.5)),
            color=(0, 0, 0, 255),
        )

    def draw_lines(self, im, lines=25):
        draw = ImageDraw.Draw(im)

        for i in range(lines):
            if random.randint(0, 1) == 0:
                draw.line(
                    (
                        random.randint(0, im.size[0]),
                        0,
                        random.randint(0, im.size[0]),
                        im.size[1],
                    ),
                    width=2,
                )
            else:
                draw.ellipse(
                    (
                        random.randint(-80, im.size[0]),
                        random.randint(-80, -10),
                        random.randint(-80, im.size[0]),
                        im.size[1] + random.randint(10, 80),
                    ),
                    width=2,
                )
        return im

    def convert_b64img(self, out):
        byte_array = BytesIO()
        out.save(byte_array, format='PNG')
        byte_array = byte_array.getvalue()

        b64image = base64.b64encode(byte_array)
        b64image = str(b64image)
        b64image = b64image[2:][:-1]

        return b64image

    def create(self, length=None, digits=None) -> str:
        """Create a new CAPTCHA dict and add it to self.captchas"""
        length = self.config['CAPTCHA_LENGTH'] if length is None else length
        digits = self.config['CAPTCHA_DIGITS'] if digits is None else digits

        text = gen_captcha_text(
            length=length, digits=digits, charpool=self.characters
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

        text_size = fnt.getsize(text)
        text_size = (int(text_size[0] * 1), int(text_size[1] * 1))

        background = self.get_background(text_size)

        background.paste(
            text_img,
            box=(
                random.randint(0, background.size[0] - text_size[0]),
                random.randint(0, background.size[1] - text_size[1]),
            ),
        )

        out = background.resize((200, 60))
        out = self.draw_lines(out)

        return {
            'img': self.convert_b64img(out),
            'text': text,
            'hash': jwtencode(
                text,
                self.config['SECRET_CAPTCHA_KEY'],
                self.config['EXPIRE_MINUTES'],
            ),
        }

    def verify(self, token: str, c_text: str) -> bool:
        """Verify CAPTCHA response. Return True if valid, False if invalid.

        Args:
            token (str): The JWT token for the CAPTCHA.
            c_text (str): The CAPTCHA text to verify.

        Returns:
            bool: True if valid, False if invalid.
        """
        decoded_text = jwtdecode(token, self.config['SECRET_CAPTCHA_KEY'])
        return str(decoded_text).upper() == str(c_text).upper()

    def captcha_html(self, img: str, jwt_str: str) -> str:
        """
        Generate HTML for the CAPTCHA image and input fields.

        Args:
            b64img (str): Base64 encoded CAPTCHA image.
            jwt_str (str): JWT string representing the CAPTCHA.

        Returns:
            str: HTML string containing the CAPTCHA image and input fields.
        """
        img = (
            '<img class="simple-captcha-img" '
            + 'src="data:image/png;base64, %s" />' % img
        )

        inpu = (
            '<input type="text" class="simple-captcha-text"'
            + 'name="captcha-text">\n'
            + '<input type="hidden" name="captcha-hash" '
            + 'value="%s">' % jwt_str
        )

        return '%s\n%s' % (img, inpu)

    def init_app(self, app):
        app.jinja_env.globals.update(captcha_html=self.captcha_html)

        return app

    def __repr__(self):
        return default_repr(self)
