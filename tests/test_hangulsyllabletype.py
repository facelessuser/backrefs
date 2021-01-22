"""Test `Hangul Syllable Type`."""
import unittest
from backrefs import uniprops
import re


class TestHangulSyllableType(unittest.TestCase):
    """Test `Hangul Syllable Type` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(uniprops.unidata.unicode_hangul_syllable_type.keys())
        keys2 = set(uniprops.unidata.ascii_hangul_syllable_type.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_hangulsyllabletype(self):
        """Test `Hangul Syllable Type` properties."""

        for k, v in uniprops.unidata.unicode_hangul_syllable_type.items():
            result = uniprops.get_unicode_property('hangulsyllabletype', k)
            self.assertEqual(result, v)

    def test_hangulsyllabletype_ascii(self):
        """Test `Hangul Syllable Type` ASCII properties."""

        for k, v in uniprops.unidata.ascii_hangul_syllable_type.items():
            result = uniprops.get_unicode_property('hangulsyllabletype', k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_hangulsyllabletype_binary(self):
        """Test `Hangul Syllable Type` ASCII properties."""

        for k, v in uniprops.unidata.ascii_hangul_syllable_type.items():
            result = uniprops.get_unicode_property('hangulsyllabletype', k, mode=uniprops.MODE_ASCII)
            self.assertEqual(result, uniprops.fmt_string(v, True))

    def test_bad_hangulsyllabletype(self):
        """Test `Hangul Syllable Type` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('hangulsyllabletype', 'bad')

    def test_alias(self):
        """Test aliases."""

        alias = None
        for k, v in uniprops.unidata.alias.unicode_alias['_'].items():
            if v == 'hangulsyllabletype':
                alias = k
                break

        self.assertTrue(alias is not None)

        # Ensure alias works
        for k, v in uniprops.unidata.unicode_hangul_syllable_type.items():
            result = uniprops.get_unicode_property(alias, k)
            self.assertEqual(result, v)
            break

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['hangulsyllabletype'].items():
            result1 = uniprops.get_unicode_property(alias, k)
            result2 = uniprops.get_unicode_property(alias, v)
            self.assertEqual(result1, result2)
