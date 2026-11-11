"""Test `Block`."""
import unittest
import re
from backrefs import uniprops
from backrefs.uniprops.unidata import block
from backrefs.uniprops.unidata import binary
from backrefs.uniprops.unidata import scriptextensions
from backrefs.uniprops.unidata import alias


class TestBlock(unittest.TestCase):
    """Test `Block` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(block.unicode_blocks.keys())
        keys2 = set(block.ascii_blocks.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_inverse_is_complement(self):
        """Test that every inverse block is exactly the code points not in the block."""

        import re._parser as parser

        def ranges(text):
            """Get the sorted, merged ranges of a property's code points."""

            if not text:
                return []
            node = parser.parse(f'[{text}]')[0]
            items = []
            for op, av in [node] if node[0] is parser.LITERAL else node[1]:
                items.append((av, av) if op is parser.LITERAL else av)
            merged = []  # type: list[tuple[int, int]]
            for lo, hi in sorted(items):
                if merged and lo <= merged[-1][1] + 1:
                    merged[-1] = (merged[-1][0], max(hi, merged[-1][1]))
                else:
                    merged.append((lo, hi))
            return merged

        def complement(values):
            """Get the ranges of all code points not in the given ranges."""

            result = []
            start = 0
            for lo, hi in values:
                if lo > start:
                    result.append((start, lo - 1))
                start = hi + 1
            if start <= 0x10FFFF:
                result.append((start, 0x10FFFF))
            return result

        for table in (block.unicode_blocks, block.ascii_blocks):
            for key, value in table.items():
                if not key.startswith('^'):
                    self.assertEqual(ranges(table['^' + key]), complement(ranges(value)), key)

    def test_no_block_inverse(self):
        """Test that the inverse of `No_Block` includes the last blocks (Supplementary Private Use Areas)."""

        from backrefs import bre

        not_in_block = bre.compile(r'\p{No_Block}')
        in_block = bre.compile(r'\P{No_Block}')
        for c in (0xF0000, 0xFFFFD, 0x100000, 0x10FFFF):
            self.assertTrue(in_block.fullmatch(chr(c)) is not None, f'U+{c:04X}')
            self.assertTrue(not_in_block.fullmatch(chr(c)) is None, f'U+{c:04X}')
        self.assertTrue(not_in_block.fullmatch('\U000effff') is not None)
        self.assertTrue(in_block.fullmatch('\U000effff') is None)

    def test_block(self):
        """Test `Block` properties."""

        for k, v in block.unicode_blocks.items():
            result = uniprops.get_unicode_property('block', k)
            self.assertEqual(result, v)

    def test_block_ascii(self):
        """Test `Block` ASCII properties."""

        for k, v in block.ascii_blocks.items():
            result = uniprops.get_unicode_property('block', k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_block_binary(self):
        """Test `Block` ASCII properties."""

        for k, v in block.ascii_blocks.items():
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

        _alias = None
        for k, v in alias.unicode_alias['_'].items():
            if v == 'block':
                _alias = k
                break

        self.assertTrue(_alias is not None)

        # Ensure alias works
        for k, v in block.unicode_blocks.items():
            result = uniprops.get_unicode_property(_alias, k)
            self.assertEqual(result, v)
            break

        # Test aliases for values
        for k, v in alias.unicode_alias['block'].items():
            result1 = uniprops.get_unicode_property(_alias, k)
            result2 = uniprops.get_unicode_property(_alias, v)
            self.assertEqual(result1, result2)

    def test_block_detect(self):
        """Test detection of `Block` properties."""

        for k, v in block.unicode_blocks.items():
            # Block will only match if not already found in scripts extensions
            if k in scriptextensions.unicode_script_extensions:
                continue
            if k in alias.unicode_alias['script']:
                continue
            if k in binary.unicode_binary:
                continue
            if k in alias.unicode_alias['binary']:
                continue
            if k in alias.unicode_alias['generalcategory']:
                continue
            result = uniprops.get_unicode_property(k)
            self.assertEqual(result, v)

    def test_inblock_detect(self):
        """Test detection of `Block` properties."""

        for k, v in block.unicode_blocks.items():
            if k.startswith('^'):
                k = '^in' + k[1:]
            else:
                k = 'in' + k
            result = uniprops.get_unicode_property(k)
            self.assertEqual(result, v)

    def test_alias_detect(self):
        """Test aliases."""

        # Test aliases for values
        for k, v in alias.unicode_alias['block'].items():
            if k in scriptextensions.unicode_script_extensions:
                continue
            if k in alias.unicode_alias['script']:
                continue
            if k in binary.unicode_binary:
                continue
            if k in alias.unicode_alias['binary']:
                continue
            if k in alias.unicode_alias['generalcategory']:
                continue
            if v in scriptextensions.unicode_script_extensions:
                continue
            if v in alias.unicode_alias['script']:
                continue
            if v in binary.unicode_binary:
                continue
            if v in alias.unicode_alias['binary']:
                continue
            if v in alias.unicode_alias['generalcategory']:
                continue
            result1 = uniprops.get_unicode_property(k)
            result2 = uniprops.get_unicode_property(v)
            self.assertEqual(result1, result2)

    def test_inalias_detect(self):
        """Test aliases."""

        # Test aliases for values
        for k, v in alias.unicode_alias['block'].items():
            result1 = uniprops.get_unicode_property('in' + k)
            result2 = uniprops.get_unicode_property('in' + v)
            self.assertEqual(result1, result2)
