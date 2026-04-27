"""Test `Age`."""
import unittest
import re
from backrefs import uniprops
from backrefs.uniprops.unidata import age
from backrefs.uniprops.unidata import alias


class TestAge(unittest.TestCase):
    """Test `Age` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(age.unicode_age.keys())
        keys2 = set(age.ascii_age.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_age(self):
        """Test `Age` properties."""

        for k, v in age.unicode_age.items():
            result = uniprops.get_unicode_property('age', k)
            self.assertEqual(result, v)

    def test_age_ascii(self):
        """Test `Age` ASCII properties."""

        for k, v in age.ascii_age.items():
            result = uniprops.get_unicode_property('age', k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_age_binary(self):
        """Test `Age` ASCII properties."""

        for k, v in age.ascii_age.items():
            result = uniprops.get_unicode_property('age', k, mode=uniprops.MODE_ASCII)
            self.assertEqual(result, uniprops.fmt_string(v, True))

    def test_bad_age(self):
        """Test age property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('age', 'bad')

    def test_alias(self):
        """Test aliases."""

        _alias = None
        for k, v in alias.unicode_alias['_'].items():
            if v == 'age':
                _alias = k
                break

        self.assertTrue(_alias is not None)

        # Ensure alias works
        for k, v in age.unicode_age.items():
            result = uniprops.get_unicode_property(_alias, k)
            self.assertEqual(result, v)
            break

        # Test aliases for values
        for k, v in alias.unicode_alias['age'].items():
            result1 = uniprops.get_unicode_property(_alias, k)
            result2 = uniprops.get_unicode_property(_alias, v)
            self.assertEqual(result1, result2)
