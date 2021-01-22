"""Test `Sentence Break`."""
import unittest
from backrefs import uniprops
import re


class TestSentenceBreak(unittest.TestCase):
    """Test `Sentence Break` access."""

    def test_table_integrity(self):
        """Test that there is parity between Unicode and ASCII tables."""

        re_key = re.compile(r'^\^?[a-z0-9./]+$')

        keys1 = set(uniprops.unidata.unicode_sentence_break.keys())
        keys2 = set(uniprops.unidata.ascii_sentence_break.keys())

        # Ensure all keys are lowercase (only need to check Unicode as the ASCII keys must match the Unicode later)
        for k in keys1:
            self.assertTrue(re_key.match(k) is not None)

        # Ensure the same keys are in both the Unicode table as the ASCII table
        self.assertEqual(keys1, keys2)

        # Ensure each positive key has an inverse key
        for key in keys1:
            if not key.startswith('^'):
                self.assertTrue('^' + key in keys1)

    def test_sentencebreak(self):
        """Test `Sentence Break` properties."""

        for k, v in uniprops.unidata.unicode_sentence_break.items():
            result = uniprops.get_unicode_property('sentencebreak', k)
            self.assertEqual(result, v)

    def test_sentencebreak_ascii(self):
        """Test `Sentence Break` ASCII properties."""

        for k, v in uniprops.unidata.ascii_sentence_break.items():
            result = uniprops.get_unicode_property('sentencebreak', k, mode=uniprops.MODE_NORMAL)
            self.assertEqual(result, v)

    def test_sentencebreak_binary(self):
        """Test `Sentence Break` ASCII properties."""

        for k, v in uniprops.unidata.ascii_sentence_break.items():
            result = uniprops.get_unicode_property('sentencebreak', k, mode=uniprops.MODE_ASCII)
            self.assertEqual(result, uniprops.fmt_string(v, True))

    def test_bad_sentencebreak(self):
        """Test `Sentence Break` property with bad value."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('sentencebreak', 'bad')

    def test_alias(self):
        """Test aliases."""

        alias = None
        for k, v in uniprops.unidata.alias.unicode_alias['_'].items():
            if v == 'sentencebreak':
                alias = k
                break

        self.assertTrue(alias is not None)

        # Ensure alias works
        for k, v in uniprops.unidata.unicode_sentence_break.items():
            result = uniprops.get_unicode_property(alias, k)
            self.assertEqual(result, v)
            break

        # Test aliases for values
        for k, v in uniprops.unidata.alias.unicode_alias['sentencebreak'].items():
            result1 = uniprops.get_unicode_property(alias, k)
            result2 = uniprops.get_unicode_property(alias, v)
            self.assertEqual(result1, result2)
