"""Backrefs package."""
from pep562 import Pep562
from .__meta__ import __version__, __version_info__
import sys
import warnings

__all__ = ("__version__", "__version_info__")
__deprecated__ = {
    "version": ("__version__", __version__),
    "version_info": ("__version_info__", __version_info__)
}

PY37 = (3, 7) <= sys.version_info


def __getattr__(name):  # noqa: N807
    """Get attribute."""

    deprecated = __deprecated__.get(name)
    if deprecated:
        warnings.warn(
            "'{}' is deprecated. Use '{}' instead.".format(name, deprecated[0]),
            category=DeprecationWarning,
            stacklevel=(3 if PY37 else 4)
        )
        return deprecated[1]
    raise AttributeError("module '{}' has no attribute '{}'".format(__name__, name))


def __dir__():  # noqa: N807
    """Module directory."""

    return sorted(list(__all__) + list(__deprecated__.keys()))


if not PY37:
    Pep562(__name__)
