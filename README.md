[![Donate via PayPal][donate-image]][donate-link]
[![Build][github-ci-image]][github-ci-link]
[![Coverage Status][codecov-image]][codecov-link]
[![PyPI Version][pypi-image]][pypi-link]
[![PyPI Downloads][pypi-down]][pypi-link]
[![PyPI - Python Version][python-image]][pypi-link]
[![License][license-image-mit]][license-link]

# Backrefs

Backrefs is a wrapper around Python's built-in [Re][re] and the 3rd party [Regex][regex] library.  Backrefs adds various
additional back references (and a couple other features) that are known to some regular expression engines, but not to
Python's Re and/or Regex.  The supported back references actually vary depending on the regular expression engine being
used as the engine may already have support for some.

```python
>>> from backrefs import bre
>>> pattern = bre.compile(r'(\p{Letter}+)')
>>> pattern.sub(r'\C\1\E', 'sometext')
'SOMETEXT'
```

# Documentation

https://facelessuser.github.io/backrefs/

# License

MIT

[github-ci-image]: https://github.com/facelessuser/backrefs/workflows/build/badge.svg
[github-ci-link]: https://github.com/facelessuser/backrefs/actions?query=workflow%3Abuild+branch%3Amaster
[codecov-image]: https://img.shields.io/codecov/c/github/facelessuser/backrefs/master.svg?logo=codecov&logoColor=aaaaaa&labelColor=333333
[codecov-link]: https://codecov.io/github/facelessuser/backrefs
[pypi-image]: https://img.shields.io/pypi/v/backrefs.svg?logo=pypi&logoColor=aaaaaa&labelColor=333333
[pypi-down]: https://img.shields.io/pypi/dm/backrefs.svg?logo=pypi&logoColor=aaaaaa&labelColor=333333
[pypi-link]: https://pypi.python.org/pypi/backrefs
[python-image]: https://img.shields.io/pypi/pyversions/backrefs?logo=python&logoColor=aaaaaa&labelColor=333333
[license-image-mit]: https://img.shields.io/badge/license-MIT-blue.svg?labelColor=333333
[license-link]: https://github.com/facelessuser/backrefs/blob/main/LICENSE.md
[donate-image]: https://img.shields.io/badge/Donate-PayPal-3fabd1?logo=paypal
[donate-link]: https://www.paypal.me/facelessuser

[re]: https://docs.python.org/3/library/re.html
[regex]: https://pypi.python.org/pypi/regex
