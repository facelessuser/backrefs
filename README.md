[![Unix Build Status][travis-image]][travis-link]
[![Windows Build Status][appveyor-image]][appveyor-link]
[![Coverage][codecov-image]][codecov-link]
[![Requirements Status][requires-image]][requires-link]
[![PyPI Version][pypi-image]][pypi-link]
![License][license-image]

# Backrefs

Backrefs is a wrapper around Python's built-in [Re][re] and the 3rd party [Regex][regex] library.  Backrefs adds various additional back references (and a couple other features) that are known to some regular expression engines, but not to Python's Re and/or Regex.  The supported back references actually vary depending on the regular expression engine being used as the engine may already have support for some.

```python
from backrefs import bre
>>> pattern = bre.compile(r'(\p{Letter}+)')
>>> pattern.sub(r'\C\1\E', 'sometext')
'SOMETEXT'
```

# Documentation

http://facelessuser.github.io/backrefs/

# License

Released under the MIT license.

Copyright (c) 2015 - 2019 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

[travis-image]: https://img.shields.io/travis/facelessuser/backrefs/master.svg?label=Unix%20Build
[travis-link]: https://travis-ci.org/facelessuser/backrefs
[appveyor-image]: https://img.shields.io/appveyor/ci/facelessuser/backrefs/master.svg?label=Windows%20Build
[appveyor-link]: https://ci.appveyor.com/project/facelessuser/backrefs
[license-image]: https://img.shields.io/badge/license-MIT-blue.svg
[codecov-image]: https://img.shields.io/codecov/c/github/facelessuser/backrefs/master.svg
[codecov-link]: http://codecov.io/github/facelessuser/backrefs?branch=master
[requires-image]: https://img.shields.io/requires/github/facelessuser/backrefs/master.svg
[requires-link]: https://requires.io/github/facelessuser/backrefs/requirements/?branch=master
[pypi-image]: https://img.shields.io/pypi/v/backrefs.svg
[pypi-link]: https://pypi.python.org/pypi/backrefs

[re]: https://docs.python.org/3/library/re.html
[regex]: https://pypi.python.org/pypi/regex
