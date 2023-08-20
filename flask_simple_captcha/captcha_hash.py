import random
import re
import string
from datetime import datetime, timedelta
from typing import Generator, List, Optional, Set, Union
from uuid import uuid4

from flask_simple_captcha.config import DEFAULT_CONFIG
from myfuncs import default_repr
from werkzeug.security import check_password_hash, generate_password_hash

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
        self.text = str(text).upper()
        self.created = datetime.now()
        self.expires = self.created + timedelta(minutes=expires_minutes)
        self.unique_salt = unique_salt
        self.method = method

    def __repr__(self) -> str:
        return default_repr(self)

    def expired(self) -> bool:
        """Check if the CAPTCHA has expired.

        Returns:
            bool: True if expired, False otherwise.
        """
        return datetime.now() > self.expires

    def verify_text(self, user_input: str) -> bool:
        """Verify the user's input against the CAPTCHA text.

        Args:
            user_input (str): User's input to verify.

        Returns:
            bool: True if the input is correct, False otherwise.
        """
        # Consider utilizing the unique_salt and method here if needed for verification
        return check_password_hash(
            self.hash,
            self.unique_salt + self.text + self.config['SECRET_CAPTCHA_KEY'],
        )
