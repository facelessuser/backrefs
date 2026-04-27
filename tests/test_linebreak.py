"""Test `Line Break`."""
import unittest
import re
from backrefs import uniprops
from backrefs.uniprops.unidata import linebreak
from backrefs.uniprops.unidata import alias


class TestLineBreak(unittest.TestCase):
    """Test `Line Break` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(linebreak.unicode_line_break.keys())
        keys2 = set(linebreak.ascii_line_break.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_linebreak(self):
        """Test `Line Break` properties."""

        for k, v in linebreak.unicode_line_break.items():
            print('linebreak={}'.format(k))
            result = uniprops.get_unicode_property('linebreak', k)
            self.assertEqual(result, v)

    def test_linebreak_ascii(self):
        """Test `Line Break` ASCII properties."""

        for k, v in linebreak.ascii_line_break.items():
            result = uniprops.get_unicode_property('linebreak', k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_linebreak_binary(self):
        """Test `Line Break` ASCII properties."""

        for k, v in linebreak.ascii_line_break.items():
            result = uniprops.get_unicode_property('linebreak', k, mode=uniprops.MODE_ASCII)
            self.assertEqual(result, uniprops.fmt_string(v, True))

    def test_bad_linebreak(self):
        """Test `Line Break` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('linebreak', 'bad')

    def test_alias(self):
        """Test aliases."""

        _alias = None
        for k, v in alias.unicode_alias['_'].items():
            if v == 'linebreak':
                _alias = k
                break

        self.assertTrue(_alias is not None)

        # Ensure alias works
        for k, v in linebreak.unicode_line_break.items():
            result = uniprops.get_unicode_property(_alias, k)
            self.assertEqual(result, v)
            break

        # Test aliases for values
        for k, v in alias.unicode_alias['linebreak'].items():
            result1 = uniprops.get_unicode_property(_alias, k)
            result2 = uniprops.get_unicode_property(_alias, v)
            self.assertEqual(result1, result2)
