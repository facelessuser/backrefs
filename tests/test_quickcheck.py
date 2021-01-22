"""Test `Quick Check`."""
import unittest
from backrefs import uniprops
import re


class TestNFCQuickCheck(unittest.TestCase):
    """Test `NFC Quick Check` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(uniprops.unidata.unicode_nfc_quick_check.keys())
        keys2 = set(uniprops.unidata.ascii_nfc_quick_check.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_nfcquickcheck(self):
        """Test `NFC Quick Check` properties."""

        for k, v in uniprops.unidata.unicode_nfc_quick_check.items():
            result = uniprops.get_unicode_property('nfcquickcheck', k)
            self.assertEqual(result, v)

    def test_nfcquickcheck_ascii(self):
        """Test `NFC Quick Check` ASCII properties."""

        for k, v in uniprops.unidata.ascii_nfc_quick_check.items():
            result = uniprops.get_unicode_property('nfcquickcheck', k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_nfcquickcheck_binary(self):
        """Test `NFC Quick Check` ASCII properties."""

        for k, v in uniprops.unidata.ascii_nfc_quick_check.items():
            result = uniprops.get_unicode_property('nfcquickcheck', k, mode=uniprops.MODE_ASCII)
            self.assertEqual(result, uniprops.fmt_string(v, True))

    def test_bad_nfcquickcheck(self):
        """Test `NFC Quick Check` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('nfcquickcheck', 'bad')

    def test_alias(self):
        """Test aliases."""

        alias = None
        for k, v in uniprops.unidata.alias.unicode_alias['_'].items():
            if v == 'nfcquickcheck':
                alias = k
                break

        self.assertTrue(alias is not None)

        # Ensure alias works
        for k, v in uniprops.unidata.unicode_nfc_quick_check.items():
            result = uniprops.get_unicode_property(alias, k)
            self.assertEqual(result, v)
            break

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['nfcquickcheck'].items():
            result1 = uniprops.get_unicode_property(alias, k)
            result2 = uniprops.get_unicode_property(alias, v)
            self.assertEqual(result1, result2)


class TestNFKCQuickCheck(unittest.TestCase):
    """Test `NFKC Quick Check` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(uniprops.unidata.unicode_nfkc_quick_check.keys())
        keys2 = set(uniprops.unidata.ascii_nfkc_quick_check.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_nfkcquickcheck(self):
        """Test `NFKC Quick Check` properties."""

        for k, v in uniprops.unidata.unicode_nfkc_quick_check.items():
            result = uniprops.get_unicode_property('nfkcquickcheck', k)
            self.assertEqual(result, v)

    def test_nfkcquickcheck_ascii(self):
        """Test `NFKC Quick Check` ASCII properties."""

        for k, v in uniprops.unidata.ascii_nfkc_quick_check.items():
            result = uniprops.get_unicode_property('nfkcquickcheck', k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_nfkcquickcheck_binary(self):
        """Test `NFKC Quick Check` ASCII properties."""

        for k, v in uniprops.unidata.ascii_nfkc_quick_check.items():
            result = uniprops.get_unicode_property('nfkcquickcheck', k, mode=uniprops.MODE_ASCII)
            self.assertEqual(result, uniprops.fmt_string(v, True))

    def test_bad_nfkc_quick_check(self):
        """Test `NFKC Quick Check` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('nfkcquickcheck', 'bad')

    def test_alias(self):
        """Test aliases."""

        alias = None
        for k, v in uniprops.unidata.alias.unicode_alias['_'].items():
            if v == 'nfkcquickcheck':
                alias = k
                break

        self.assertTrue(alias is not None)

        # Ensure alias works
        for k, v in uniprops.unidata.unicode_nfkc_quick_check.items():
            result = uniprops.get_unicode_property(alias, k)
            self.assertEqual(result, v)
            break

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['nfkcquickcheck'].items():
            result1 = uniprops.get_unicode_property(alias, k)
            result2 = uniprops.get_unicode_property(alias, v)
            self.assertEqual(result1, result2)


class TestNFDQuickCheck(unittest.TestCase):
    """Test `NFD Quick Check` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(uniprops.unidata.unicode_nfd_quick_check.keys())
        keys2 = set(uniprops.unidata.ascii_nfd_quick_check.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_nfdquickcheck(self):
        """Test `NFD Quick Check` properties."""

        for k, v in uniprops.unidata.unicode_nfd_quick_check.items():
            result = uniprops.get_unicode_property('nfdquickcheck', k)
            self.assertEqual(result, v)

    def test_nfdquickcheck_ascii(self):
        """Test `NFD Quick Check` ASCII properties."""

        for k, v in uniprops.unidata.ascii_nfd_quick_check.items():
            result = uniprops.get_unicode_property('nfdquickcheck', k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_nfdquickcheck_binary(self):
        """Test `NFD Quick Check` ASCII properties."""

        for k, v in uniprops.unidata.ascii_nfd_quick_check.items():
            result = uniprops.get_unicode_property('nfdquickcheck', k, mode=uniprops.MODE_ASCII)
            self.assertEqual(result, uniprops.fmt_string(v, True))

    def test_bad_nfdquickcheck(self):
        """Test `NFD Quick Check` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('nfdquickcheck', 'bad')

    def test_alias(self):
        """Test aliases."""

        alias = None
        for k, v in uniprops.unidata.alias.unicode_alias['_'].items():
            if v == 'nfdquickcheck':
                alias = k
                break

        self.assertTrue(alias is not None)

        # Ensure alias works
        for k, v in uniprops.unidata.unicode_nfd_quick_check.items():
            result = uniprops.get_unicode_property(alias, k)
            self.assertEqual(result, v)
            break

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['nfdquickcheck'].items():
            result1 = uniprops.get_unicode_property(alias, k)
            result2 = uniprops.get_unicode_property(alias, v)
            self.assertEqual(result1, result2)


class TestNFKDQuickCheck(unittest.TestCase):
    """Test `NFKD Quick Check` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(uniprops.unidata.unicode_nfkd_quick_check.keys())
        keys2 = set(uniprops.unidata.ascii_nfkd_quick_check.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_nfkdquickcheck(self):
        """Test `NFKD Quick Check` properties."""

        for k, v in uniprops.unidata.unicode_nfkd_quick_check.items():
            result = uniprops.get_unicode_property('nfkdquickcheck', k)
            self.assertEqual(result, v)

    def test_nfkdquickcheck_ascii(self):
        """Test `NFKD Quick Check` ASCII properties."""

        for k, v in uniprops.unidata.ascii_nfkd_quick_check.items():
            result = uniprops.get_unicode_property('nfkdquickcheck', k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_nfkquickcheck_binary(self):
        """Test `NFKD Quick Check` ASCII properties."""

        for k, v in uniprops.unidata.ascii_nfkd_quick_check.items():
            result = uniprops.get_unicode_property('nfkdquickcheck', k, mode=uniprops.MODE_ASCII)
            self.assertEqual(result, uniprops.fmt_string(v, True))

    def test_bad_nfkdquickcheck(self):
        """Test `NFKD Quick Check` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('nfkdquickcheck', 'bad')

    def test_alias(self):
        """Test aliases."""

        alias = None
        for k, v in uniprops.unidata.alias.unicode_alias['_'].items():
            if v == 'nfkdquickcheck':
                alias = k
                break

        self.assertTrue(alias is not None)

        # Ensure alias works
        for k, v in uniprops.unidata.unicode_nfkd_quick_check.items():
            result = uniprops.get_unicode_property(alias, k)
            self.assertEqual(result, v)
            break

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['nfkdquickcheck'].items():
            result1 = uniprops.get_unicode_property(alias, k)
            result2 = uniprops.get_unicode_property(alias, v)
            self.assertEqual(result1, result2)
