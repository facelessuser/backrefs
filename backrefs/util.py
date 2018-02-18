"""
Utilities and compatibility abstraction.

Licensed under MIT
Copyright (c) 2015 - 2018 Isaac Muse <isaacmuse@gmail.com>
"""
import sys
import struct

PY2 = (2, 0) <= sys.version_info < (3, 0)
PY3 = (3, 0) <= sys.version_info < (4, 0)
PY34 = (3, 4) <= sys.version_info
PY36 = (3, 6) <= sys.version_info
PY37 = (3, 7) <= sys.version_info

if PY3:
    from functools import lru_cache  # noqa F401
    import copyreg  # noqa F401

    string_type = str
    binary_type = bytes
    unichar = chr

else:
    from backports.functools_lru_cache import lru_cache  # noqa F401
    import copy_reg as copyreg  # noqa F401

    string_type = unicode  # noqa F821
    binary_type = str  # noqa F821
    unichar = unichr  # noqa F821


class StringIter(object):
    """Preprocess replace tokens."""

    def __init__(self, string):
        """Initialize."""

        self._string = string
        self._index = 0

    def __iter__(self):
        """Iterate."""

        return self

    def __next__(self):
        """Python 3 iterator compatible next."""

        return self.iternext()

    @property
    def index(self):
        """Get Index."""

        return self._index

    def rewind(self, count):
        """Rewind index."""

        if count > self._index:  # pragma: no cover
            raise ValueError("Can't rewind past beginning!")

        self._index -= count

    def iternext(self):
        """Iterate through characters of the string."""

        try:
            char = self._string[self._index]
            self._index += 1
        except IndexError:
            raise StopIteration

        return char

    # Python 2 iterator compatible next.
    next = __next__  # noqa A002


def uchr(i):
    """Allow getting Unicode character on narrow python builds."""

    try:
        return unichar(i)
    except ValueError:
        return struct.pack('i', i).decode('utf-32')


def uord(c):
    """Get Unicode ordinal."""

    if len(c) == 2:
        high, low = [ord(p) for p in c]
        ordinal = (high - 0xD800) * 0x400 + low - 0xDC00 + 0x10000
    else:
        ordinal = ord(c)

    return ordinal


class Immutable(object):
    """Immutable."""

    __slots__ = tuple()

    def __init__(self, **kwargs):
        """Initialize."""

        for k, v in kwargs.items():
            super(Immutable, self).__setattr__(k, v)

    def __setattr__(self, name, value):
        """Prevent mutability."""

        raise AttributeError('Class is immutable!')
