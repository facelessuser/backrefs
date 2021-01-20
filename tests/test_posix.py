"""Test `POSIX`."""
import unittest
from backrefs import uniprops
import re


class TestPosix(unittest.TestCase):
    """Test `POSIX` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(uniprops.unidata.unicode_posix_properties.keys())
        keys2 = set(uniprops.unidata.ascii_posix_properties.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_posix(self):
        """Test `POSIX` properties."""

        for k, v in uniprops.unidata.unicode_posix_properties.items():
            result = uniprops.get_posix_property(k, mode=uniprops.POSIX)
            self.assertEqual(result, v)

    def test_posix_ascii(self):
        """Test `POSIX` ASCII properties."""

        for k, v in uniprops.unidata.ascii_posix_properties.items():
            result = uniprops.get_posix_property(k, mode=uniprops.POSIX_ASCII)
            self.assertEqual(result, v)

    def test_posix_unicode(self):
        """Test `POSIX` Unicode properties."""

        for k in uniprops.unidata.ascii_posix_properties.keys():
            result = uniprops.get_posix_property(k, mode=uniprops.POSIX_UNICODE)
            if k.startswith('^'):
                k = '^posix' + k[1:]
            else:
                k = 'posix' + k
            self.assertEqual(result, uniprops.unidata.unicode_binary[k])

    def test_bad_script(self):
        """Test `POSIX` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_posix_property('bad')
