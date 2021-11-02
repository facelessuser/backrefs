"""
Utilities and compatibility abstraction.

Licensed under MIT
Copyright (c) 2015 - 2020 Isaac Muse <isaacmuse@gmail.com>
"""
import sys
import warnings
from typing import Tuple, Any, List

PY37 = (3, 7) <= sys.version_info

FMT_FIELD = 0
FMT_INDEX = 1
FMT_ATTR = 2
FMT_CONV = 3
FMT_SPEC = 4


class StringIter:
    """Preprocess replace tokens."""

    def __init__(self, text: str) -> None:
        """Initialize."""

        self._string = text
        self._index = 0

    def __iter__(self) -> "StringIter":
        """Iterate."""

        return self

    def __next__(self) -> str:
        """Python 3 iterator compatible next."""

        return self.iternext()

    @property
    def index(self) -> int:
        """Get Index."""

        return self._index

    def rewind(self, count: int) -> None:
        """Rewind index."""

        if count > self._index:  # pragma: no cover
            raise ValueError("Can't rewind past beginning!")

        self._index -= count

    def iternext(self) -> str:
        """Iterate through characters of the string."""

        try:
            char = self._string[self._index]
            self._index += 1
        except IndexError:
            raise StopIteration

        return char


def _to_bstr(obj: Any) -> bytes:
    """Convert to byte string."""

    if isinstance(obj, str):
        return obj.encode('ascii', 'backslashreplace')
    elif not isinstance(obj, bytes):
        return str(obj).encode('ascii', 'backslashreplace')
    return obj


def format_bytes(captures: List[bytes], formatting: Tuple[Tuple[int, Any]]) -> bytes:
    """Perform a string format."""

    capture = captures  # type: Any
    for i, fmt in enumerate(formatting, 0):
        if i == 0:
            continue
        fmt_type, value = fmt
        if fmt_type == FMT_ATTR:
            # Attribute
            capture = getattr(capture, value)
        elif fmt_type == FMT_INDEX:
            # Index
            capture = capture[value]
        elif fmt_type == FMT_CONV:
            # Conversion
            if value in ('r', 'a'):
                capture = repr(capture).encode('ascii', 'backslashreplace')
            elif value == 's':
                # If the object is not string or byte string already
                capture = _to_bstr(capture)
        elif fmt_type == FMT_SPEC:
            # Integers and floats don't have an explicit 's' format type.
            if value[3] and value[3] == 's':
                if isinstance(capture, int):  # pragma: no cover
                    raise ValueError("Unknown format code 's' for object of type 'int'")
                if isinstance(capture, float):  # pragma: no cover
                    raise ValueError("Unknown format code 's' for object of type 'float'")

            # Ensure object is a byte string
            capture = _to_bstr(capture)

            spec_type = value[1]
            if spec_type == '^':
                capture = capture.center(value[2], value[0])
            elif spec_type == ">":
                capture = capture.rjust(value[2], value[0])
            else:
                capture = capture.ljust(value[2], value[0])

    # Make sure the final object is a byte string
    return _to_bstr(capture)


def format_string(captures: List[str], formatting: Tuple[Tuple[int, Any]]) -> str:
    """Perform a string format."""

    capture = captures  # type: Any
    for i, fmt in enumerate(formatting, 0):
        if i == 0:
            continue
        fmt_type, value = fmt
        if fmt_type == FMT_ATTR:
            # Attribute
            capture = getattr(capture, value)
        elif fmt_type == FMT_INDEX:
            # Index
            capture = capture[value]
        elif fmt_type == FMT_CONV:
            # Conversion
            if value == 'a':
                capture = ascii(capture)
            elif value == 'r':
                capture = repr(capture)
            elif value == 's':
                # If the object is not string or byte string already
                capture = str(capture)
        elif fmt_type == FMT_SPEC:
            # Integers and floats don't have an explicit 's' format type.
            if value[3] and value[3] == 's':
                if isinstance(capture, int):  # pragma: no cover
                    raise ValueError("Unknown format code 's' for object of type 'int'")
                if isinstance(capture, float):  # pragma: no cover
                    raise ValueError("Unknown format code 's' for object of type 'float'")

            # Ensure object is a byte string
            if not isinstance(capture, str):
                capture = str(capture)

            spec_type = value[1]
            if spec_type == '^':
                capture = capture.center(value[2], value[0])
            elif spec_type == ">":
                capture = capture.rjust(value[2], value[0])
            else:
                capture = capture.ljust(value[2], value[0])

    # Make sure the final object is a byte string
    return str(capture) if not isinstance(capture, str) else capture


class Immutable(object):
    """Immutable."""

    __slots__: Tuple[Any, ...] = tuple()

    def __init__(self, **kwargs: Any) -> None:
        """Initialize."""

        for k, v in kwargs.items():
            super(Immutable, self).__setattr__(k, v)

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutability."""

        raise AttributeError('Class is immutable!')


def warn_deprecated(message: str, stacklevel: int = 2) -> None:  # pragma: no cover
    """Warn deprecated."""

    warnings.warn(
        message,
        category=DeprecationWarning,
        stacklevel=stacklevel
    )
