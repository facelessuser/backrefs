"""Test `General Category`."""
import unittest
import re
from backrefs import uniprops
from backrefs.uniprops.unidata import generalcategory
from backrefs.uniprops.unidata import alias


class TestGeneralCategory(unittest.TestCase):
    """Test `General Category` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(generalcategory.unicode_properties.keys())
        keys2 = set(generalcategory.ascii_properties.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        for key in keys1:
            k1 = set(generalcategory.unicode_properties[key].keys())
            k2 = set(generalcategory.ascii_properties[key].keys())

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

        for k1, v1 in generalcategory.unicode_properties.items():
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

        for k1, v1 in generalcategory.ascii_properties.items():
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

        for k1, v1 in generalcategory.unicode_properties.items():
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

        for k1, v1 in generalcategory.ascii_properties.items():
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

        for k1, v1 in generalcategory.ascii_properties.items():
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

    def test_gc_range(self):
        """Test characters `UnicodeData.txt` defines with a `First` and a `Last` line."""

        for char in ('\uac00', '\u4e16', '\ud55c', '\ud7a3'):
            for category, match in (('lo', True), ('l', True), ('cn', False), ('^cn', True)):
                result = re.match('[%s]' % uniprops.get_unicode_property(category), char)
                self.assertEqual(result is not None, match)

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

        _alias = None
        for k, v in alias.unicode_alias['_'].items():
            if v == 'generalcategory':
                _alias = k
                break

        self.assertTrue(_alias is not None)

        # Test aliases for values
        for k, v in alias.unicode_alias['generalcategory'].items():
            result1 = uniprops.get_unicode_property(_alias, k)
            result2 = uniprops.get_unicode_property(_alias, v)
            self.assertEqual(result1, result2)

    def test_alias_detect(self):
        """Test aliases."""

        # Test aliases for values
        for k, v in alias.unicode_alias['generalcategory'].items():
            result1 = uniprops.get_unicode_property(k)
            result2 = uniprops.get_unicode_property(v)
            self.assertEqual(result1, result2)

    def test_is_prefix(self):
        """Test that an initial `is` is allowed on General Category values and on the property name (`UAX44-LM3`)."""

        table = generalcategory.unicode_properties
        names = set(table) | {a + b for a in table for b in table[a] if not b.startswith('^')}
        names |= set(alias.unicode_alias['generalcategory'])
        for name in names:
            expected = uniprops.get_unicode_property(name)
            negated = uniprops.get_unicode_property('^' + name)
            self.assertEqual(uniprops.get_unicode_property('is' + name), expected, name)
            self.assertEqual(uniprops.get_unicode_property('^is' + name), negated, name)
            for prop in ('gc', 'generalcategory', 'isgc', 'isgeneralcategory'):
                self.assertEqual(uniprops.get_unicode_property(prop, 'is' + name), expected, (prop, name))
                self.assertEqual(uniprops.get_unicode_property(prop, name), expected, (prop, name))
                self.assertEqual(uniprops.get_unicode_property('^' + prop, 'is' + name), negated, (prop, name))

        # An initial `is` is only removed once.
        for args in (('isislu',), ('gc', 'isislu'), ('isisgc', 'lu'), ('is',), ('gc', 'is')):
            with self.assertRaises(ValueError):
                uniprops.get_unicode_property(*args)

    def test_is_prefix_unambiguous(self):
        """
        Test that no name begins with `is`.

        Removing an initial `is` relies on names being unique even when an initial `is` is ignored, which Unicode
        guarantees. As no name begins with `is`, that holds for the names Backrefs supports. If a name ever begins
        with `is`, check that it can't be confused with another name before allowing it here.
        """

        from backrefs.uniprops.unidata import binary, block, scriptextensions

        table = generalcategory.unicode_properties
        namespaces = {
            'General Category': (
                set(table) | {a + b for a in table for b in table[a]} | set(alias.unicode_alias['generalcategory'])
            ),
            'Script': set(scriptextensions.unicode_script_extensions) | set(alias.unicode_alias['script']),
            'Binary': set(binary.unicode_binary) | set(alias.unicode_alias['binary']),
            'Block': set(block.unicode_blocks) | set(alias.unicode_alias['block']),
            'Property names': set(alias.unicode_alias['_']) | set(alias.unicode_alias['_'].values()),
        }
        for namespace, names in namespaces.items():
            self.assertEqual([n for n in names if n.lstrip('^').startswith('is')], [], namespace)
