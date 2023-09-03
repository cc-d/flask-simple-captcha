import string
from typing import Optional, Union, Set, Tuple

CHARPOOL = tuple(set(string.ascii_uppercase))
EXCHARS = tuple(set('oOlI1'))

DEFAULT_CONFIG = {
    'SECRET_CAPTCHA_KEY': 'LONG SECRET KEY HERE',  # use for JWT encoding/decoding
    'CAPTCHA_LENGTH': 6,  # Length of the generated CAPTCHA text
    'CAPTCHA_DIGITS': False,  # Should digits be added to the character pool?
    # EXPIRE_SECONDS will take prioritity over EXPIRE_MINUTES if both are set.
    'EXPIRE_SECONDS': 60 * 10,
    #'EXPIRE_MINUTES': 10, # backwards compatibility concerns supports this too
    #'EXCLUDE_VISUALLY_SIMILAR': True,  # Optional
    #'ONLY_UPPERCASE': True,  # Optional
    #'CHARACTER_POOL': 'AaBb',  # Optional
}

if (
    'EXPIRE_MINUTES' in DEFAULT_CONFIG
    and 'EXPIRE_SECONDS' not in DEFAULT_CONFIG
):
    EXPIRE_NORMALIZED = DEFAULT_CONFIG['EXPIRE_MINUTES'] * 60
else:
    EXPIRE_NORMALIZED = DEFAULT_CONFIG['EXPIRE_SECONDS']
