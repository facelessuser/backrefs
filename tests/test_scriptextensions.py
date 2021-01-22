"""Test `Script Extensions`."""
import unittest
from backrefs import uniprops
import re


class TestScriptExtensions(unittest.TestCase):
    """Test `Script Extensions` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(uniprops.unidata.unicode_script_extensions.keys())
        keys2 = set(uniprops.unidata.ascii_script_extensions.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_scriptextensions(self):
        """Test `Script Extensions` properties."""

        for k, v in uniprops.unidata.unicode_script_extensions.items():
            result = uniprops.get_unicode_property('scriptextensions', k)
            self.assertEqual(result, v)

    def test_scriptextensions_ascii(self):
        """Test `Script Extensions` ASCII properties."""

        for k, v in uniprops.unidata.ascii_script_extensions.items():
            result = uniprops.get_unicode_property('scriptextensions', k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_scriptextensions_binary(self):
        """Test `Script Extensions` ASCII properties."""

        for k, v in uniprops.unidata.ascii_script_extensions.items():
            result = uniprops.get_unicode_property('scriptextensions', k, mode=uniprops.MODE_ASCII)
            self.assertEqual(result, uniprops.fmt_string(v, True))

    def test_bad_scriptextensions(self):
        """Test `Script Extensions` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('scriptextensions', 'bad')

    def test_isbad_property(self):
        """Test `isbad` property."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('^isbad')

    def test_alias(self):
        """Test aliases."""

        alias = None
        for k, v in uniprops.unidata.alias.unicode_alias['_'].items():
            if v == 'scriptextensions':
                alias = k
                break

        self.assertTrue(alias is not None)

        # Ensure alias works
        for k, v in uniprops.unidata.unicode_script_extensions.items():
            result = uniprops.get_unicode_property(alias, k)
            self.assertEqual(result, v)
            break

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['script'].items():
            result1 = uniprops.get_unicode_property(alias, k)
            result2 = uniprops.get_unicode_property(alias, v)
            self.assertEqual(result1, result2)

    def test_scriptextension_detect(self):
        """Test detection of `Script Extensions` properties."""

        for k, v in uniprops.unidata.unicode_script_extensions.items():
            result = uniprops.get_unicode_property(k)
            self.assertEqual(result, v)

    def test_isscript_detect(self):
        """Test detection of `Script Extensions` properties."""

        for k, v in uniprops.unidata.unicode_script_extensions.items():
            if k.startswith('^'):
                k = '^is' + k[1:]
            else:
                k = 'is' + k
            result = uniprops.get_unicode_property(k)
            self.assertEqual(result, v)

    def test_alias_detect(self):
        """Test aliases."""

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['script'].items():
            result1 = uniprops.get_unicode_property(k)
            result2 = uniprops.get_unicode_property(v)
            self.assertEqual(result1, result2)

    def test_isalias_detect(self):
        """Test aliases."""

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['script'].items():
            result1 = uniprops.get_unicode_property('is' + k)
            result2 = uniprops.get_unicode_property('is' + v)
            self.assertEqual(result1, result2)
