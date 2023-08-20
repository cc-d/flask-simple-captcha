import sys
from os.path import dirname, abspath, join as pjoin

FSC_DIR = dirname(abspath(__file__))
ROOT_DIR = dirname(FSC_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from .captcha import CAPTCHA, DEFAULT_CONFIG
from .utils import CaptchaHash, default_repr

print(locals(), globals())
print('\n', vars(CAPTCHA))
