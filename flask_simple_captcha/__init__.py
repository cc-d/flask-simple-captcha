#!/usr/bin/env python3
import base64
import string
import random
import os
import datetime
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
}


class CAPTCHA:

    def __init__(self, config: dict):
        self.config = DEFAULT_CONFIG
        for key in config.keys():
            self.config[key] = config[key]

        self.unique_salt = ''.join(
            random.choice(string.ascii_letters + string.digits) for _ in range(16)
        )
        self.captcha_data = {}  # A dictionary to store the CAPTCHA data
        self.characters = string.ascii_uppercase
        if self.config['CAPTCHA_DIGITS']:
            self.characters = self.characters + string.digits
        self.verified_ids = set()

    def get_background(self, text_size):
        background = Image.new(
            'RGBA',
            (int(text_size[0] * 1.25), int(text_size[1] * 1.5)),
            color=(0, 0, 0, 255),
        )
        return background

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

    def create(self, length=None, digits=None):
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

        self.captcha_data[c_hash] = {'id': unique_id, 'timestamp': datetime.now()}

        c_hash = c_hash.replace(self.config['METHOD'] + '$', '')


        print(self.captcha_data)

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
            + 'value="%s">' % captcha['hash']
        )

        return '%s\n%s' % (img, inpu)

    def verify(self, c_text, c_hash, c_key=None):
        self.cleanup_old_hashes()

        c_hash = self.config['METHOD'] + '$' + c_hash

        # Check if the CAPTCHA data exists
        captcha_hash = self.captcha_data.get(c_hash)

        if captcha_hash is None:
            return False

        c_id = captcha_hash['id']
        if c_id in self.verified_ids:
            return False

        c_text = c_text.upper()

        c_key = c_text + self.config['SECRET_CAPTCHA_KEY'] + self.unique_salt

        # Verification passed, so remove the CAPTCHA data
        print(self.captcha_data)
        print(c_hash)
        print(c_key)
        if check_password_hash(c_hash, c_key):
            del self.captcha_data[c_hash]
            return True
        return False

    def cleanup_old_hashes(self):
        # Set the time limit for valid hashes
        time_limit = datetime.now() - timedelta(minutes=1)

        # Remove hashes older than the time limit
        old_hashes = [
            hash_key
            for hash_key, data in self.captcha_data.items()
            if data['timestamp'] < time_limit
        ]
        for hash_key in old_hashes:
            del self.captcha_data[hash_key]

    def init_app(self, app):
        app.jinja_env.globals.update(captcha_html=self.captcha_html)

        return app


if __name__ == '__main__':
    print(CAPTCHA().create())
