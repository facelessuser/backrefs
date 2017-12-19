"""
Compatibility abstraction.

Licensed under MIT
Copyright (c) 2015 - 2016 Isaac Muse <isaacmuse@gmail.com>
"""
import sys
import struct

PY3 = (3, 0) <= sys.version_info < (4, 0)

if PY3:
    string_type = str
    binary_type = bytes
    unichar = chr

    def iterstring(string):
        """Iterate through a string."""

        if isinstance(string, binary_type):
            for x in range(0, len(string)):
                yield string[x:x + 1]
        else:
            for c in string:
                yield c

    class Tokens(object):
        """Tokens base for Python 3."""

        def iternext(self):
            """Common override method."""

        def __next__(self):
            """Python 3 iterator compatible next."""

            return self.iternext()

else:
    string_type = unicode  # noqa F821
    binary_type = str  # noqa F821
    unichar = unichr  # noqa F821

    def iterstring(string):
        """Iterate through a string."""

        for c in string:
            yield c

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


def int2str(number):
    """Convert number to string."""

    return string_type(number)


def int2bytes(number):
    """Convert number to bytes."""

    return string_type(number).encode('ascii')
