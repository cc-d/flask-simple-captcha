from datetime import datetime, timedelta
import jwt
from flask_simple_captcha.config import DEFAULT_CONFIG
from typing import Optional
import string
import random


def jwtencode(
    text: str,
    secret_key: str = DEFAULT_CONFIG['SECRET_CAPTCHA_KEY'],
    expire_seconds: int = DEFAULT_CONFIG['EXPIRE_NORMALIZED'],
) -> str:
    """
    Encode the CAPTCHA text into a JWT token.

    Args:
        text (str): The CAPTCHA text to be encoded.
        secret_key (str, optional): The secret key for JWT encoding. Defaults to value in DEFAULT_CONFIG.
        expire_seconds (int, optional): The expiration time for the token in seconds.
            Defaults to config EXPIRE_NORMALIZED.

    Returns:
        str: The encoded JWT token.
    """
    payload = {
        'text': text,
        'exp': datetime.utcnow() + timedelta(seconds=expire_seconds),
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')


def jwtdecode(
    token: str, secret_key: str = DEFAULT_CONFIG['SECRET_CAPTCHA_KEY']
) -> Optional[str]:
    """
    Decode the CAPTCHA text from a JWT token.

    Args:
        token (str): The JWT token to decode.
        secret_key (str, optional): The secret key for JWT decoding. Defaults to value in DEFAULT_CONFIG.

    Returns:
        Optional[str]: The decoded CAPTCHA text if valid, None if invalid.
    """
    try:
        return jwt.decode(token, secret_key, algorithms=['HS256'])['text']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


CHARPOOL = (
    string.ascii_uppercase + string.digits
    if DEFAULT_CONFIG['CAPTCHA_DIGITS']
    else string.ascii_uppercase
)


def gen_captcha_text(
    length: int = DEFAULT_CONFIG['CAPTCHA_LENGTH'],
    charpool: str = CHARPOOL,
    digits: bool = DEFAULT_CONFIG['CAPTCHA_DIGITS'],
) -> str:
    """
    Generate a random CAPTCHA text.

    Args:
        length (int, optional): The length of the CAPTCHA text.
            Defaults to value in DEFAULT_CONFIG.
        charpool (str, optional): The character pool to use for generating the CAPTCHA text.
            Defaults to value in CHARPOOL.
        digits (bool, optional): Whether to include digits in the character pool.
            Defaults to value in DEFAULT_CONFIG.
    Returns:
        str: The generated CAPTCHA text.
    """
    if digits:
        charpool += string.digits
    return ''.join(random.choice(charpool) for _ in range(length)).upper()
