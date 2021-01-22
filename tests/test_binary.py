"""Test `Binary`."""
import unittest
from backrefs import uniprops
import re


class TestBinary(unittest.TestCase):
    """Test `Binary` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(uniprops.unidata.unicode_binary.keys())
        keys2 = set(uniprops.unidata.ascii_binary.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_binary(self):
        """Test `Binary` properties."""

        for k, v in uniprops.unidata.unicode_binary.items():
            result = uniprops.get_unicode_property(k)
            self.assertEqual(result, v)

    def test_binary_ascii(self):
        """Test `Binary` properties."""

        for k, v in uniprops.unidata.ascii_binary.items():
            result = uniprops.get_unicode_property(k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_binary_binary(self):
        """Test `Binary` ASCII properties."""

        for k, v in uniprops.unidata.ascii_binary.items():
            result = uniprops.get_unicode_property(k, mode=uniprops.MODE_ASCII)
            self.assertEqual(result, uniprops.fmt_string(v, True))

    def test_binary_true(self):
        """Test binary Category with a value."""

        result = uniprops.get_unicode_property('alphabetic', 'true')
        self.assertEqual(result, uniprops.unidata.unicode_binary['alphabetic'])

    def test_binary_t(self):
        """Test binary Category with a value."""

        result = uniprops.get_unicode_property('alphabetic', 't')
        self.assertEqual(result, uniprops.unidata.unicode_binary['alphabetic'])

    def test_binary_yes(self):
        """Test binary Category with a value."""

        result = uniprops.get_unicode_property('alphabetic', 'yes')
        self.assertEqual(result, uniprops.unidata.unicode_binary['alphabetic'])

    def test_binary_y(self):
        """Test binary Category with a value."""

        result = uniprops.get_unicode_property('alphabetic', 'y')
        self.assertEqual(result, uniprops.unidata.unicode_binary['alphabetic'])

    def test_binary_true_inverted(self):
        """Test binary Category with an inverted value."""

        result = uniprops.get_unicode_property('^alphabetic', 'true')
        self.assertEqual(result, uniprops.unidata.unicode_binary['^alphabetic'])

    def test_binary_false(self):
        """Test false."""

        result = uniprops.get_unicode_property('alphabetic', 'false')
        self.assertEqual(result, uniprops.unidata.unicode_binary['^alphabetic'])

    def test_binary_f(self):
        """Test short false."""

        result = uniprops.get_unicode_property('alphabetic', 'f')
        self.assertEqual(result, uniprops.unidata.unicode_binary['^alphabetic'])

    def test_binary_no(self):
        """Test no."""

        result = uniprops.get_unicode_property('alphabetic', 'no')
        self.assertEqual(result, uniprops.unidata.unicode_binary['^alphabetic'])

    def test_binary_n(self):
        """Test short no."""

        result = uniprops.get_unicode_property('alphabetic', 'n')
        self.assertEqual(result, uniprops.unidata.unicode_binary['^alphabetic'])

    def test_binary_false_inverted(self):
        """Test inverted false."""

        result = uniprops.get_unicode_property('^alphabetic', 'false')
        self.assertEqual(result, uniprops.unidata.unicode_binary['alphabetic'])

    def test_bad_binary(self):
        """Test binary property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('alphabetic', 'bad')

    def test_alias(self):
        """Test aliases."""

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['binary'].items():
            result1 = uniprops.get_unicode_property(k, 't')
            result2 = uniprops.get_unicode_property(v, 't')
            self.assertEqual(result1, result2)

    def test_alias_detect(self):
        """Test aliases."""

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['binary'].items():
            result1 = uniprops.get_unicode_property(k)
            result2 = uniprops.get_unicode_property(v)
            self.assertEqual(result1, result2)

    def test_isbinary_detect(self):
        """Test detection of `Binary` properties."""

        for k, v in uniprops.unidata.unicode_binary.items():
            if k.startswith('^'):
                k = '^is' + k[1:]
            else:
                k = 'is' + k
            result = uniprops.get_unicode_property(k)
            self.assertEqual(result, v)

    def test_isalias_detect(self):
        """Test aliases."""

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['binary'].items():
            is_k = 'is' + k
            is_v = 'is' + v
            result1 = uniprops.get_unicode_property(is_k)
            result2 = uniprops.get_unicode_property(is_v)
            self.assertEqual(result1, result2)
