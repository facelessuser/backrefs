"""Test `Word Break`."""
import unittest
import re
from backrefs import uniprops
from backrefs.uniprops.unidata import wordbreak
from backrefs.uniprops.unidata import alias


class TestWordBreak(unittest.TestCase):
    """Test `Word Break` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(wordbreak.unicode_word_break.keys())
        keys2 = set(wordbreak.ascii_word_break.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_wordbreak(self):
        """Test `Word Break` properties."""

        for k, v in wordbreak.unicode_word_break.items():
            result = uniprops.get_unicode_property('wordbreak', k)
            self.assertEqual(result, v)

    def test_wordbreak_ascii(self):
        """Test `Word Break` ASCII properties."""

        for k, v in wordbreak.ascii_word_break.items():
            result = uniprops.get_unicode_property('wordbreak', k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_wordbreak_binary(self):
        """Test `Word Break` ASCII properties."""

        for k, v in wordbreak.ascii_word_break.items():
            result = uniprops.get_unicode_property('wordbreak', k, mode=uniprops.MODE_ASCII)
            self.assertEqual(result, uniprops.fmt_string(v, True))

    def test_bad_wordbreak(self):
        """Test `Word Break` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('wordbreak', 'bad')

    def test_alias(self):
        """Test aliases."""

        _alias = None
        for k, v in alias.unicode_alias['_'].items():
            if v == 'wordbreak':
                _alias = k
                break

        self.assertTrue(_alias is not None)

        # Ensure alias works
        for k, v in wordbreak.unicode_word_break.items():
            result = uniprops.get_unicode_property(_alias, k)
            self.assertEqual(result, v)
            break

        # Test aliases for values
        for k, v in alias.unicode_alias['wordbreak'].items():
            result1 = uniprops.get_unicode_property(_alias, k)
            result2 = uniprops.get_unicode_property(_alias, v)
            self.assertEqual(result1, result2)
