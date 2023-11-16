import string
from glob import glob
from typing import Optional, Union, Set, Tuple

CHARPOOL = tuple(set(string.ascii_uppercase))
EXCHARS = tuple(set('oOlI1'))

DEFAULT_CONFIG = {
    'SECRET_CAPTCHA_KEY': 'LONGKEY',  # use for JWT encoding/decoding
    # CAPTCHA GENERATION SETTINGS
    'EXPIRE_SECONDS': 60 * 10,  # takes precedence over EXPIRE_MINUTES
    'CAPTCHA_IMG_FORMAT': 'JPEG',  # 'PNG' or 'JPEG' (JPEG is 3X faster)
    # CAPTCHA TEXT SETTINGS
    'CAPTCHA_LENGTH': 6,  # Length of the generated CAPTCHA text
    'CAPTCHA_DIGITS': False,  # Should digits be added to the character pool?
    'EXCLUDE_VISUALLY_SIMILAR': True,  # Exclude visually similar characters
    'TEXT_FONT_SIZE': 30,  # Font size of the CAPTCHA text
    'VARY_FONT_SIZE': True,  # Vary the font size of the CAPTCHA text
    'VARY_FONT_RANGE': 2,  # Range of font size variation up/down
    #
    # Optional/Backwards Compatability settings
    #'USE_TEXT_FONTS': ['arial', 'roboto-mono'], # Only use these fonts in ./fonts
    #'EXPIRE_MINUTES': 10, # backwards compatibility concerns supports this too
    #'EXCLUDE_VISUALLY_SIMILAR': True,  # Optional
    #'ONLY_UPPERCASE': True,  # Optional
    #'CHARACTER_POOL': 'AaBb',  # Optional
}

EXPIRE_NORMALIZED = DEFAULT_CONFIG['EXPIRE_SECONDS']
