import base64
import os
import random
import string
import sys
from datetime import datetime, timedelta
from io import BytesIO
from typing import Iterable, Optional, Set, Tuple, Union

import jwt
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from .config import CHARPOOL, DEFAULT_CONFIG, EXCHARS, EXPIRE_NORMALIZED


def hash_text(
    text: str, secret_key: str = DEFAULT_CONFIG['SECRET_CAPTCHA_KEY']
) -> str:
    """
    Encrypt the CAPTCHA text.

    Args:
        text (str): The CAPTCHA text to be encrypted.
        secret_key (str, optional): The secret key for encryption.
            Defaults to value in DEFAULT_CONFIG.

    Returns:
        str: The encrypted CAPTCHA text.
    """
    salted_text = secret_key + text
    return generate_password_hash(salted_text)


def jwtencrypt(
    text: str,
    secret_key: str = DEFAULT_CONFIG['SECRET_CAPTCHA_KEY'],
    expire_seconds: int = EXPIRE_NORMALIZED,
) -> str:
    """
    Encode the CAPTCHA text into a JWT token.

    Args:
        text (str): The CAPTCHA text to be encoded.
        secret_key (str, optional): The secret key for JWT encoding.
            Defaults to value in DEFAULT_CONFIG.
        expire_seconds (int, optional): The expiration time for the token in seconds.
            Defaults to 600, 10 minutes.

    Returns:
        str: The encoded JWT token.
    """
    hashed_text = hash_text(text, secret_key)
    payload = {
        'hashed_text': hashed_text,
        'exp': datetime.utcnow() + timedelta(seconds=expire_seconds),
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')


def jwtdecrypt(
    token: str,
    original_text: str,
    secret_key: str = DEFAULT_CONFIG['SECRET_CAPTCHA_KEY'],
) -> Optional[str]:
    """
    Decode the CAPTCHA text from a JWT token.

    Args:
        token (str): The JWT token to decode.
        original_text (str): The original CAPTCHA text.
        secret_key (str, optional): The secret key for JWT decoding.

    Returns:
        Optional[str]: The decoded CAPTCHA text if valid, None if invalid.
    """
    try:
        decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
        if 'hashed_text' not in decoded:
            return None

        hashed_text = decoded['hashed_text']
        salted_original_text = secret_key + original_text

        # Verify if the hashed text matches the original text
        if check_password_hash(hashed_text, salted_original_text):
            return original_text
        else:
            return None

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def exclude_similar_chars(chars: Union[str, set, list, tuple]) -> str:
    """Excludes characters that are potentially visually confusing from
    the character pool (provided as charstr).

    Args:
        charstr (Union[str, set, list, tuple]): The character pool to exclude characters from.

    Returns:
        Union[str, set, list, tuple]: The character pool with
            visually confusing characters excluded.
    """
    if isinstance(chars, str):
        return ''.join({c for c in chars if c not in EXCHARS})
    elif isinstance(chars, set):
        return chars - set(EXCHARS)
    elif isinstance(chars, list):
        return [c for c in chars if c not in EXCHARS]
    else:
        return tuple(c for c in chars if c not in EXCHARS)


def gen_captcha_text(
    length: int = 6,
    add_digits: bool = False,
    exclude_similar: bool = True,
    charpool: Optional[Iterable] = None,
    only_uppercase: Optional[bool] = None,
) -> str:
    """Generate a random CAPTCHA text.
    Args:
        length (int): The length of the CAPTCHA text.
            Defaults to 6
        add_digits (bool): add digits to the character pool?
            Defaults to False
        exclude_similar (bool): exclude visually similar characters?
            from the character pool. Defaults to True.
        charpool (Iterable, optional): The character pool to
            generate the CAPTCHA text from. If this is provided, it will
            override the default character pool as well as add_digits.
            Defaults to None.
        only_uppercase (bool, optional): Only return uppercase characters. If
            a custom character pool is passed, only the uppercase characters will
            be used from that pool.
            Defaults to True.
    Returns:
        str: The generated CAPTCHA text.
    """
    if charpool is not None:
        if only_uppercase is True:
            charpool = tuple({c.upper() for c in charpool})
        else:
            charpool = tuple(charpool)
    else:
        charpool = CHARPOOL

    if exclude_similar:
        charpool = exclude_similar_chars(charpool)

    if add_digits:
        charpool += tuple(set(string.digits))

    return ''.join((random.choice(charpool) for _ in range(length)))
