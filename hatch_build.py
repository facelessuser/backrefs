"""Dynamically define some metadata."""
import os
import sys
import importlib.util
from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def get_version_dev_status(root):
    """Get version_info without importing the entire module."""

    path = os.path.join(root, "backrefs", "__meta__.py")
    spec = importlib.util.spec_from_file_location("__meta__", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version_info__._get_dev_status()


def get_unicodedata():
    """Download the `unicodedata` version for the given Python version."""

    import unicodedata

    uver = unicodedata.unidata_version
    path = os.path.join(os.path.dirname(__file__), 'tools', 'unidatadownload.py')
    spec = importlib.util.spec_from_file_location("unidatadownload", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.get_unicodedata(uver, no_zip=True)
    return uver


def generate_unicode_table():
    """Generate the Unicode table for the given Python version."""

    uver = get_unicodedata()
    path = os.path.join(os.path.dirname(__file__), 'tools', 'unipropgen.py')
    spec = importlib.util.spec_from_file_location("unipropgen", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    module.build_tables(
        os.path.join(
            os.path.dirname(__file__),
            'backrefs', 'uniprops', 'unidata'
        ),
        uver
    )


class CustomBuildHook(BuildHookInterface):
    """Build hook."""

    def initialize(self, version, build_data):
        """Setup the build tag."""

        if self.target_name != 'wheel':
            return

        build_data['tag'] = f'py{"".join([str(x) for x in sys.version_info[:2]])}-none-any'
        generate_unicode_table()


class CustomMetadataHook(MetadataHookInterface):
    """Our metadata hook."""

    def update(self, metadata):
        """See https://ofek.dev/hatch/latest/plugins/metadata-hook/ for more information."""

        metadata["classifiers"] = [
            f"Development Status :: {get_version_dev_status(self.root)}",
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
            'Programming Language :: Python :: 3.13',
            'Programming Language :: Python :: 3.14',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Typing :: Typed'
        ]
