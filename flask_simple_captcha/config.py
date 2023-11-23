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
    'BACKGROUND_COLOR': (0, 0, 0),  # RGB(A?) background color (default black)
    'TEXT_COLOR': (255, 255, 255),  # RGB(A?) text color (default white)
    # Optional/Backwards Compatability settings
    #'EXPIRE_MINUTES': 10, # backwards compatibility concerns supports this too
    #'EXCLUDE_VISUALLY_SIMILAR': True,  # Optional
    #'ONLY_UPPERCASE': True,  # Optional
    #'CHARACTER_POOL': 'AaBb',  # Optional
    #'USE_TEXT_FONTS': ['RobotoMono-Bold'], # Only use these fonts in ./fonts
}

EXPIRE_NORMALIZED = DEFAULT_CONFIG['EXPIRE_SECONDS']

# should add these to config and allow users to change them
IMGHEIGHT = 60
IMGWIDTH = 180
FONTSIZE = 30
