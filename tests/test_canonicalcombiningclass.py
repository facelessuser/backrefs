"""Test `Canonnical Combining Class`."""
import unittest
from backrefs import uniprops
import re


class TestCanonicalCombiningClass(unittest.TestCase):
    """Test `Canonnical Combining Class` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(uniprops.unidata.unicode_canonical_combining_class.keys())
        keys2 = set(uniprops.unidata.ascii_canonical_combining_class.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_canonicalcombiningclass(self):
        """Test `Canonnical Combining Class` properties."""

        for k, v in uniprops.unidata.unicode_canonical_combining_class.items():
            result = uniprops.get_unicode_property('canonicalcombiningclass', k)
            self.assertEqual(result, v)

    def test_canonicalcombiningclass_ascii(self):
        """Test `Canonnical Combining Class` ASCII properties."""

        for k, v in uniprops.unidata.ascii_canonical_combining_class.items():
            result = uniprops.get_unicode_property('canonicalcombiningclass', k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_canonicalcombiningclass_binary(self):
        """Test `Canonnical Combining Class` ASCII properties."""

        for k, v in uniprops.unidata.ascii_canonical_combining_class.items():
            result = uniprops.get_unicode_property('canonicalcombiningclass', k, mode=uniprops.MODE_ASCII)
            self.assertEqual(result, uniprops.fmt_string(v, True))

    def test_bad_canonicalcombiningclass(self):
        """Test `Canonnical Combining Class` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('canonicalcombiningclass', 'bad')

    def test_alias(self):
        """Test aliases."""

        alias = None
        for k, v in uniprops.unidata.alias.unicode_alias['_'].items():
            if v == 'canonicalcombiningclass':
                alias = k
                break

        self.assertTrue(alias is not None)

        # Ensure alias works
        for k, v in uniprops.unidata.unicode_canonical_combining_class.items():
            result = uniprops.get_unicode_property(alias, k)
            self.assertEqual(result, v)
            break

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['canonicalcombiningclass'].items():
            result1 = uniprops.get_unicode_property(alias, k)
            result2 = uniprops.get_unicode_property(alias, v)
            self.assertEqual(result1, result2)
