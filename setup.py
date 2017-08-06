#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup package."""
from setuptools import setup, find_packages
import sys
import os
import imp
import traceback

PY3 = (3, 0) <= sys.version_info < (4, 0)


def get_version():
    """Get version and version_info without importing the entire module."""

    devstatus = {
        'alpha': '3 - Alpha',
        'beta': '4 - Beta',
        'candidate': '4 - Beta',
        'final': '5 - Production/Stable'
    }
    path = os.path.join(os.path.dirname(__file__), 'backrefs')
    fp, pathname, desc = imp.find_module('__init__', [path])
    try:
        v = imp.load_module('__init__', fp, pathname, desc)
        return v.version, devstatus[v.version_info[3]]
    except Exception:
        print(traceback.format_exc())
    finally:
        fp.close()


def get_unicodedata():
    """Download the unicodedata version for the given Python version."""

    import unicodedata

    fail = False
    path = os.path.join(os.path.dirname(__file__), 'tools')
    fp, pathname, desc = imp.find_module('unidatadownload', [path])
    try:
        unidatadownload = imp.load_module('unidatadownload', fp, pathname, desc)
        unidatadownload.get_unicodedata(unicodedata.unidata_version, no_zip=True)
    except Exception:
        print(traceback.format_exc())
        fail = True
    finally:
        fp.close()

    assert not fail, "Failed to obtain unicodedata!"


def generate_unicode_table():
    """Generate the unicode table for the given Python version."""

    fail = False
    path = os.path.join(os.path.dirname(__file__), 'tools')
    fp, pathname, desc = imp.find_module('unipropgen', [path])
    try:
        unipropgen = imp.load_module('unipropgen', fp, pathname, desc)
        unipropgen.build_unicode_property_table(
            os.path.join(
                os.path.dirname(__file__),
                'backrefs', 'uniprops', 'unidata'
            )
        )
    except Exception:
        print(traceback.format_exc())
        fail = True
    finally:
        fp.close()

    assert not fail, "Failed uniprops.py generation!"


VER, DEVSTATUS = get_version()
get_unicodedata()
generate_unicode_table()

LONG_DESC = '''
Backrefs is a library that wraps the default Python re module or the third party regex module in order
to add additional back refrences.
You can check out the list of available extensions and learn more about them by `reading the docs`_.

.. _`reading the docs`: http://facelessuser.github.io/backrefs/

Support
=======

Help and support is available here at the repository's `bug tracker`_.
Please read about `support and contributing`_ before creating issues.

.. _`bug tracker`: https://github.com/facelessuser/backrefs/issues
.. _`support and contributing`: http://facelessuser.github.io/backrefs/contributing/
'''

setup(
    name='backrefs',
    version=VER,
    keywords='regex re',
    description='A wrapper around re and regex that adds additional back references.',
    long_description=LONG_DESC,
    author='Isaac Muse',
    author_email='Isaac.Muse [at] gmail.com',
    url='https://github.com/facelessuser/backrefs',
    packages=find_packages(exclude=['tools', 'tests']),
    install_requires=[],
    zip_safe=False,
    package_data={},
    license='MIT License',
    classifiers=[
        'Development Status :: %s' % DEVSTATUS,
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
