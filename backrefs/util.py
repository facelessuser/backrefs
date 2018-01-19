"""
Utilities and compatibility abstraction.

Licensed under MIT
Copyright (c) 2015 - 2018 Isaac Muse <isaacmuse@gmail.com>
"""
import sys
import struct

PY3 = (3, 0) <= sys.version_info < (4, 0)
PY34 = (3, 4) <= sys.version_info
PY36 = (3, 6) <= sys.version_info
PY37 = (3, 7) <= sys.version_info

if PY3:
    from functools import lru_cache  # noqa: F401

    string_type = str
    binary_type = bytes
    unichar = chr

    class Tokens(object):
        """Tokens base for Python 3."""

        def iternext(self):
            """Common override method."""

        def __next__(self):
            """Python 3 iterator compatible next."""

            return self.iternext()

else:
    from backports.functools_lru_cache import lru_cache  # noqa: F401

    string_type = unicode  # noqa F821
    binary_type = str  # noqa F821
    unichar = unichr  # noqa F821

    class Tokens(object):
        """Tokens base for Python 2."""

        def iternext(self):
            """Common override method."""

        def next(self):
            """Python 2 iterator compatible next."""

            return self.iternext()


def uchr(i):
    """Allow getting Unicode character on narrow python builds."""

    try:
        return unichar(i)
    except ValueError:  # pragma: no cover
        return struct.pack('i', i).decode('utf-32')


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
