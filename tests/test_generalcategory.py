"""Test `General Category`."""
import unittest
from backrefs import uniprops
import re


class TestGeneralCategory(unittest.TestCase):
    """Test `General Category` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(uniprops.unidata.unicode_properties.keys())
        keys2 = set(uniprops.unidata.ascii_properties.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        for key in keys1:
            k1 = set(uniprops.unidata.unicode_properties[key].keys())
            k2 = set(uniprops.unidata.ascii_properties[key].keys())

            # Ensure each subcategory has a ^ key
            self.assertTrue('^' in k1)

            # Ensure each positive key has an inverse key
            for key in k1:
                if not key.startswith('^'):
                    self.assertTrue('^' + key in k1)

            # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
            for k in k1:
                self.assertTrue(k == '^' or re_key.match(k) is not None)

            # Ensure each Unicode subcategory has the same keys as the ASCII subcategory
            self.assertEqual(k1, k2)

    def test_gc(self):
        """Test `General Category`."""

        for k1, v1 in uniprops.unidata.unicode_properties.items():
            for k2, v2 in v1.items():
                if k2.startswith('^'):
                    prefix = '^'
                    subcategory = k2[1:]
                else:
                    prefix = ''
                    subcategory = k2
                prop = prefix + "generalcategory"
                category = k1 + subcategory

                result = uniprops.get_unicode_property(prop, category)
                self.assertEqual(result, v2)

    def test_gc_ascii(self):
        """Test `General Category`."""

        for k1, v1 in uniprops.unidata.ascii_properties.items():
            for k2, v2 in v1.items():
                if k2.startswith('^'):
                    prefix = '^'
                    subcategory = k2[1:]
                else:
                    prefix = ''
                    subcategory = k2
                prop = prefix + "generalcategory"
                category = k1 + subcategory

                result = uniprops.get_unicode_property(prop, category, mode=uniprops.MODE_NORMAL)
                self.assertEqual(result, v2)

    def test_gc_just_category(self):
        """Test `General Category`."""

        for k1, v1 in uniprops.unidata.unicode_properties.items():
            for k2, v2 in v1.items():
                if k2.startswith('^'):
                    prefix = '^'
                    subcategory = k2[1:]
                else:
                    prefix = ''
                    subcategory = k2
                category = prefix + k1 + subcategory

                result = uniprops.get_unicode_property(category)
                self.assertEqual(result, v2)

    def test_gc_just_category_ascii(self):
        """Test `General Category`."""

        for k1, v1 in uniprops.unidata.ascii_properties.items():
            for k2, v2 in v1.items():
                if k2.startswith('^'):
                    prefix = '^'
                    subcategory = k2[1:]
                else:
                    prefix = ''
                    subcategory = k2
                category = prefix + k1 + subcategory

                result = uniprops.get_unicode_property(category, mode=uniprops.MODE_NORMAL)
                self.assertEqual(result, v2)

    def test_gc_just_category_binary(self):
        """Test `General Category` ASCII properties."""

        for k1, v1 in uniprops.unidata.ascii_properties.items():
            for k2, v2 in v1.items():
                if k2.startswith('^'):
                    prefix = '^'
                    subcategory = k2[1:]
                else:
                    prefix = ''
                    subcategory = k2
                category = prefix + k1 + subcategory

                result = uniprops.get_unicode_property(category, mode=uniprops.MODE_ASCII)
                self.assertEqual(result, uniprops.fmt_string(v2, True))

    def test_bad_single_subcategory(self):
        """Test `Joining Group` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('generalcategory', 'q')

    def test_bad_double_subcategory(self):
        """Test `Joining Group` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('generalcategory', 'qq')

    def test_alias(self):
        """Test aliases."""

        alias = None
        for k, v in uniprops.unidata.alias.unicode_alias['_'].items():
            if v == 'generalcategory':
                alias = k
                break

        self.assertTrue(alias is not None)

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['generalcategory'].items():
            result1 = uniprops.get_unicode_property(alias, k)
            result2 = uniprops.get_unicode_property(alias, v)
            self.assertEqual(result1, result2)

    def test_alias_detect(self):
        """Test aliases."""

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['generalcategory'].items():
            result1 = uniprops.get_unicode_property(k)
            result2 = uniprops.get_unicode_property(v)
            self.assertEqual(result1, result2)
