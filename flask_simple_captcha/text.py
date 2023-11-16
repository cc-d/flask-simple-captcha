import os
import os.path as op
import re
from typing import Optional, List, Tuple, Union
from glob import glob


class CaptchaFont:
    def __init__(self, path: str):
        self.filename = op.basename(path)
        self.name = '.'.join(self.filename.split('.')[:-1])
        self.path = path

    def __repr__(self):
        return '<CaptchaFont %r>' % self.name


FONTS_DIR = op.join(op.dirname(op.abspath(__file__)), 'fonts')
FONT_PATHS = glob(op.join(FONTS_DIR, '*.ttf'))
FONT_NAMES = [op.basename(p) for p in FONT_PATHS]

CAPTCHA_FONTS = [CaptchaFont(p) for p in FONT_PATHS]


def get_font(
    name: str, font_pool: list = CAPTCHA_FONTS
) -> Optional[CaptchaFont]:
    """Get a CaptchaFont object by name or filename or path str
    Args:
        name (str): The name, filename, or path of the font
        font_pool (list, optional): list of CaptchaFont objects to search.
            Defaults to CAPTCHA_FONTS.
    Returns:
        CaptchaFont: The CaptchaFont object if found, else None
    """
    for font in font_pool:
        if font.name == name:
            return font
        elif font.filename == name:
            return font
        elif font.path == name:
            return font
    return None
