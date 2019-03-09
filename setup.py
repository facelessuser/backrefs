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

    path = os.path.join(os.path.dirname(__file__), 'backrefs')
    fp, pathname, desc = imp.find_module('__meta__', [path])
    try:
        vi = imp.load_module('__meta__', fp, pathname, desc).__version_info__
        return vi._get_canonical(), vi._get_dev_status()
    except Exception:
        print(traceback.format_exc())
    finally:
        fp.close()


def get_requirements():
    """Load list of dependencies."""

    install_requires = []
    with open("requirements/project.txt") as f:
        for line in f:
            if not line.startswith("#"):
                install_requires.append(line.strip())
    return install_requires


def get_unicodedata():
    """Download the `unicodedata` version for the given Python version."""

    import unicodedata

    fail = False
    uver = unicodedata.unidata_version
    path = os.path.join(os.path.dirname(__file__), 'tools')
    fp, pathname, desc = imp.find_module('unidatadownload', [path])
    try:
        unidatadownload = imp.load_module('unidatadownload', fp, pathname, desc)
        unidatadownload.get_unicodedata(uver, no_zip=True)
    except Exception:
        print(traceback.format_exc())
        fail = True
    finally:
        fp.close()

    assert not fail, "Failed to obtain unicodedata!"
    return uver


def generate_unicode_table():
    """Generate the Unicode table for the given Python version."""

    uver = get_unicodedata()
    fail = False
    path = os.path.join(os.path.dirname(__file__), 'tools')
    fp, pathname, desc = imp.find_module('unipropgen', [path])
    try:
        unipropgen = imp.load_module('unipropgen', fp, pathname, desc)
        unipropgen.build_tables(
            os.path.join(
                os.path.dirname(__file__),
                'backrefs', 'uniprops', 'unidata'
            ),
            uver
        )
    except Exception:
        print(traceback.format_exc())
        fail = True
    finally:
        fp.close()

    assert not fail, "Failed uniprops.py generation!"


def get_description():
    """Get long description."""

    with open("README.md", 'r') as f:
        desc = f.read()
    return desc


VER, DEVSTATUS = get_version()
generate_unicode_table()

setup(
    name='backrefs',
    version=VER,
    python_requires=">=3.4",
    keywords='regex re',
    description='A wrapper around re and regex that adds additional back references.',
    long_description=get_description(),
    long_description_content_type='text/markdown',
    author='Isaac Muse',
    author_email='Isaac.Muse@gmail.com',
    url='https://github.com/facelessuser/backrefs',
    packages=find_packages(exclude=['tools', 'tests']),
    install_requires=get_requirements(),
    zip_safe=False,
    package_data={},
    license='MIT License',
    classifiers=[
        'Development Status :: %s' % DEVSTATUS,
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
