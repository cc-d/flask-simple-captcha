"""
legacy file, kept around for off chance somebody is relying
on backwards compatability, all functionality should go in __init__.py
"""
import os
import re
import time
import inspect
import random
import string
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union

import logging

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Callable[..., Any])

ASCII_CHARS = string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase


def trunc_str(string: str, max_length: int) -> str:
    """
    Truncates a string if its length exceeds the specified maximum length.
    If the string is truncated, it appends '...' to indicate the truncation.

    Args:
        string (str): The string to truncate.
        max_length (int): The maximum length of the truncated string.

    Returns:
        str: The truncated string.
    """
    if len(string) > max_length:
        return string[:max_length - 3] + "..."
    return string


# legacy use the logfunc pip package instead
def logf(
    level: Optional[Union[int, str]] = logging.DEBUG,
    log_args: bool = True,
    log_return: bool = True,
    max_str_len: int = 1000,
    measure_time: bool = True
) -> Callable[[T], T]:
    """
    A decorator that logs the execution time, function name, arguments, keyword arguments,
    and return value of a function using a specified log level.

    Args:
        level (Union[int, str], optional): The log level to use for logging. Defaults to logging.DEBUG.
        log_args (bool, optional): Should the function arguments be logged? Defaults to True.
        log_return (bool, optional): Should function return be logged? Defaults to True.
        max_str_len (int, optional): Maximum length of the logged arguments and return values. Defaults to 1000.
        measure_time (bool, optional): Should the function execution time be measured? Defaults to True.

    Returns:
        Callable[[T], T]: The wrapped function.
    """
    if isinstance(level, str):
        level_int = logging.getLevelName(level.upper())
    else:
        level_int = int(level)

    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Start the timer if required and execute the function.
            start_time = time.time() if measure_time else None

            # Log function arguments if required
            if log_args:
                arg_str = f"{func.__name__}() | {str(args)[:max_str_len]} {str(kwargs)[:max_str_len]}"
            else:
                arg_str = f"{func.__name__}()"

            logger.log(level_int, arg_str)

            # Execute the function
            result = func(*args, **kwargs)

            if measure_time:
                end_time = time.time()
                # Calculate the execution time and format the log message.
                exec_time = end_time - start_time
                exec_time_str = f"{exec_time:.5f}s"

            # Log the return value and execution time if required
            if log_return and measure_time:
                result_str = trunc_str(str(result), max_str_len)
                log_message = f"{func.__name__}() {exec_time_str} | {result_str}"
            elif log_return:
                result_str = trunc_str(str(result), max_str_len)
                log_message = f"{func.__name__}() | {result_str}"
            elif measure_time:
                log_message = f"{func.__name__}() {exec_time_str}"
            else:
                log_message = None

            if log_message is not None:
                # Log the message using the specified level.
                logger.log(level_int, log_message)

            return result
        return wrapper
    return decorator


@logf()
def ran_str(length: int) -> str:
    """ Returns a string of random ascii characters of n length

    Args:
        length (int): length of returned str

    Returns:
        str: random char string of n length
    """
    s = ''
    for i in range(0, length):
        s += random.choice(ASCII_CHARS)
    return s



@logf()
def get_asctime() -> str:
    """Returns the current time in the same format as logging %(asctime)s


    Returns:
        str: current asctime
    """
    now = datetime.now()
    return now.strftime(f"%Y-%m-%d %H:%M:%S")


@logf()
def valid_uuid(string):
    regex = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[0-9a-f]{4}-[0-9a-f]{12}$')
    return bool(regex.match(string))