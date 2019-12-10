# Installation

## Overview

Backrefs doesn't have any required external dependencies.  If desired, you can install the optional [Regex][regex]
module and use Backrefs with either Python's Re module or the Regex module. Instructions to install with and without
optional dependencies is found below.

## Installation

There are a couple of recommended ways to install Backrefs.  If you would like to install in a virtual machine, you can
do that as well.

1. Install with pip:

    ```console
    $ pip install backrefs
    ```

2. Install with optional requirement `regex`:

    ```console
    $ pip install backrefs[extras]
    ```

2. Install locally from source via:

    ```console
    $ python setup.py build
    $ python setup.py install
    ```

3. If developing Backrefs, you can install via:

    ```console
    $ pip install --editable .
    ```

    This method will allow you to instantly see your changes without reinstalling which is great for developing.

--8<-- "links.txt"
