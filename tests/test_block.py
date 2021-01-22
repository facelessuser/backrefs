"""Test `Block`."""
import unittest
from backrefs import uniprops
import re


class TestBlock(unittest.TestCase):
    """Test `Block` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(uniprops.unidata.unicode_blocks.keys())
        keys2 = set(uniprops.unidata.ascii_blocks.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_block(self):
        """Test `Block` properties."""

        for k, v in uniprops.unidata.unicode_blocks.items():
            result = uniprops.get_unicode_property('block', k)
            self.assertEqual(result, v)

    def test_block_ascii(self):
        """Test `Block` ASCII properties."""

        for k, v in uniprops.unidata.ascii_blocks.items():
            result = uniprops.get_unicode_property('block', k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_block_binary(self):
        """Test `Block` ASCII properties."""

        for k, v in uniprops.unidata.ascii_blocks.items():
            result = uniprops.get_unicode_property('block', k, mode=uniprops.MODE_ASCII)
            self.assertEqual(result, uniprops.fmt_string(v, True))

    def test_bad_block(self):
        """Test `Block` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('block', 'bad')

    def test_inbad_property(self):
        """Test `inbad` property."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('^inbad')

    def test_alias(self):
        """Test aliases."""

        alias = None
        for k, v in uniprops.unidata.alias.unicode_alias['_'].items():
            if v == 'block':
                alias = k
                break

        self.assertTrue(alias is not None)

        # Ensure alias works
        for k, v in uniprops.unidata.unicode_blocks.items():
            result = uniprops.get_unicode_property(alias, k)
            self.assertEqual(result, v)
            break

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['block'].items():
            result1 = uniprops.get_unicode_property(alias, k)
            result2 = uniprops.get_unicode_property(alias, v)
            self.assertEqual(result1, result2)

    def test_block_detect(self):
        """Test detection of `Block` properties."""

        for k, v in uniprops.unidata.unicode_blocks.items():
            # Block will only match if not already found in scripts extensions
            if k in uniprops.unidata.unicode_script_extensions:
                continue
            if k in uniprops.unidata.alias.unicode_alias['script']:
                continue
            if k in uniprops.unidata.unicode_binary:
                continue
            if k in uniprops.unidata.alias.unicode_alias['binary']:
                continue
            if k in uniprops.unidata.alias.unicode_alias['generalcategory']:
                continue
            result = uniprops.get_unicode_property(k)
            self.assertEqual(result, v)

    def test_inblock_detect(self):
        """Test detection of `Block` properties."""

        for k, v in uniprops.unidata.unicode_blocks.items():
            if k.startswith('^'):
                k = '^in' + k[1:]
            else:
                k = 'in' + k
            result = uniprops.get_unicode_property(k)
            self.assertEqual(result, v)

    def test_alias_detect(self):
        """Test aliases."""

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['block'].items():
            if k in uniprops.unidata.unicode_script_extensions:
                continue
            if k in uniprops.unidata.alias.unicode_alias['script']:
                continue
            if k in uniprops.unidata.unicode_binary:
                continue
            if k in uniprops.unidata.alias.unicode_alias['binary']:
                continue
            if k in uniprops.unidata.alias.unicode_alias['generalcategory']:
                continue
            if v in uniprops.unidata.unicode_script_extensions:
                continue
            if v in uniprops.unidata.alias.unicode_alias['script']:
                continue
            if v in uniprops.unidata.unicode_binary:
                continue
            if v in uniprops.unidata.alias.unicode_alias['binary']:
                continue
            if v in uniprops.unidata.alias.unicode_alias['generalcategory']:
                continue
            result1 = uniprops.get_unicode_property(k)
            result2 = uniprops.get_unicode_property(v)
            self.assertEqual(result1, result2)

    def test_inalias_detect(self):
        """Test aliases."""

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['block'].items():
            result1 = uniprops.get_unicode_property('in' + k)
            result2 = uniprops.get_unicode_property('in' + v)
            self.assertEqual(result1, result2)
