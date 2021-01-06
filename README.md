[![Donate via PayPal][donate-image]][donate-link]
[![Discord][discord-image]][discord-link]
[![Build][github-ci-image]][github-ci-link]
[![Coverage Status][codecov-image]][codecov-link]
[![PyPI Version][pypi-image]][pypi-link]
[![PyPI - Python Version][python-image]][pypi-link]
![License][license-image-mit]

# Backrefs

Backrefs is a wrapper around Python's built-in [Re][re] and the 3rd party [Regex][regex] library.  Backrefs adds various
additional back references (and a couple other features) that are known to some regular expression engines, but not to
Python's Re and/or Regex.  The supported back references actually vary depending on the regular expression engine being
used as the engine may already have support for some.

```python
from backrefs import bre
>>> pattern = bre.compile(r'(\p{Letter}+)')
>>> pattern.sub(r'\C\1\E', 'sometext')
'SOMETEXT'
```

# Documentation

https://facelessuser.github.io/backrefs/

# License

Released under the MIT license.

Copyright (c) 2015 - 2021 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

[github-ci-image]: https://github.com/facelessuser/backrefs/workflows/build/badge.svg?branch=master&event=push
[github-ci-link]: https://github.com/facelessuser/backrefs/actions?query=workflow%3Abuild+branch%3Amaster
[discord-image]: https://img.shields.io/discord/678289859768745989?logo=discord&logoColor=aaaaaa&color=mediumpurple&labelColor=333333
[discord-link]:https://discord.gg/TWs8Tgr
[codecov-image]: https://img.shields.io/codecov/c/github/facelessuser/backrefs/master.svg?logo=codecov&logoColor=aaaaaa&labelColor=333333
[codecov-link]: https://codecov.io/github/facelessuser/backrefs
[pypi-image]: https://img.shields.io/pypi/v/backrefs.svg?logo=pypi&logoColor=aaaaaa&labelColor=333333
[pypi-link]: https://pypi.python.org/pypi/backrefs
[python-image]: https://img.shields.io/pypi/pyversions/backrefs?logo=python&logoColor=aaaaaa&labelColor=333333
[license-image-mit]: https://img.shields.io/badge/license-MIT-blue.svg?labelColor=333333
[donate-image]: https://img.shields.io/badge/Donate-PayPal-3fabd1?logo=paypal
[donate-link]: https://www.paypal.me/facelessuser

[re]: https://docs.python.org/3/library/re.html
[regex]: https://pypi.python.org/pypi/regex
