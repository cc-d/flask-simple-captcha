import string
from random import choice as rchoice
from PIL import Image
from typing import Tuple
from uuid import uuid4
from .config import DEFAULT_CONFIG

from .utils import (
    jwtencrypt,
    jwtdecrypt,
    gen_captcha_text,
    CHARPOOL,
    exclude_similar_chars,
)

from .img import (
    convert_b64img as new_convert_b64img,
    draw_lines as new_draw_lines,
    create_text_img,
)
from .text import CAPTCHA_FONTS, get_font


class CAPTCHA:
    """CAPTCHA class to generate and validate CAPTCHAs."""

    def __init__(self, config: dict):
        """Initialize CAPTCHA with default configuration."""
        self.config = {**DEFAULT_CONFIG, **config}
        self.verified_captchas = set()
        self.secret = self.config['SECRET_CAPTCHA_KEY']

        # jwt expiration time
        if 'EXPIRE_NORMALIZED' in config:
            self.expire_secs = config['EXPIRE_NORMALIZED']
        elif 'EXPIRE_SECONDS' in config:
            self.expire_secs = config['EXPIRE_SECONDS']
        elif 'EXPIRE_MINUTES' in config and 'EXPIRE_SECONDS' not in config:
            self.expire_secs = config['EXPIRE_MINUTES'] * 60
        else:
            self.expire_secs = DEFAULT_CONFIG['EXPIRE_SECONDS']

        # character pool
        if 'CHARACTER_POOL' in self.config:
            chars = self.config['CHARACTER_POOL']
        else:
            chars = ''.join(CHARPOOL)

        # uppercase characters
        if (
            'ONLY_UPPERCASE' in self.config
            and self.config['ONLY_UPPERCASE'] is False
        ):
            chars = ''.join(set(c for c in chars))
            self.only_upper = False
        else:
            chars = ''.join(set(c.upper() for c in chars))
            self.only_upper = True

        # digits
        if self.config['CAPTCHA_DIGITS']:
            chars += string.digits

        # visually similar characters
        if self.config['EXCLUDE_VISUALLY_SIMILAR']:
            chars = exclude_similar_chars(chars)

        self.characters = tuple(set(chars))

        # img format
        self.img_format = self.config['CAPTCHA_IMG_FORMAT']

        # fonts
        self.fonts = CAPTCHA_FONTS

        # if USE_TEXT_FONTS is set in config, only use those fonts
        if 'USE_TEXT_FONTS' in self.config:
            self.fonts = []
            for fntname in self.config['USE_TEXT_FONTS']:
                fnt = get_font(fntname, CAPTCHA_FONTS)
                if fnt is not None:
                    self.fonts.append(fnt)

    def get_background(self, text_size: Tuple[int, int]) -> Image:
        """preserved for backwards compatibility"""
        return Image.new(
            'RGBA',
            (int(text_size[0]), int(text_size[1])),
            color=(0, 0, 0, 255),
        )

    def convert_b64img(self, *args, **kwargs) -> str:
        """preserved for backwards compatibility"""
        return new_convert_b64img(*args, **kwargs)

    def draw_lines(self, *args, **kwargs) -> Image:
        """preserved for backwards compatibility"""
        return new_draw_lines(*args, **kwargs)

    def create(self, length=None, digits=None) -> str:
        """Create a new CAPTCHA dict and add it to self.captchas"""
        # backwards compatibility
        length = self.config['CAPTCHA_LENGTH'] if length is None else length
        add_digits = (
            self.config['CAPTCHA_DIGITS'] if digits is None else digits
        )

        text = gen_captcha_text(
            length=length, add_digits=add_digits, charpool=self.characters
        )
        out_img = create_text_img(
            text,
            rchoice(self.fonts).path,
            back_color=self.config['BACKGROUND_COLOR'],
            text_color=self.config['TEXT_COLOR'],
        )

        return {
            'img': self.convert_b64img(out_img, self.img_format),
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
        mimetype = 'image/png' if self.img_format == 'PNG' else 'image/jpeg'
        img = (
            '<img class="simple-captcha-img" '
            + 'src="data:%s;base64, %s" />' % (mimetype, captcha['img'])
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
