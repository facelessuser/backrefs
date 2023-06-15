# Installation

## Overview

Backrefs is a wrapper around Python's built-in [Re][re] and the 3rd party [Regex][regex] library.  Backrefs adds various
additional back references (and a couple other features) that are known to some regular expression engines, but not to
Python's Re and/or Regex.  The supported references actually vary depending on the regular expression engine being
used as the engine may already have support for some, or things that prevent implementation of a feature.

Backrefs comes in two flavors: `bre` (a Re wrapper) and `bregex` (a Regex wrapper).

## Installation

There are a couple of recommended ways to install Backrefs.

1.  Install with pip:

    ```console
    $ pip install backrefs
    ```

2.  Install with optional requirement `regex`:

    ```console
    $ pip install backrefs[extras]
    ```

2.  Install locally from source via:

    ```console
    $ python setup.py build
    $ python setup.py install
    ```

3.  If developing Backrefs, you can install via:

    ```console
    $ pip install --editable .
    ```

    This method will allow you to instantly see your changes without reinstalling which is great for developing.
