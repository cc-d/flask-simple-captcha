import base64
import random
import string
import os
import sys
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple
from uuid import uuid4
from werkzeug.security import check_password_hash, generate_password_hash
from flask_simple_captcha.config import DEFAULT_CONFIG
from flask_simple_captcha.captcha_hash import CaptchaHash
from myfuncs import default_repr


class CAPTCHA:
    """CAPTCHA class to generate and validate CAPTCHAs."""

    CHARPOOL = (
        string.ascii_uppercase + string.digits
        if DEFAULT_CONFIG['CAPTCHA_DIGITS']
        else string.ascii_uppercase
    )

    def __init__(self, config: dict):
        """Initialize CAPTCHA with default configuration."""
        self.config = {**DEFAULT_CONFIG, **config}
        self.unique_salt = ''.join(
            random.choice(CAPTCHA.CHARPOOL)
            for _ in range(self.config['UNIQUE_SALT_LENGTH'])
        )
        self.captchas = {}  # A dictionary to store the CAPTCHA data
        self.characters = (
            string.ascii_uppercase + string.digits
            if self.config['CAPTCHA_DIGITS']
            else string.ascii_uppercase
        )

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

    def create(self, length=None, digits=None) -> CaptchaHash:
        """Create a new CAPTCHA dict and add it to self.captchas"""
        length = self.config['CAPTCHA_LENGTH'] if length is None else length
        digits = self.config['CAPTCHA_DIGITS'] if digits is None else digits

        self.cleanup_old_hashes()

        text = ''.join([random.choice(self.characters) for i in range(length)])
        text = text.upper()

        # Concatenate the unique salt with the text and secret key to generate the hash
        c_key = text + self.config['SECRET_CAPTCHA_KEY'] + self.unique_salt
        c_hash = generate_password_hash(c_key, method=self.config['METHOD'])
        unique_id = str(uuid4())

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

        # Generate unique hash
        captcha_hash = CaptchaHash(
            c_hash=gen_captcha_key(
                self.unique_salt,
                text,
                self.config['SECRET_CAPTCHA_KEY'],
                self.config['METHOD'],
            ),
            b64img=self.convert_b64img(out),
            text=text,
            unique_salt=self.unique_salt,
            secret_key=self.config['SECRET_CAPTCHA_KEY'],
            method=self.config['METHOD'],
            expires_minutes=self.config['EXPIRE_MINUTES'],
        )

        self.captchas[captcha_hash.uuid] = captcha_hash

        return captcha_hash

    def verify(self, c_text: str, c_hash: str) -> bool:
        """Verify CAPTCHA response. Return True if valid, False if invalid.

        Args:
            c_text (str): The CAPTCHA text to verify.
            c_hash (str): The CAPTCHA uuid to verify (NOT THE HASH).

        Returns:
            bool: True if valid, False if invalid.
        """
        if c_hash not in self.captchas:
            return False

        captcha_hash: CaptchaHash = self.captchas[c_hash]
        if captcha_hash.expired():
            del self.captchas[c_hash]
            return False

        if check_password_hash(
            captcha_hash.hash,
            self.unique_salt + c_text + self.config['SECRET_CAPTCHA_KEY'],
        ):
            del self.captchas[c_hash]
            return True

        return False

    def captcha_html(self, captcha: CaptchaHash):
        img = (
            '<img class="simple-captcha-img" '
            + 'src="data:image/png;base64, %s" />' % captcha.b64img
        )

        inpu = (
            '<input type="text" class="simple-captcha-text"'
            + 'name="captcha-text">\n'
            + '<input type="hidden" name="captcha-hash" '
            + 'value="%s">' % captcha.uuid
        )

        return '%s\n%s' % (img, inpu)

    def cleanup_old_hashes(self) -> dict:
        """Remove old CAPTCHA hashes from self.captchas."""
        now = datetime.now()
        for k, v in self.captchas.copy().items():
            if now >= v.expires:
                del self.captchas[k]

    def init_app(self, app):
        app.jinja_env.globals.update(captcha_html=self.captcha_html)

        return app

    def __repr__(self):
        return default_repr(self)


def gen_captcha_key(
    unique_salt: str, text: str, secret_key: str, method: str
) -> str:
    """Generate a CAPTCHA key.

    Args:
        unique_salt (str): Unique salt for the CAPTCHA.
        text (str): CAPTCHA text.
        secret_key (str): Secret key for the CAPTCHA.
        method (str): Hashing method.

    Returns:
        str: CAPTCHA key.
    """
    return generate_password_hash(
        unique_salt + text + secret_key, method=method
    )
