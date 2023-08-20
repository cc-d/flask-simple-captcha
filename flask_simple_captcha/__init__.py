#!/usr/bin/env python3
from typing import Tuple, Dict
import base64
import string
import random
import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash


DEFAULT_CONFIG = {
    'SECRET_CAPTCHA_KEY': 'CHANGEME - 40 or 50 character long key here',
    'METHOD': 'pbkdf2:sha256:100',
    'CAPTCHA_LENGTH': 6,
    'CAPTCHA_DIGITS': False,
    'EXPIRE_MINUTES': 15,
}


class CAPTCHA:
    def __init__(self, config: dict):
        """Initialize CAPTCHA with default configuration."""
        self.config = DEFAULT_CONFIG.copy()
        self.config.update(config)  # Update with provided config for 3.7 compatibility
        self.unique_salt = ''.join(
            random.choice(string.ascii_letters + string.digits) for _ in range(16)
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

    def create(self, length=None, digits=None) -> dict:
        """Create a new CAPTCHA dict and add it to self.captchas"""
        length = self.config['CAPTCHA_LENGTH'] if length is None else length
        digits = self.config['CAPTCHA_DIGITS'] if digits is None else digits

        self.cleanup_old_hashes()

        text = ''.join([random.choice(self.characters) for i in range(length)])
        text = text.upper()

        # Concatenate the unique salt with the text and secret key to generate the hash
        c_key = text + self.config['SECRET_CAPTCHA_KEY'] + self.unique_salt

        c_hash = generate_password_hash(
            c_key, method=self.config['METHOD'], salt_length=8
        )

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

        self.captchas[unique_id] = {'hash': c_hash, 'timestamp': datetime.now()}

        return {
            'img': self.convert_b64img(out),
            'text': text,
            'hash': c_hash,
            'id': unique_id,
        }

    def convert_b64img(self, out):
        byte_array = BytesIO()
        out.save(byte_array, format='PNG')
        byte_array = byte_array.getvalue()

        b64image = base64.b64encode(byte_array)
        b64image = str(b64image)
        b64image = b64image[2:][:-1]

        return b64image

    def captcha_html(self, captcha):
        img = (
            '<img class="simple-captcha-img" '
            + 'src="data:image/png;base64, %s" />' % captcha['img']
        )

        inpu = (
            '<input type="text" class="simple-captcha-text"'
            + 'name="captcha-text">\n'
            + '<input type="hidden" name="captcha-hash" '
            + 'value="%s">' % captcha['id']
        )

        return '%s\n%s' % (img, inpu)

    def verify(self, c_text: str, c_hash: str) -> bool:
        """Verify CAPTCHA response.

        Note: The hash was previously used for submissions, but now the UUID is used instead.
        """
        self.cleanup_old_hashes()
        captcha_uuid = c_hash  # Necessary for legacy/backwards compatibility reasons

        if captcha_uuid in self.verified_ids or captcha_uuid not in self.captchas:
            return False

        captcha_dict = self.captchas.get(captcha_uuid)
        c_hash = captcha_dict['hash']
        c_text = c_text.upper()
        c_key = c_text + self.config['SECRET_CAPTCHA_KEY'] + self.unique_salt

        # Verification passed, so remove the CAPTCHA data
        if check_password_hash(c_hash, c_key):
            del self.captchas[captcha_uuid]
            self.verified_ids.add(captcha_uuid)  # Store verified IDs
            return True

        return False

    def cleanup_old_hashes(self):
        # Set the time limit for valid hashes
        time_limit = datetime.now() - timedelta(minutes=self.config['EXPIRE_MINUTES'])

        # Remove hashes older than the time limit
        old_uuids = [
            uuid_key
            for uuid_key, data in self.captchas.items()
            if data['timestamp'] < time_limit
        ]
        for uuid_key in old_uuids:
            del self.captchas[uuid_key]

    def init_app(self, app):
        app.jinja_env.globals.update(captcha_html=self.captcha_html)

        return app


if __name__ == '__main__':
    print(CAPTCHA().create())
