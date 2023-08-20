from typing import Generator
from datetime import datetime, timedelta
from myfuncs import default_repr
from config import DEFAULT_CONFIG
from werkzeug.security import check_password_hash, generate_password_hash
from uuid import uuid4
import random
import re
import string

CHARPOOL = (
    string.ascii_uppercase
    if not DEFAULT_CONFIG['CAPTCHA_DIGITS']
    else string.ascii_uppercase + string.digits
)


class CaptchaHash:
    def __init__(
        self,
        b64img: str,
        text: str,
        unique_salt: str,
        c_hash: str,
        secret_key: str,
        usalt_len: int = DEFAULT_CONFIG['UNIQUE_SALT_LENGTH'],
        method: str = DEFAULT_CONFIG['METHOD'],
        expires_minutes: int = DEFAULT_CONFIG['EXPIRE_MINUTES'],
    ):
        self.secret_key = secret_key

        self.b64img = b64img
        self.hash = c_hash
        self.uuid = str(uuid4())
        self.b64 = b64img
        self.text = str(text).upper()
        self.created = datetime.now()
        self.expires = self.created + timedelta(expires_minutes)
        self.unique_salt = unique_salt
        self.method = method

    def __repr__(self) -> str:
        return default_repr(self)
