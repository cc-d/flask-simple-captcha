#!/usr/bin/env python3
import base64
import os
import random
import string
import sys

from os.path import dirname, abspath, join as pjoin

FSC_DIR = dirname(abspath(__file__))
ROOT_DIR = dirname(FSC_DIR)
if FSC_DIR not in sys.path:
    sys.path.insert(0, FSC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, Tuple, Generator, List, Set, Union, Optional
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont
from flask_simple_captcha.utils import CaptchaHash, default_repr
from werkzeug.security import check_password_hash, generate_password_hash
from config import DEFAULT_CONFIG


class CAPTCHA:
    def __init__(self, config: dict):
        """Initialize CAPTCHA with default configuration."""
        self.config = DEFAULT_CONFIG.copy()
        self.config.update(
            config
        )  # Update with provided config for 3.7 compatibility
        self.unique_salt = ''.join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(self.config['UNIQUE_SALT_LENGTH'])
        )
        self.captchas = {}  # A dictionary to store the CAPTCHA data
        self.characters = string.ascii_uppercase
        if self.config['CAPTCHA_DIGITS']:
            self.characters += string.digits
        self.verified_ids = set()

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

        caphash = CaptchaHash(
            b64img=self.convert_b64img(out),
            text=text,
            method=self.config['METHOD'],
            unique_salt=self.unique_salt,
            c_hash=c_hash,
            secret_key=c_key,
            expires_minutes=self.config['EXPIRE_MINUTES'],
        )
        self.captchas[caphash.uuid] = caphash
        return caphash

    def convert_b64img(self, out):
        byte_array = BytesIO()
        out.save(byte_array, format='PNG')
        byte_array = byte_array.getvalue()

        b64image = base64.b64encode(byte_array)
        b64image = str(b64image)
        b64image = b64image[2:][:-1]

        return b64image

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

    def verify(self, c_text: str, c_hash: str) -> bool:
        """Verify CAPTCHA response. Return True if valid, False if invalid.

        !! IMPORTANT !! THE C_HASH PARAMETER IS ACTUALLY THE UUID
            THIS WAS NECESSARY FOR BACKWARDS COMPATABILITY REASONS

        Args:
            c_text (str): The CAPTCHA text to verify
            c_hash (str): The CAPTCHA uuid to verify (NOT THE HASH)

        Returns:
            bool: True if valid, False if invalid
        """
        captcha_uuid = (
            c_hash  # Necessary for legacy/backwards compatibility reasons
        )

        self.cleanup_old_hashes()

        if captcha_uuid in self.verified_ids:
            return False

        c_datetime = self.captchas.get(captcha_uuid, None)
        if c_datetime is None:
            return
        c_key = (
            c_text + self.config['SECRET_CAPTCHA_KEY'] + c_datetime.unique_salt
        )

        c_hash = c_datetime.hash
        # Verification passed, so remove the CAPTCHA data
        if check_password_hash(c_hash, c_key):
            # self.verified_ids.add(captcha_uuid)
            del self.captchas[captcha_uuid]
            return True

        return False

    from logfunc import logf

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


if __name__ == '__main__':
    print(CAPTCHA().create())
