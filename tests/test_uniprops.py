"""Test `uniprops`."""
import unittest
from backrefs import uniprops


class TestUniprops(unittest.TestCase):
    """General bad cases for `Uniprops`."""

    def test_with_bad_property_and_value(self):
        """Test property with bad category."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('^bad', 'bad')

    def test_bad_property(self):
        """Test bad property."""

        with self.assertRaises(ValueError):
            uniprops.get_unicode_property('^bad')
