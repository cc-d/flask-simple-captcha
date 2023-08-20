import sys
from os.path import dirname, abspath, join as pjoin

FSC_DIR = dirname(abspath(__file__))
ROOT_DIR = dirname(FSC_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from flask_simple_captcha.captcha_generation import (
    CAPTCHA,
    DEFAULT_CONFIG,
    gen_captcha_key,
)
from flask_simple_captcha.captcha_hash import CaptchaHash

print(locals(), globals())
print('\n', vars(CAPTCHA))
