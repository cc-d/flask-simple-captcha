import inspect
import subprocess as subproc
import sys
import os
import string
from json import loads, dumps
from typing import (
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    Any,
    Iterable,
    Generator,
    Callable,
    Optional,
)

import random

ALPHANUMERIC_CHARS = string.ascii_letters + string.digits
USERNAME_ASCII_CHARS = ALPHANUMERIC_CHARS + '_-'


def nlprint(*args, **kwargs) -> None:
    """Identical to normal print() but also prints an extra \n above/below"""
    print()
    print(*args, **kwargs)
    print()


def is_jwt_str(s: str) -> bool:
    """Check if a string is an encrypted JWT"""
    parts = str(s).split('.')
    return len(parts) == 3


def ranstr(
    min_length: int = 16,
    max_length: int = 32,
    chars: Iterable = ALPHANUMERIC_CHARS,
    as_generator: bool = False,
) -> Union[Generator, str]:
    """Generate a random string of specified length and characters between min_length and max_length.

    Args:
        min_length (int, optional): The length of the string. Defaults to 16.
        max_length (int, optional): The maximum length of the string. Defaults to 32.
        chars (Iterable, optional): The characters to be used for generating the string.
            Defaults to ALPHANUMERIC_CHARS.
        as_generator (bool, optional): Specifies whether to return a generator instead of a string.
            Defaults to False.
    Returns:
        Union[Generator, str]: The generated string if `as_generator` is False.
            A generator if `as_generator` is True.
    """
    length = random.randint(min_length, max_length)
    if as_generator:
        return (random.choice(chars) for _ in range(length))
    return ''.join(random.choice(chars) for _ in range(length))


def runcmd(
    cmd: str, output: bool = True, *args, **kwargs
) -> Optional[List[str]]:
    """
    Run a command in the shell.

    Args:
        cmd (str): The command to be executed.
        output (bool, optional): Specifies whether to capture and return the output of the command.
            Defaults to True.
        *args: Additional positional arguments to be passed to subprocess.run().
        **kwargs: Additional keyword arguments to be passed to subprocess.run().

    Returns:
        Optional[List[str]]: The captured output of the command as a list of lines if `output` is True.
            None if `output` is False.

    Raises:
        CalledProcessError: If the command exits with a non-zero status and `check=True`.

    """
    if output:
        return subproc.run(
            [c for c in cmd.split()],
            check=True,
            text=True,
            capture_output=True,
            *args,
            **kwargs,
        ).stdout.splitlines()
    else:
        subproc.run(
            [c for c in cmd.split()],
            check=False,
            text=False,
            capture_output=False,
            *args,
            **kwargs,
        )


def get_terminal_width(default: int = 80) -> int:
    """Returns the terminal width. If not detectable, returns default value."""
    try:
        return os.get_terminal_size().columns
    except OSError:
        return default


def print_middle(obj: any, char: str = '=', noprint: bool = False) -> str:
    """
    Print the string representation of an object centered in a line of characters
    based on the terminal width.

    Args:
        obj (Any): The object whose string representation needs to be printed.
        char (str, optional): The character used for filling. Defaults to '='.
        noprint (bool, optional): Specifies whether to avoid printing the generated string.
            Defaults to False.

    Returns:
        str: The generated string.
    """
    terminal_width = get_terminal_width()
    obj_str = str(obj)

    # Calculate the padding on each side. If the total length is odd,
    # the extra space will be on the right side.
    padding = (terminal_width - len(obj_str) - 2) // 2

    result = char * padding + ' ' + obj_str + ' ' + char * padding

    if not noprint:
        print(result)
    return result


def print_columns(iterable: Iterable, separator: str = "  ") -> None:
    objs = list(sorted(iterable))  # Convert any iterable to a list
    terminal_width = get_terminal_width()

    # Calculate max length of str representation of all objects
    max_length = max(len(str(obj)) for obj in objs)

    # Calculate the width of one column, including its separator
    column_width = max_length + len(separator)

    # Calculate number of columns that can fit in terminal width
    num_columns = terminal_width // column_width

    # Adjust if terminal_width is smaller than max_length
    num_columns = max(1, num_columns)

    # Calculate the number of rows needed
    num_rows = -(-len(objs) // num_columns)  # ceiling division

    # Print the objects in rows
    for row in range(num_rows):
        line = []
        for col in range(num_columns):
            index = (
                row * num_columns + col
            )  # This line is correct for row-first printing
            if index < len(objs):
                line.append(str(objs[index]).ljust(max_length))
        print(separator.join(line))


def objinfo(obj: Any):
    """Print information about an object."""
    terminal_width = get_terminal_width()

    obj_type = type(obj)
    obj_name = obj.__name__ if hasattr(obj, "__name__") else "N/A"
    obj_attrs = sorted(
        str(attr) for attr in dir(obj) if not callable(getattr(obj, attr))
    )
    obj_methods = sorted(
        str(method) for method in dir(obj) if callable(getattr(obj, method))
    )
    obj_doc = inspect.getdoc(obj) or "No documentation available."
    obj_scope = (
        "Local"
        if obj in inspect.currentframe().f_back.f_locals.values()
        else "Global"
    )
    obj_size = sys.getsizeof(obj)
    obj_mutability = "Mutable" if hasattr(obj, "__dict__") else "Immutable"
    obj_identity = id(obj)

    def print_info():
        header = f"{obj_name} ({obj_type})"
        subheader = (
            f"Size: {obj_size}",
            f"Scope: {obj_scope}",
            f"Mutability: {obj_mutability}",
            f"Identity: {obj_identity}",
        )
        print()
        print_middle(header)
        print()
        print_columns(subheader)
        nlprint(f'{print_middle("Attributes",  "-", noprint=True)}')
        print_columns(obj_attrs)
        nlprint(f'{print_middle("Methods", "-", noprint=True)}')
        print_columns(obj_methods)
        nlprint(f'{print_middle("Documentation", "-", noprint=True)}')
        print(obj_doc)
        nlprint('-' * terminal_width)

    print_info()


def recursive_json(obj):
    result = {}
    for k, v in obj.__dict__.items():
        if hasattr(v, '__dict__'):
            result[k] = recursive_json(v)
        else:
            result[k] = v
    return result


def default_repr(obj: Any, transform: Optional[Callable] = None, json: bool = False, *args, **kwargs) -> str:
    if json and hasattr(obj, '__dict__'):
        return dumps(dict(recursive_json(obj)), indent=2, *args, **kwargs)

    if hasattr(obj, '__dict__'):
        attributes = ', '.join(
            f"{key}={value!r}"
            if not hasattr(value, '__dict__')
            else f"{key}={default_repr(value)}"
            for key, value in obj.__dict__.items()
            if not callable(value) and not str(key).startswith("_")
        )
        return f"{obj.__class__.__name__}({attributes})"
    else:
        if isinstance(obj, int):
            return 'int(%s)' % obj
        elif isinstance(obj, float):
            return 'float(%s)' % obj
        elif isinstance(obj, str):
            return 'str(%s)' % obj
        elif isinstance(obj, set):
            return 'set(%s)' % obj
        elif True in {isinstance(obj, t) for t in (list, tuple, dict)}:
            return str(obj)

        attributes = ', '.join(
            f"{attr}={getattr(obj, str(attr))}"
            for attr in dir(obj)
            if not callable(getattr(obj, str(attr))) and not str(attr).startswith("_")
        )
        return f"{obj.__class__.__name__}({attributes})"

    # Catch-all return statement
    return str(obj)
