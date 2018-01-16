# -*- coding: utf-8 -*-
"""Test bre lib."""
from __future__ import unicode_literals
import unittest
from backrefs import bre
import re
import sys
import pytest
import sre_constants

PY3 = (3, 0) <= sys.version_info < (4, 0)
PY36_PLUS = (3, 6) <= sys.version_info
PY37_PLUS = (3, 7) <= sys.version_info

if PY3:
    binary_type = bytes  # noqa
else:
    binary_type = str  # noqa


class TestSearchTemplate(unittest.TestCase):
    """Search template tests."""

    def test_infinite_loop_catch(self):
        """Test infinite loop catch."""

        with pytest.raises(bre.RecursionException):
            bre.compile_search(r'((?a)(?u))')

    def test_comments_with_scoped_verbose(self):
        """Test scoped verbose with comments (PY36+)."""

        if PY36_PLUS:
            pattern = bre.compile_search(
                r'''(?u)Test # \e(?#\e\)(?x:
                Test #\e(?#\e\)
                (Test # \e
                )Test #\e
                )Test # \e'''
            )

            self.assertEqual(
                pattern.pattern,
                r'''(?u)Test # \x1b(?#\e\)(?x:
                Test #\\e(?#\\e\)
                (Test # \\e
                )Test #\\e
                )Test # \x1b'''
            )

            self.assertTrue(pattern.match('Test # \x16TestTestTestTest # \x1b') is not None)

    def test_byte_string_named_chars(self):
        """Test byte string named char."""

        pattern = bre.compile_search(br'\N{Latin small letter a}')
        self.assertEqual(
            pattern.pattern,
            br'\141'
        )
        self.assertTrue(pattern.match(b'a') is not None)

        pattern = bre.compile_search(br'[^\N{Latin small letter a}]')
        self.assertEqual(
            pattern.pattern,
            br'[^\141]'
        )
        self.assertTrue(pattern.match(b'b') is not None)

        pattern = bre.compile_search(br'\N{black club suit}')
        self.assertEqual(
            pattern.pattern,
            b'[^\x00-\xff]'
        )
        self.assertTrue(pattern.match(b'a') is None)

        pattern = bre.compile_search(br'[\N{black club suit}]')
        self.assertEqual(
            pattern.pattern,
            b'[^\x00-\xff]'
        )
        self.assertTrue(pattern.match(b'a') is None)

        pattern = bre.compile_search(br'[^\N{black club suit}]')
        self.assertEqual(
            pattern.pattern,
            b'[\x00-\xff]'
        )
        self.assertTrue(pattern.match(b'a') is not None)

    def test_escape_char(self):
        """Test escape char."""

        pattern = bre.compile_search(
            r'test\etest[\e]{2}'
        )

        self.assertEqual(
            pattern.pattern,
            r'test\x1btest[\x1b]{2}'
        )

        self.assertTrue(pattern.match('test\x1btest\x1b\x1b') is not None)

    def test_comments(self):
        """Test comments v0."""

        pattern = bre.compile_search(
            r'''(?xu)
            Test # \p{XDigit}
            (Test (?#\p{XDigit}))
            Test \p{XDigit}
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?xu)
            Test # \\p{XDigit}
            (Test (?#\p{XDigit}))
            Test [0-9A-Fa-f]
            '''
        )

        self.assertTrue(pattern.match('TestTestTestA') is not None)

    def test_trailing_bslash(self):
        """Test trailing back slash."""

        with pytest.raises(sre_constants.error):
            pattern = bre.compile_search('test\\', re.UNICODE)

        with pytest.raises(sre_constants.error):
            pattern = bre.compile_search('test[\\', re.UNICODE)

        with pytest.raises(sre_constants.error):
            pattern = bre.compile_search('test(\\', re.UNICODE)

        pattern = bre.compile_search('\\Qtest\\', re.UNICODE)
        self.assertEqual(pattern.pattern, 'test\\\\')

    def test_escape_values_in_verbose_comments(self):
        """Test added escapes in verbose comments."""

        pattern = bre.compile_search(r'(?x)test # \l \p{numbers}', re.UNICODE)
        self.assertEqual(pattern.pattern, r'(?x)test # \\l \\p{numbers}', re.UNICODE)

    def test_char_group_nested_opening(self):
        """Test char group with nested opening [."""

        pattern = bre.compile_search(r'test [[] \N{black club suit}', re.UNICODE)
        self.assertEqual(pattern.pattern, 'test [[] \u2663', re.UNICODE)

    def test_inline_comments(self):
        """Test that we properly find inline comments and avoid them."""
        pattern = bre.compile_search(r'test(?#\l\p{^IsLatin})', re.UNICODE)
        m = pattern.match('test')
        self.assertEqual(pattern.pattern, r'test(?#\l\p{^IsLatin})')
        self.assertTrue(m is not None)

    def test_unicode_name(self):
        """Test Unicode block."""

        pattern = bre.compile_search(r'\N{black club suit}', re.UNICODE)
        m = pattern.match('\N{black club suit}')
        self.assertTrue(m is not None)
        pattern = bre.compile_search(r'[\N{black club suit}]')
        m = pattern.match('\N{black club suit}')
        self.assertTrue(m is not None)

    def test_unicode_block(self):
        """Test Unicode block."""

        pattern = bre.compile_search(r'\p{InBasicLatin}')
        m = pattern.match(r'a')
        self.assertTrue(m is not None)
        m = pattern.match(r'·')
        self.assertTrue(m is None)

    def test_unicode_block_specifier(self):
        """Test Unicode block by specifier."""

        pattern = bre.compile_search(r'\p{Block: BasicLatin}')
        m = pattern.match(r'a')
        self.assertTrue(m is not None)
        m = pattern.match(r'·')
        self.assertTrue(m is None)

    def test_inverse_unicode_block(self):
        """Test inverse Unicode block."""

        pattern = bre.compile_search(r'\p{^InBasicLatin}')
        m = pattern.match(r'a')
        self.assertTrue(m is None)
        m = pattern.match(r'·')
        self.assertTrue(m is not None)

    def test_inverse_unicode_block_specifier(self):
        """Test inverse Unicode block by specifier."""

        pattern = bre.compile_search(r'\p{^Block: BasicLatin}')
        m = pattern.match(r'a')
        self.assertTrue(m is None)
        m = pattern.match(r'·')
        self.assertTrue(m is not None)

    def test_unicode_script(self):
        """Test Unicode script."""

        pattern = bre.compile_search(r'\p{IsLatin}')
        m = pattern.match(r'a')
        self.assertTrue(m is not None)
        m = pattern.match(r'·')
        self.assertTrue(m is None)

    def test_unicode_script_specifier(self):
        """Test Unicode script by specifier."""

        pattern = bre.compile_search(r'\p{Script: Latin}')
        m = pattern.match(r'a')
        self.assertTrue(m is not None)
        m = pattern.match(r'·')
        self.assertTrue(m is None)

    def test_inverse_unicode_script(self):
        """Test inverse Unicode script."""

        pattern = bre.compile_search(r'\p{^IsLatin}')
        m = pattern.match(r'a')
        self.assertTrue(m is None)
        m = pattern.match(r'·')
        self.assertTrue(m is not None)

    def test_inverse_unicode_script_specifier(self):
        """Test inverse Unicode block by specifier."""

        pattern = bre.compile_search(r'\p{^Script: Latin}')
        m = pattern.match(r'a')
        self.assertTrue(m is None)
        m = pattern.match(r'·')
        self.assertTrue(m is not None)

    def test_posix_in_group_unicode(self):
        """Test posix in a group."""

        pattern = bre.compile_search(r'Test [[:graph:]]', re.UNICODE)
        self.assertNotEqual(pattern.pattern, r'Test [[:graph:]]')

    def test_posix_in_group_unicode_with_normal_form(self):
        r"""Test posix in a group against \p{} form."""

        pattern = bre.compile_search(r'Test [[:graph:]]', re.UNICODE)
        pattern2 = bre.compile_search(r'Test [\p{Graph}]', re.UNICODE)
        self.assertEqual(pattern.pattern, pattern2.pattern)

    def test_posix_in_group_ascii(self):
        """Test posix in a group for ASCII."""
        if PY3:
            pattern = bre.compile_search(r'Test [[:graph:]]', re.ASCII)
            pattern2 = bre.compile_search('Test [\u0021-\u007E]', re.ASCII)
        else:
            pattern = bre.compile_search(r'Test [[:graph:]]')
            pattern2 = bre.compile_search(r'Test [\u0021-\u007E]')
        self.assertEqual(pattern.pattern, pattern2.pattern)

    def test_not_posix_at_start_group(self):
        """Test a situation that is not a POSIX at the start of a group."""

        pattern = bre.compile_search(r'Test [:graph:]]')
        self.assertEqual(pattern.pattern, r'Test [:graph:]]')

    def test_ascii_upper_props(self):
        """Test ASCII uppercase properties."""

        pattern = bre.compile_search(br'EX\c+LE')
        m = pattern.match(br'EXAMPLE')
        self.assertTrue(m is not None)

    def test_ascii_upper_props_group(self):
        """Test ASCII uppercase properties in a character group."""

        pattern = bre.compile_search(br'EX[\c]+LE')
        m = pattern.match(br'EXAMPLE')
        self.assertTrue(m is not None)

    def test_ascii_lower_props(self):
        """Test ASCII lowercase properties."""

        pattern = bre.compile_search(br'EX\l+LE')
        m = pattern.match(br'EXampLE')
        self.assertTrue(m is not None)

    def test_ascii_lower_props_group(self):
        """Test ASCII uppercase properties in a char group."""

        pattern = bre.compile_search(br'EX[\l]+LE')
        m = pattern.match(br'EXampLE')
        self.assertTrue(m is not None)

    def test_ascii_props_mixed_group(self):
        """Test mixed ASCII properties in group."""

        pattern = bre.compile_search(br'EX[\l\c]+LE')
        m = pattern.match(br'EXaMpLE')
        self.assertTrue(m is not None)

    def test_ascii_props_mixed(self):
        """Test mixed ASCII properties."""

        pattern = bre.compile_search(br'EX\l\c\lLE')
        m = pattern.match(br'EXaMpLE')
        self.assertTrue(m is not None)

    def test_reverse_ascii_lower_props(self):
        """Test reverse ASCII lowercase properties."""

        pattern = bre.compile_search(br'EX\L+LE')
        m = pattern.match(br'EXAMPLE')
        self.assertTrue(m is not None)

    def test_reverse_ascii_lower_props_group(self):
        """Test reverse ASCII lowercase properties in a group."""

        pattern = bre.compile_search(br'EX[\L]+LE')
        m = pattern.match(br'EXAMPLE')
        self.assertTrue(m is not None)

    def test_reverse_ascii_upper_props(self):
        """Test reverse ASCII uppercase properties."""

        pattern = bre.compile_search(br'EX\C+LE')
        m = pattern.match(br'EXampLE')
        self.assertTrue(m is not None)

    def test_reverse_ascii_upper_props_group(self):
        """Test reverse ASCII uppercase properties in a group."""

        pattern = bre.compile_search(br'EX[\C]+LE')
        m = pattern.match(br'EXampLE')
        self.assertTrue(m is not None)

    def test_reverse_ascii_props_mixed_group(self):
        """Test reverse mixed ASCII properties in a group."""

        pattern = bre.compile_search(br'EX[\C\L]+LE')
        m = pattern.match(br'EXaMpLE')
        self.assertTrue(m is not None)

    def test_reverse_ascii_props_mixed(self):
        """Test reverse ASCII properties."""

        pattern = bre.compile_search(br'EX\C\L\CLE')
        m = pattern.match(br'EXaMpLE')
        self.assertTrue(m is not None)

    def test_unrecognized_backrefs(self):
        """Test unrecognized backrefs."""

        result = bre.SearchTemplate(r'Testing unrecognized backrefs \k!').apply()
        self.assertEqual(r'Testing unrecognized backrefs \k!', result)

    def test_quote(self):
        """Test quoting/escaping."""

        result = bre.SearchTemplate(r'Testing \Q(\s+[quote]*\s+)?\E!').apply()
        self.assertEqual(r'Testing %s!' % re.escape(r'(\s+[quote]*\s+)?'), result)

    def test_normal_backrefs(self):
        """
        Test normal builtin backrefs.

        They should all pass through unaltered.
        """

        result = bre.SearchTemplate(r'\a\b\f\n\r\t\v\A\b\B\d\D\s\S\w\W\Z\\[\b]').apply()
        self.assertEqual(r'\a\b\f\n\r\t\v\A\b\B\d\D\s\S\w\W\Z\\[\b]', result)

    def test_quote_no_end(self):
        r"""Test quote where no `\E` is defined."""

        result = bre.SearchTemplate(r'Testing \Q(quote) with no [end]!').apply()
        self.assertEqual(r'Testing %s' % re.escape(r'(quote) with no [end]!'), result)

    def test_quote_in_char_groups(self):
        """Test that quote backrefs are handled in character groups."""

        result = bre.SearchTemplate(r'Testing [\Qchar\E block] [\Q(AVOIDANCE)\E]!').apply()
        self.assertEqual(r'Testing [char block] [\(AVOIDANCE\)]!', result)

    def test_quote_in_char_groups_with_right_square_bracket_first(self):
        """Test that quote backrefs are handled in character groups that have a right square bracket as first char."""

        result = bre.SearchTemplate(r'Testing [^]\Qchar\E block] []\Q(AVOIDANCE)\E]!').apply()
        self.assertEqual(r'Testing [^]char block] []\(AVOIDANCE\)]!', result)

    def test_extraneous_end_char(self):
        r"""Test that stray '\E's get removed."""

        result = bre.SearchTemplate(r'Testing \Eextraneous end char\E!').apply()
        self.assertEqual(r'Testing extraneous end char!', result)

    def test_escaped_backrefs(self):
        """Ensure escaped backrefs don't get processed."""

        result = bre.SearchTemplate(r'\\cTesting\\C \\lescaped\\L \\Qbackrefs\\E!').apply()
        self.assertEqual(r'\\cTesting\\C \\lescaped\\L \\Qbackrefs\\E!', result)

    def test_escaped_escaped_backrefs(self):
        """Ensure escaping escaped backrefs do get processed."""

        result = bre.SearchTemplate(r'Testing escaped escaped \\\Qbackrefs\\\E!').apply()
        self.assertEqual(r'Testing escaped escaped \\backrefs\\\\!', result)

    def test_escaped_escaped_escaped_backrefs(self):
        """Ensure escaping escaped escaped backrefs don't get processed."""

        result = bre.SearchTemplate(r'Testing escaped escaped \\\\Qbackrefs\\\\E!').apply()
        self.assertEqual(r'Testing escaped escaped \\\\Qbackrefs\\\\E!', result)

    def test_escaped_escaped_escaped_escaped_backrefs(self):
        """
        Ensure escaping escaped escaped escaped backrefs do get processed.

        This is far enough to prove out that we are handling them well enough.
        """

        result = bre.SearchTemplate(r'Testing escaped escaped \\\\\Qbackrefs\\\\\E!').apply()
        self.assertEqual(r'Testing escaped escaped \\\\backrefs\\\\\\\\!', result)

    def test_normal_escaping(self):
        """Normal escaping should be unaltered."""

        result = bre.SearchTemplate(r'\n \\n \\\n \\\\n \\\\\n').apply()
        self.assertEqual(r'\n \\n \\\n \\\\n \\\\\n', result)

    def test_normal_escaping2(self):
        """Normal escaping should be unaltered part2."""

        result = bre.SearchTemplate(r'\y \\y \\\y \\\\y \\\\\y').apply()
        self.assertEqual(r'\y \\y \\\y \\\\y \\\\\y', result)

    def test_unicode_shorthand_properties_capital(self):
        """
        Exercising that Unicode properties are built correctly by testing shorthand lower and upper.

        We want to test uppercase and make sure things make sense,
        and then test lower case later.  Not extensive, just making sure its generally working.
        """

        pattern = bre.compile_search(r'EX\cMPLE', re.UNICODE)
        m = pattern.match(r'EXÁMPLE')
        self.assertTrue(m is not None)
        m = pattern.match(r'exámple')
        self.assertTrue(m is None)

    def test_unicode_shorthand_properties_lower(self):
        """Exercise the Unicode shorthand properties for lower case."""

        pattern = bre.compile_search(r'ex\lmple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('EXÁMPLE')
        self.assertTrue(m is None)

    def test_unicode_shorthand_properties_in_char_group(self):
        """Exercise the Unicode shorthand properties inside a char group."""

        pattern = bre.compile_search(r'ex[\l\c]mple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('exÁmple')
        self.assertTrue(m is not None)

    def test_unicode_shorthand_properties_with_string_flag(self):
        """Exercise the Unicode shorthand properties with an re string flag `(?u)`."""

        pattern = bre.compile_search(r'ex[\l\c]mple(?u)')
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('exÁmple')
        self.assertTrue(m is not None)

    def test_unicode_shorthand_ascii_only(self):
        """Ensure that when the Unicode flag is not used, only ASCII properties are used."""

        flags = bre.ASCII if PY3 else 0
        pattern = bre.compile_search(r'ex\lmple', flags)
        m = pattern.match('exámple')
        self.assertTrue(m is None)
        m = pattern.match('example')
        self.assertTrue(m is not None)

    def test_unicode_properties_capital(self):
        """
        Exercising that Unicode properties are built correctly.

        We want to test uppercase and make sure things make sense,
        and then test lower case later.  Not extensive, just making sure its generally working.
        """

        pattern = bre.compile_search(r'EX\p{Lu}MPLE', re.UNICODE)
        m = pattern.match(r'EXÁMPLE')
        self.assertTrue(m is not None)
        m = pattern.match(r'EXáMPLE')
        self.assertTrue(m is None)

    def test_unicode_properties_lower(self):
        """Exercise the Unicode properties for lower case."""

        pattern = bre.compile_search(r'ex\p{Ll}mple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('exÁmple')
        self.assertTrue(m is None)

    def test_unicode_properties_in_char_group(self):
        """Exercise the Unicode properties inside a character group."""

        pattern = bre.compile_search(r'ex[\p{Ll}\p{Lu}]mple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('exÁmple')
        self.assertTrue(m is not None)

    def test_unicode_short_properties_letters(self):
        """Exercise the Unicode shortened properties for letters."""

        pattern = bre.compile_search(r'ex\pLmple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('ex!mple')
        self.assertTrue(m is None)

    def test_unicode_short_properties_in_char_group(self):
        """Exercise the Unicode shortened properties inside a character group."""

        pattern = bre.compile_search(r'ex[\pL]mple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('ex!mple')
        self.assertTrue(m is None)

    def test_inverse_unicode_short_properties_letters(self):
        """Exercise the inverse Unicode shortened properties for letters."""

        pattern = bre.compile_search(r'ex\PLmple', re.UNICODE)
        m = pattern.match('ex!mple')
        self.assertTrue(m is not None)
        m = pattern.match('exámple')
        self.assertTrue(m is None)

    def test_inverse_unicode_short_properties_in_char_group(self):
        """Exercise the inverse Unicode shortened properties inside a character group."""

        pattern = bre.compile_search(r'ex[\PL]mple', re.UNICODE)
        m = pattern.match('ex!mple')
        self.assertTrue(m is not None)
        m = pattern.match('exÁmple')
        self.assertTrue(m is None)

    def test_unicode_properties_names(self):
        """Test Unicode group friendly names."""

        pattern = bre.compile_search(r'ex[\p{Letter}]mple', re.UNICODE)
        m = pattern.match('exámple')
        self.assertTrue(m is not None)
        m = pattern.match('exÁmple')
        self.assertTrue(m is not None)

    def test_unicode_properties_inverse(self):
        """Exercising inverse Unicode properties."""

        pattern = bre.compile_search(r'\P{Po}', re.UNICODE)
        m = pattern.match(r'·')
        self.assertTrue(m is None)
        m = pattern.match(r'P')
        self.assertTrue(m is not None)

    def test_negated_unicode_properties_inverse(self):
        """Exercising negated inverse Unicode properties."""

        pattern = bre.compile_search(r'[^\P{Po}]', re.UNICODE)
        m = pattern.match(r'·')
        self.assertTrue(m is not None)
        m = pattern.match(r'P')
        self.assertTrue(m is None)

    def test_binary_property(self):
        r"""Binary patterns should match `\p` references."""

        pattern = bre.compile_search(br'EX\p{Lu}MPLE')
        m = pattern.match(br'EXAMPLE')
        self.assertTrue(m is not None)

    def test_binary_property_no_value(self):
        """Test when a property returns nothing in byte string."""

        pattern = bre.compile_search(br'EX\p{OtherAlphabetic}MPLE')
        self.assertEqual(pattern.pattern, b'EX[^\x00-\xff]MPLE')

        pattern = bre.compile_search(br'EX\P{OtherAlphabetic}MPLE')
        self.assertEqual(pattern.pattern, b'EX[\x00-\xff]MPLE')

        pattern = bre.compile_search(br'EX[\p{OtherAlphabetic}]MPLE')
        self.assertEqual(pattern.pattern, b'EX[^\x00-\xff]MPLE')

        pattern = bre.compile_search(br'EX[\P{OtherAlphabetic}]MPLE')
        self.assertEqual(pattern.pattern, b'EX[\x00-\xff]MPLE')

        pattern = bre.compile_search(br'EX[^\p{OtherAlphabetic}]MPLE')
        self.assertEqual(pattern.pattern, b'EX[\x00-\xff]MPLE')

        pattern = bre.compile_search(br'EX[^\P{OtherAlphabetic}]MPLE')
        self.assertEqual(pattern.pattern, b'EX[^\x00-\xff]MPLE')

        pattern = bre.compile_search(br'EX[\p{OtherAlphabetic}a]MPLE')
        self.assertEqual(pattern.pattern, b'EX[a]MPLE')

        pattern = bre.compile_search(br'EX[\P{OtherAlphabetic}a]MPLE')
        self.assertEqual(pattern.pattern, b'EX[\x00-\xffa]MPLE')

        pattern = bre.compile_search(br'EX[^\p{OtherAlphabetic}a]MPLE')
        self.assertEqual(pattern.pattern, b'EX[^a]MPLE')

        pattern = bre.compile_search(br'EX[^\P{OtherAlphabetic}a]MPLE')
        self.assertEqual(pattern.pattern, b'EX[^\x00-\xffa]MPLE')

    def test_unicode_and_verbose_flag(self):
        """Test that `VERBOSE` and `UNICODE` together come through."""

        pattern = bre.compile_search(r'Some pattern', flags=bre.VERBOSE | bre.UNICODE)
        self.assertTrue(pattern.flags & bre.UNICODE and pattern.flags & bre.VERBOSE)

    def test_detect_verbose_string_flag_at_end(self):
        """Test verbose string flag `(?x)` at end."""

        template = bre.SearchTemplate(
            r'''
            This is a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [#\ ] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ a # \Qcomment\E (?x)
            '''
        )
        template.apply()

        self.assertTrue(template.verbose)

    def test_ignore_verbose_string(self):
        """Test verbose string flag `(?x)` in character set."""

        pattern = bre.compile_search(
            r'''
            This is not a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [#\ (?x)] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ not a # \Qcomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''
            This is not a # comment
            This is not a \# comment
            This is not a [#\ (?x)] comment
            This is not a [\#] comment
            This\ is\ not a # comment
            '''
        )

    def test_verbose_string_in_quote(self):
        """Test verbose string flag `(?x)` in quote."""

        pattern = bre.compile_search(
            r'''
            This is not a # \Qcomment(?x)\E
            This is not a \# \Qcomment\E
            This is not a [#\ ] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ not a # \Qcomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''
            This is not a # comment\(\?x\)
            This is not a \# comment
            This is not a [#\ ] comment
            This is not a [\#] comment
            This\ is\ not a # comment
            '''
        )

    def test_unicode_string_flag(self):
        """Test finding Unicode/ASCII string flag."""

        if PY3:
            template = bre.SearchTemplate(r'Testing for (?ia) ASCII flag.', False, None)
            template.apply()
            self.assertFalse(template.unicode)
        else:
            template = bre.SearchTemplate(r'Testing for (?iu) Unicode flag.', False, None)
            template.apply()
            self.assertTrue(template.unicode)

    def test_unicode_string_flag_in_group(self):
        """Test ignoring Unicode/ASCII string flag in group."""

        if PY3:
            template = bre.SearchTemplate(r'Testing for [(?ia)] ASCII flag.', False, None)
            template.apply()
            self.assertTrue(template.unicode)
        else:
            template = bre.SearchTemplate(r'Testing for [(?iu)] Unicode flag.', False, None)
            template.apply()
            self.assertFalse(template.unicode)

    def test_unicode_string_flag_escaped(self):
        """Test ignoring Unicode/ASCII string flag in group."""

        if PY3:
            template = bre.SearchTemplate(r'Testing for \(?ia) ASCII flag.', False, None)
            template.apply()
            self.assertTrue(template.unicode)
        else:
            template = bre.SearchTemplate(r'Testing for \(?iu) Unicode flag.', False, None)
            template.apply()
            self.assertFalse(template.unicode)

    def test_unicode_string_flag_unescaped(self):
        """Test unescaped Unicode string flag."""

        if PY3:
            template = bre.SearchTemplate(r'Testing for \\(?ia) ASCII flag.', False, None)
            template.apply()
            self.assertFalse(template.unicode)
        else:
            template = bre.SearchTemplate(r'Testing for \\(?iu) Unicode flag.', False, None)
            template.apply()
            self.assertTrue(template.unicode)

    def test_unicode_string_flag_escaped_deep(self):
        """Test deep escaped Unicode flag."""

        if PY3:
            template = bre.SearchTemplate(r'Testing for \\\(?ia) ASCII flag.', False, None)
            template.apply()
            self.assertTrue(template.unicode)
        else:
            template = bre.SearchTemplate(r'Testing for \\\(?iu) Unicode flag.', False, None)
            template.apply()
            self.assertFalse(template.unicode)

    def test_verbose_comment_no_nl(self):
        """Test verbose comment with no newline."""

        pattern = bre.compile_search(
            '(?x)This is a # comment with no new line'
        )

        self.assertEqual(
            pattern.pattern,
            '(?x)This is a # comment with no new line'
        )

    def test_other_backrefs(self):
        """Test that other backrefs make it through."""

        pattern = bre.compile_search(
            r'''(?x)
            This \bis a # \Qcomment\E
            This is\w+ not a \# \Qcomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?x)
            This \bis a # comment
            This is\w+ not a \# comment
            '''
        )

    def test_re_pattern_input(self):
        """Test that search pattern input can be a compiled re pattern."""

        pattern1 = re.compile("(test)")
        pattern2 = bre.compile_search(pattern1)
        m = pattern2.match('test')
        self.assertTrue(m is not None)


class TestReplaceTemplate(unittest.TestCase):
    """Test replace template."""

    def test_replace_unicode_name_ascii_range(self):
        """Test replacing Unicode names in the ASCII range."""

        pattern = re.compile(r"(some)(.+?)(pattern)(!)")
        expand = bre.compile_replace(
            pattern,
            r'\1 \N{Latin small letter a}\l\N{Latin Capital Letter A} and '
            r'\LSPAN \N{Latin Capital Letter A}\E and Escaped \\N{Latin Capital Letter A}\E \3'
        )
        results = expand(pattern.match('some test pattern!'))

        self.assertEqual(
            'some aa and span a and Escaped \\N{Latin Capital Letter A} pattern',
            results
        )

    def test_replace_unicode_name(self):
        """Test replacing Unicode names."""

        pattern = re.compile(r"(some)(.+?)(pattern)(!)")
        expand = bre.compile_replace(
            pattern,
            r'\1 \N{Black club suit}\l\N{Greek Capital Letter omega} and '
            r'\LSPAN \N{Greek Capital Letter omega}\E and Escaped \\N{Greek Capital Letter omega}\E \3'
        )
        results = expand(pattern.match('some test pattern!'))

        self.assertEqual(
            'some \u2663\u03c9 and span \u03c9 and Escaped \\N{Greek Capital Letter omega} pattern',
            results
        )

    def test_format_replace_unicode_name(self):
        """Test replacing format Unicode names."""

        pattern = re.compile(r"(some)(.+?)(pattern)(!)")
        expandf = bre.compile_replace(
            pattern,
            r'{1} \N{Black club suit}\l\N{Greek Capital Letter omega} and '
            r'\LSPAN \N{Greek Capital Letter omega}\E and Escaped \\N{{Greek Capital Letter omega}}\E {3}',
            bre.FORMAT
        )
        results = expandf(pattern.match('some test pattern!'))

        self.assertEqual(
            'some \u2663\u03c9 and span \u03c9 and Escaped \\N{Greek Capital Letter omega} pattern',
            results
        )

    def test_get_replace_template_string(self):
        """Test retrieval of the replace template original string."""

        pattern = re.compile(r"(some)(.+?)(pattern)(!)")
        template = bre.ReplaceTemplate(pattern, r'\c\1\2\C\3\E\4')

        self.assertEqual(r'\c\1\2\C\3\E\4', template.get_base_template())

    def test_uppercase(self):
        """Test uppercase."""

        text = "This is a test for uppercase!"
        pattern = re.compile(r"(.+?)(uppercase)(!)")
        expand = bre.compile_replace(pattern, r'\1\c\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for Uppercase!', results)

    def test_lowercase(self):
        """Test lowercase."""

        text = "This is a test for LOWERCASE!"
        pattern = re.compile(r"(.+?)(LOWERCASE)(!)")
        expand = bre.compile_replace(pattern, r'\1\l\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for lOWERCASE!', results)

    def test_span_uppercase(self):
        """Test span uppercase."""

        text = "This is a test for uppercase!"
        pattern = re.compile(r"(.+?)(uppercase)(!)")
        expand = bre.compile_replace(pattern, r'\1\C\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for UPPERCASE!', results)

    def test_span_lowercase(self):
        """Test span lowercase."""

        text = "This is a test for LOWERCASE!"
        pattern = re.compile(r"(.+?)(LOWERCASE)(!)")
        expand = bre.compile_replace(pattern, r'\1\L\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for lowercase!', results)

    def test_single_stacked_case(self):
        """Test stacked casing of non-spans."""

        text = "This is a test for stacking!"
        pattern = re.compile(r"(.+?)(stacking)(!)")
        expand = bre.compile_replace(pattern, r'\1\c\l\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for Stacking!', results)

    def test_span_stacked_case(self):
        """Test stacked casing of non-spans in and out of a span."""

        text = "This is a test for STACKING!"
        pattern = re.compile(r"(.+?)(STACKING)(!)")
        expand = bre.compile_replace(pattern, r'\1\c\L\l\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for Stacking!', results)

    def test_single_case_followed_by_bslash(self):
        """Test single backslash following a single case reference."""

        text = "This is a test!"
        pattern = re.compile(r"(.+?)(test)(!)")
        expand = bre.compile_replace(pattern, r'\1\c\\\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a \\test!', results)

    def test_span_case_followed_by_bslash(self):
        """Test single backslash following a span case reference."""

        text = "This is a test!"
        pattern = re.compile(r"(.+?)(test)(!)")
        expand = bre.compile_replace(pattern, r'\1\C\\\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a \\TEST!', results)

    def test_single_span_stacked_literal(self):
        """Test single backslash before a single case reference before a literal."""

        text = "This is a test!"
        pattern = re.compile(r"(.+?)(test)(!)")
        expand = bre.compile_replace(pattern, r'Test \l\Cstacked\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('Test sTACKED!', results)

    def test_extraneous_end_char(self):
        """Test for extraneous end characters."""

        text = "This is a test for extraneous \\E chars!"
        pattern = re.compile(r"(.+?)(extraneous)(.+)")
        expand = bre.compile_replace(pattern, r'\1\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for extraneous \\E chars!', results)

    def test_normal_backrefs(self):
        """Test for normal backrefs."""

        text = "This is a test for normal backrefs!"
        pattern = re.compile(r"(.+?)(normal)(.+)")
        expand = bre.compile_replace(pattern, '\\1\\2\t\\3 \u0067\147\v\f\n')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for normal\t backrefs! gg\v\f\n', results)

    def test_span_case_no_end(self):
        r"""Test case where no \E is defined."""

        text = "This is a test for uppercase with no end!"
        pattern = re.compile(r"(.+?)(uppercase)(.+)")
        expand = bre.compile_replace(pattern, r'\1\C\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for UPPERCASE WITH NO END!', results)

    def test_span_upper_after_upper(self):
        """Test uppercase followed by uppercase span."""

        text = "This is a complex uppercase test!"
        pattern = re.compile(r"(.+?)(uppercase)(.+)")
        expand = bre.compile_replace(pattern, r'\1\c\C\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE test!', results)

    def test_span_lower_after_lower(self):
        """Test lowercase followed by lowercase span."""

        text = "This is a complex LOWERCASE test!"
        pattern = re.compile(r"(.+?)(LOWERCASE)(.+)")
        expand = bre.compile_replace(pattern, r'\1\l\L\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase test!', results)

    def test_span_upper_around_upper(self):
        """Test uppercase span around an uppercase."""

        text = "This is a complex uppercase test!"
        pattern = re.compile(r"(.+?)(uppercase)(.+)")
        expand = bre.compile_replace(pattern, r'\1\C\c\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE test!', results)

    def test_span_lower_around_lower(self):
        """Test lowercase span around an lowercase."""

        text = "This is a complex LOWERCASE test!"
        pattern = re.compile(r"(.+?)(LOWERCASE)(.+)")
        expand = bre.compile_replace(pattern, r'\1\L\l\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase test!', results)

    def test_upper_after_upper(self):
        """Test uppercase after uppercase."""

        text = "This is a complex uppercase test!"
        pattern = re.compile(r"(.+?)(uppercase)(.+)")
        expand = bre.compile_replace(pattern, r'\1\c\c\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex Uppercase test!', results)

    def test_upper_span_inside_upper_span(self):
        """Test uppercase span inside uppercase span."""

        text = "This is a complex uppercase test!"
        pattern = re.compile(r"(.+?)(uppercase)(.+)")
        expand = bre.compile_replace(pattern, r'\1\C\C\2\E\3\E')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE TEST!', results)

    def test_lower_after_lower(self):
        """Test lowercase after lowercase."""

        text = "This is a complex LOWERCASE test!"
        pattern = re.compile(r"(.+?)(LOWERCASE)(.+)")
        expand = bre.compile_replace(pattern, r'\1\l\l\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lOWERCASE test!', results)

    def test_lower_span_inside_lower_span(self):
        """Test lowercase span inside lowercase span."""

        text = "This is a complex LOWERCASE TEST!"
        pattern = re.compile(r"(.+?)(LOWERCASE)(.+)")
        expand = bre.compile_replace(pattern, r'\1\L\L\2\E\3\E')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase test!', results)

    def test_span_upper_after_lower(self):
        """Test lowercase followed by uppercase span."""

        text = "This is a complex uppercase test!"
        pattern = re.compile(r"(.+?)(uppercase)(.+)")
        expand = bre.compile_replace(pattern, r'\1\l\C\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex uPPERCASE test!', results)

    def test_span_lower_after_upper(self):
        """Test uppercase followed by lowercase span."""

        text = "This is a complex LOWERCASE test!"
        pattern = re.compile(r"(.+?)(LOWERCASE)(.+)")
        expand = bre.compile_replace(pattern, r'\1\c\L\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex Lowercase test!', results)

    def test_span_upper_around_lower(self):
        """Test uppercase span around a lowercase."""

        text = "This is a complex uppercase test!"
        pattern = re.compile(r"(.+?)(uppercase)(.+)")
        expand = bre.compile_replace(pattern, r'\1\C\l\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex uPPERCASE test!', results)

    def test_span_lower_around_upper(self):
        """Test lowercase span around an uppercase."""

        text = "This is a complex LOWERCASE test!"
        pattern = re.compile(r"(.+?)(LOWERCASE)(.+)")
        expand = bre.compile_replace(pattern, r'\1\L\c\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex Lowercase test!', results)

    def test_end_after_single_case(self):
        r"""Test that \E after a single case such as \l is handled proper."""

        text = "This is a single case end test!"
        pattern = re.compile(r"(.+?)(case)(.+)")
        expand = bre.compile_replace(pattern, r'\1\l\E\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a single case end test!', results)

    def test_end_after_single_case_nested(self):
        r"""Test that \E after a single case such as \l is handled proper inside a span."""

        text = "This is a nested single case end test!"
        pattern = re.compile(r"(.+?)(case)(.+)")
        expand = bre.compile_replace(pattern, r'\1\C\2\c\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a nested single CASE end test!', results)

    def test_single_case_at_end(self):
        """Test when a single case backref is the final char."""

        text = "This is a single case at end test!"
        pattern = re.compile(r"(.+?)(case)(.+)")
        expand = bre.compile_replace(pattern, r'\1\2\3\c')
        results = expand(pattern.match(text))

        self.assertEqual('This is a single case at end test!', results)

    def test_single_case_not_on_group(self):
        """Test single case when not applied to a group."""

        text = "This is a single case test that is not on a group!"
        pattern = re.compile(r"(.+)")
        expand = bre.compile_replace(pattern, r'\cstill works!')
        results = expand(pattern.match(text))

        self.assertEqual('Still works!', results)

    def test_case_span_not_on_group(self):
        """Test case span when not applied to a group."""

        text = "This is a case test that is not on a group!"
        pattern = re.compile(r"(.+)")
        expand = bre.compile_replace(pattern, r'\Cstill\E works!')
        results = expand(pattern.match(text))

        self.assertEqual('STILL works!', results)

    def test_escaped_backrefs(self):
        """Test escaped backrefs."""

        text = "This is a test of escaped backrefs!"
        pattern = re.compile(r"(.+)")
        expand = bre.compile_replace(pattern, r'\\\\l\\c\1')
        results = expand(pattern.match(text))

        self.assertEqual(r'\\l\cThis is a test of escaped backrefs!', results)

    def test_escaped_slash_before_backref(self):
        """Test deeper escaped slash."""

        text = "this is a test of escaped slash backrefs!"
        pattern = re.compile(r"(.+)")
        expand = bre.compile_replace(pattern, r'\\\\\lTest: \\\c\1')
        results = expand(pattern.match(text))

        self.assertEqual(r'\\test: \This is a test of escaped slash backrefs!', results)

    def test_normal_escaping(self):
        """Test normal escaped slash."""

        text = "This is a test of normal escaping!"
        pattern = re.compile(r"(.+)")
        repl_pattern = r'\t \\t \\\t \\\\t \\\\\t'
        expand = bre.compile_replace(pattern, repl_pattern)
        m = pattern.match(text)
        results = expand(m)
        results2 = pattern.sub(repl_pattern, text)

        self.assertEqual(results2, results)
        self.assertEqual('\t \\t \\\t \\\\t \\\\\t', results)

    def test_binary_normal_escaping(self):
        """Test binary normal escaped slash."""

        text = b"This is a test of normal escaping!"
        pattern = re.compile(br"(.+)")
        repl_pattern = br'\t \\t \\\t \\\\t \\\\\t'
        expand = bre.compile_replace(pattern, repl_pattern)
        m = pattern.match(text)
        results = expand(m)
        results2 = pattern.sub(repl_pattern, text)

        self.assertEqual(results2, results)
        self.assertEqual(b'\t \\t \\\t \\\\t \\\\\t', results)

    def test_escaped_slash_at_eol(self):
        """Test escaped slash at end of line."""

        text = "This is a test of eol escaping!"
        pattern = re.compile(r"(.+)")
        expand = bre.compile_replace(pattern, r'\\\\')
        results = expand(pattern.match(text))

        self.assertEqual('\\\\', results)

    def test_ignore_group(self):
        """Test that backrefs inserted by matching groups are passed over."""

        text = r"This is a test to see if \Cbackre\Efs in gr\coups get ig\Lnor\led proper!"
        pattern = re.compile(r"(This is a test to see if \\Cbackre\\Efs )(.+?)(ig\\Lnor\\led )(proper)(!)")
        expand = bre.compile_replace(pattern, r'Here is the first \C\1\Ethe second \c\2third \L\3\E\4\5')
        results = expand(pattern.match(text))

        self.assertEqual(
            r'Here is the first THIS IS A TEST TO SEE IF \CBACKRE\EFS the second In gr\coups get third '
            r'ig\lnor\led proper!',
            results
        )

    def test_zero_width_boundary(self):
        """Test that we handle zero width boundaries."""

        text = '//\nfunc (xx *XX) getChild(int i) PararseTree {\n    return null\n}\n\n//'
        pattern = bre.compile_search(r'^(\s*func \(xx.+?\()(\w+.+?)\s+([^,)]+)((?:,[^)]*)?)(\)\s+.+?\{)', bre.MULTILINE)
        expand = bre.compile_replace(pattern, r'\1\3 \2\4\5')
        results = pattern.sub(expand, text)

        self.assertEqual(
            '//\nfunc (xx *XX) getChild(i int) PararseTree {\n    return null\n}\n\n//',
            results
        )

    def test_mixed_groups1(self):
        """Test mix of upper and lower case with named groups and a string replace pattern."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.+?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = re.compile(text_pattern)

        # Use text pattern directly.
        expand = bre.compile_replace(pattern, r'\l\C\g<first>\l\g<second>\L\c\g<third>\E\g<fourth>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('tHIS iS A TEST FOR Named capture GROUPS!', results)

    def test_mixed_groups2(self):
        """Test mix of upper and lower case with group indexes and a string replace pattern."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.+?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = re.compile(text_pattern)

        # This will pass because we do not need to resolve named groups.
        expand = bre.compile_replace(pattern, r'\l\C\g<1>\l\g<2>\L\c\g<3>\E\g<4>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('tHIS iS A TEST FOR Named capture GROUPS!', results)

    def test_mixed_groups3(self):
        """Test mix of upper and lower case with named groups and a compiled replace pattern."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.+?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = re.compile(text_pattern)

        # Now using compiled pattern, we can use named groups in replace template.
        expand = bre.compile_replace(pattern, r'\l\C\g<first>\l\g<second>\L\c\g<third>\E\g<fourth>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('tHIS iS A TEST FOR Named capture GROUPS!', results)

    def test_as_replace_function(self):
        """Test that replace can be used as a replace function."""

        text = "this will be fed into re.subn!  Here we go!  this will be fed into re.subn!  Here we go!"
        text_pattern = r"(?P<first>this )(?P<second>.+?)(!)"
        pattern = bre.compile_search(text_pattern)
        replace = bre.compile_replace(pattern, r'\c\g<first>is awesome\g<3>')
        result, count = pattern.subn(replace, text)

        self.assertEqual(result, "This is awesome!  Here we go!  This is awesome!  Here we go!")
        self.assertEqual(count, 2)

    def test_binary_replace(self):
        """Test that binary regex result is a binary string."""

        text = b"This is some binary text!"
        pattern = bre.compile_search(br"This is (some binary text)!")
        expand = bre.compile_replace(pattern, br'\C\1\E')
        m = pattern.match(text)
        result = expand(m)
        self.assertEqual(result, b"SOME BINARY TEXT")
        self.assertTrue(isinstance(result, binary_type))

    def test_template_replace(self):
        """Test replace by passing in replace function."""

        text = "Replace with function test!"
        pattern = bre.compile_search('(.+)')
        repl = bre.ReplaceTemplate(pattern, 'Success!')
        expand = bre.compile_replace(pattern, repl)

        m = pattern.match(text)
        result = expand(m)

        self.assertEqual('Success!', result)

    def test_numeric_groups(self):
        """Test numeric capture groups."""

        text = "this is a test for numeric capture groups!"
        text_pattern = r"(this )(.+?)(numeric capture )(groups)(!)"
        pattern = re.compile(text_pattern)

        # This will pass because we do not need to resolve named groups.
        expand = bre.compile_replace(pattern, r'\l\C\g<0001>\l\g<02>\L\c\g<03>\E\g<004>\E\5\n\C\g<000>\E')
        results = expand(pattern.match(text))
        self.assertEqual(
            'tHIS iS A TEST FOR Numeric capture GROUPS!\nTHIS IS A TEST FOR NUMERIC CAPTURE GROUPS!',
            results
        )

    def test_numeric_format_groups(self):
        """Test numeric format capture groups."""

        text = "this is a test for numeric capture groups!"
        text_pattern = r"(this )(.+?)(numeric capture )(groups)(!)"
        pattern = re.compile(text_pattern)

        expand = bre.compile_replace(pattern, r'\l\C{0001}\l{02}\L\c{03}\E{004}\E{5}\n\C{000}\E', bre.FORMAT)
        results = expand(pattern.match(text))
        self.assertEqual(
            'tHIS iS A TEST FOR Numeric capture GROUPS!\nTHIS IS A TEST FOR NUMERIC CAPTURE GROUPS!',
            results
        )

    def test_escaped_format_groups(self):
        """Test escaping of format capture groups."""

        text = "this is a test for format capture groups!"
        text_pattern = r"(this )(.+?)(format capture )(groups)(!)"
        pattern = re.compile(text_pattern)

        expand = bre.compile_replace(
            pattern, r'\l\C{{0001}}\l{{{02}}}\L\c{03}\E{004}\E{5}\n\C{000}\E', bre.FORMAT
        )
        results = expand(pattern.match(text))
        self.assertEqual(
            '{0001}{IS A TEST FOR }Format capture GROUPS!\nTHIS IS A TEST FOR FORMAT CAPTURE GROUPS!',
            results
        )

    def test_format_auto(self):
        """Test auto format capture groups."""

        text = "this is a test for format capture groups!"
        text_pattern = r"(this )(.+?)(format capture )(groups)(!)"
        pattern = re.compile(text_pattern)

        expand = bre.compile_replace(
            pattern, r'\C{}\E\n\l\C{}\l{}\L\c{}\E{}\E{}{{}}', bre.FORMAT
        )
        results = expand(pattern.match(text))
        self.assertEqual(
            'THIS IS A TEST FOR FORMAT CAPTURE GROUPS!\ntHIS iS A TEST FOR Format capture GROUPS!{}',
            results
        )

    def test_format_captures(self):
        """Test format capture indexing."""

        text = "abababab"
        text_pattern = r"(\w)+"
        pattern = re.compile(text_pattern)

        expand = bre.compile_replace(
            pattern, r'{1[0]}{1[-1]}{1[0]}', bre.FORMAT
        )
        results = expand(pattern.match(text))
        self.assertEqual(
            'bbb',
            results
        )

    def test_format_auto_captures(self):
        """Test format auto capture indexing."""

        text = "abababab"
        text_pattern = r"(\w)+"
        pattern = re.compile(text_pattern)

        expand = bre.compile_replace(
            pattern, r'{[-1]}{[0]}', bre.FORMAT
        )
        results = expand(pattern.match(text))
        self.assertEqual(
            'ababababb',
            results
        )

    def test_format_capture_bases(self):
        """Test capture bases."""

        text = "abababab"
        text_pattern = r"(\w)+"
        pattern = re.compile(text_pattern)

        expand = bre.compile_replace(
            pattern, r'{1[-0x1]}{1[-0o1]}{1[-0b1]}', bre.FORMAT
        )
        results = expand(pattern.match(text))
        self.assertEqual(
            'bbb',
            results
        )

    def test_binary_format_capture_bases(self):
        """Test capture bases."""

        text = b"abababab"
        text_pattern = br"(\w)+"
        pattern = re.compile(text_pattern)

        expand = bre.compile_replace(
            pattern, br'{1[-0x1]}{1[-0o1]}{1[-0b1]}', bre.FORMAT
        )
        results = expand(pattern.match(text))
        self.assertEqual(
            b'bbb',
            results
        )

    def test_format_escapes(self):
        """Test format escapes."""

        text = "abababab"
        text_pattern = r"(\w)+"
        pattern = re.compile(text_pattern)

        expand = bre.compile_replace(
            pattern, r'{1[-1]}\g<1>\\g<1>\1\\2\\\3', bre.FORMAT
        )
        results = expand(pattern.match(text))
        self.assertEqual(
            'b\\g<1>\\g<1>\1\\2\\\3',
            results
        )

    def test_format_escapes_before_group(self):
        """Test format escapes before group."""

        text = "abababab"
        text_pattern = r"(\w)+"
        pattern = re.compile(text_pattern)

        expand = bre.compile_replace(
            pattern, r'\{1[-1]}\\{1[-1]}', bre.FORMAT
        )
        results = expand(pattern.match(text))
        self.assertEqual(
            '\\b\\b',
            results
        )

    def test_dont_case_special_refs(self):
        """Test that we don't case Unicode and bytes tokens, but case the character."""

        # Unicode and bytes should get evaluated proper
        pattern = re.compile('Test')
        expand = bre.compile_replace(pattern, r'\x57\u0057\u0109\C\u0077\u0109\n\x77\E\l\x57\c\u0109\c\u0077')
        results = expand(pattern.match('Test'))
        self.assertEqual('WW\u0109W\u0108\nWw\u0108W', results)

        expandf = bre.compile_replace(pattern, r'\C\u0109\n\x77\E\l\x57\c\u0109', bre.FORMAT)
        results = expandf(pattern.match('Test'))
        self.assertEqual('\u0108\nWw\u0108', results)

        # Wide Unicode must be evaluated before narrow Unicode
        pattern = re.compile('Test')
        expand = bre.compile_replace(pattern, r'\C\U00000109\n\x77\E\l\x57\c\U00000109')
        results = expand(pattern.match('Test'))
        self.assertEqual('\u0108\nWw\u0108', results)

        expandf = bre.compile_replace(pattern, r'\C\U00000109\n\x77\E\l\x57\c\U00000109', bre.FORMAT)
        results = expandf(pattern.match('Test'))
        self.assertEqual('\u0108\nWw\u0108', results)

        # Python 3.7 will choke on \U and \u as invalid escapes, so
        # don't bother running these tests there.
        if not PY37_PLUS:
            # Binary doesn't care about Unicode, but should evaluate bytes
            pattern = re.compile(b'Test')
            expand = bre.compile_replace(pattern, br'\C\u0109\n\x77\E\l\x57\c\u0109')
            results = expand(pattern.match(b'Test'))
            self.assertEqual(b'\\U0109\nWw\\u0109', results)

            expandf = bre.compile_replace(pattern, br'\C\u0109\n\x77\E\l\x57\c\u0109', bre.FORMAT)
            results = expandf(pattern.match(b'Test'))
            self.assertEqual(b'\\U0109\nWw\\u0109', results)

            pattern = re.compile(b'Test')
            expand = bre.compile_replace(pattern, br'\C\U00000109\n\x77\E\l\x57\c\U00000109')
            results = expand(pattern.match(b'Test'))
            self.assertEqual(b'\U00000109\nWw\U00000109', results)

            expandf = bre.compile_replace(pattern, br'\C\U00000109\n\x77\E\l\x57\c\U00000109', bre.FORMAT)
            results = expandf(pattern.match(b'Test'))
            self.assertEqual(b'\U00000109\nWw\U00000109', results)

        # Format doesn't care about groups
        pattern = re.compile('Test')
        expand = bre.compile_replace(pattern, r'\127\666\C\167\666\n\E\l\127\c\666', bre.FORMAT)
        results = expand(pattern.match('Test'))
        self.assertEqual('W\u01b6W\u01b5\nw\u01b5', results)

        pattern = re.compile(b'Test')
        expandf = bre.compile_replace(pattern, br'\127\C\167\n\E\l\127', bre.FORMAT)
        results = expandf(pattern.match(b'Test'))
        self.assertEqual(b'WW\nw', results)

        # Octal behavior in regex grabs \127 before it evaluates \27, so we must match that behavior
        pattern = re.compile('Test')
        expand = bre.compile_replace(pattern, r'\127\666\C\167\666\n\E\l\127\c\666')
        results = expand(pattern.match('Test'))
        self.assertEqual('W\u01b6W\u01b5\nw\u01b5', results)

        pattern = re.compile(b'Test')
        expandf = bre.compile_replace(pattern, br'\127\C\167\n\E\l\127')
        results = expandf(pattern.match(b'Test'))
        self.assertEqual(b'WW\nw', results)

        # Null should pass through
        pattern = re.compile('Test')
        expand = bre.compile_replace(pattern, r'\0\00\000')
        results = expand(pattern.match('Test'))
        self.assertEqual('\x00\x00\x00', results)

        pattern = re.compile(b'Test')
        expand = bre.compile_replace(pattern, br'\0\00\000')
        results = expand(pattern.match(b'Test'))
        self.assertEqual(b'\x00\x00\x00', results)

        pattern = re.compile('Test')
        expand = bre.compile_replace(pattern, r'\0\00\000', bre.FORMAT)
        results = expand(pattern.match('Test'))
        self.assertEqual('\x00\x00\x00', results)

        pattern = re.compile(b'Test')
        expand = bre.compile_replace(pattern, br'\0\00\000', bre.FORMAT)
        results = expand(pattern.match(b'Test'))
        self.assertEqual(b'\x00\x00\x00', results)


class TestExceptions(unittest.TestCase):
    """Test Exceptions."""

    # def test_incomplete_replace_narrow_unicode(self):
    #     """Test incomplete replace of narrow Unicode."""

    #     p = bre.compile_search(r'test')
    #     with self.assertRaises(SyntaxError) as e:
    #         bre.compile_replace(p, r'Replace \u fail!')
    #     self.assertTrue(str(e), 'Format for Unicode is \\uXXXX!')

    # def test_incomplete_replace_wide_unicode(self):
    #     """Test incomplete replace wide Unicode."""

    #     p = bre.compile_search(r'test')
    #     with self.assertRaises(SyntaxError) as e:
    #         bre.compile_replace(p, r'Replace \U fail!')
    #     self.assertTrue(str(e), 'Format for wide Unicode is \\UXXXXXXXX!')

    def test_not_posix_at_end_group(self):
        """Test a situation that is not a POSIX at the end of a group."""

        with pytest.raises(sre_constants.error) as excinfo:
            bre.compile_search(r'Test [[:graph:]')
        self.assertTrue(excinfo is not None)

    def test_incomplete_replace_unicode_name(self):
        """Test incomplete replace with Unicode name."""

        p = bre.compile_search(r'test')
        with pytest.raises(SyntaxError) as e:
            bre.compile_replace(p, r'Replace \N fail!')
        self.assertEqual(str(e.value), 'Format for Unicode name is \\N{name}!')

    def test_incomplete_replace_group(self):
        """Test incomplete replace group."""

        p = bre.compile_search(r'test')
        with pytest.raises(SyntaxError) as e:
            bre.compile_replace(p, r'Replace \g fail!')
        self.assertEqual(str(e.value), 'Format for group is \\g<group_name_or_index>!')

    def test_incomplete_replace_byte(self):
        """Test incomplete byte group."""

        p = bre.compile_search(r'test')
        with pytest.raises(SyntaxError) as e:
            bre.compile_replace(p, r'Replace \x fail!')
        self.assertEqual(str(e.value), 'Format for byte is \\xXX!')

    def test_bad_posix(self):
        """Test bad posix."""

        with pytest.raises(ValueError) as e:
            bre.compile_search(r'[[:bad:]]', re.UNICODE)

        self.assertEqual(str(e.value), 'Invalid POSIX property!')

    def test_bad_binary(self):
        """Test bad binary."""

        with pytest.raises(ValueError) as e:
            bre.compile_search(r'\p{bad_binary:n}', re.UNICODE)

        self.assertEqual(str(e.value), 'Invalid Unicode property!')

        with pytest.raises(ValueError) as e:
            bre.compile_search(r'\p{bad_binary:y}', re.UNICODE)

        self.assertEqual(str(e.value), 'Invalid Unicode property!')

    def test_bad_category(self):
        """Test bad category."""

        with pytest.raises(ValueError) as e:
            bre.compile_search(r'\p{alphanumeric: bad}', re.UNICODE)

        self.assertEqual(str(e.value), 'Invalid Unicode property!')

    def test_bad_short_category(self):
        """Test bad category."""

        with pytest.raises(ValueError) as e:
            bre.compile_search(r'\pQ', re.UNICODE)

        self.assertEqual(str(e.value), 'Invalid Unicode property!')

    def test_incomplete_inverse_category(self):
        """Test incomplete inverse category."""

        with pytest.raises(SyntaxError) as e:
            bre.compile_search(r'\p', re.UNICODE)

        self.assertEqual(str(e.value), 'Format for Unicode property is \\p{property} or \\pP!')

    def test_incomplete_category(self):
        """Test incomplete category."""

        with pytest.raises(SyntaxError) as e:
            bre.compile_search(r'\P', re.UNICODE)

        self.assertEqual(str(e.value), 'Format for inverse Unicode property is \\P{property} or \\PP!')

    def test_incomplete_unicode_name(self):
        """Test incomplete Unicode name."""

        with pytest.raises(SyntaxError) as e:
            bre.compile_search(r'\N', re.UNICODE)

        self.assertEqual(str(e.value), 'Format for Unicode name is \\N{name}!')

    def test_bad_left_format_bracket(self):
        """Test bad left format bracket."""

        text_pattern = r"(Bad )(format)!"
        pattern = re.compile(text_pattern)

        with pytest.raises(ValueError) as excinfo:
            bre.compile_replace(pattern, r'Bad format { test', bre.FORMAT)

        assert "Single unmatched curly bracket!" in str(excinfo.value)

    def test_bad_right_format_bracket(self):
        """Test bad right format bracket."""

        text_pattern = r"(Bad )(format)!"
        pattern = re.compile(text_pattern)

        with pytest.raises(ValueError) as excinfo:
            bre.compile_replace(pattern, r'Bad format } test', bre.FORMAT)

        assert "Single unmatched curly bracket!" in str(excinfo.value)

    def test_switch_from_format_auto(self):
        """Test a switch from auto to manual format."""

        text_pattern = r"(this )(.+?)(format capture )(groups)(!)"
        pattern = re.compile(text_pattern)

        with pytest.raises(ValueError) as excinfo:
            bre.compile_replace(
                pattern, r'{}{}{manual}', bre.FORMAT
            )

        assert "Cannot switch to manual format during auto format!" in str(excinfo.value)

    def test_switch_from_format_manual(self):
        """Test a switch from manual to auto format."""

        text_pattern = r"(this )(.+?)(format capture )(groups)(!)"
        pattern = re.compile(text_pattern)

        with pytest.raises(ValueError) as excinfo:
            bre.compile_replace(
                pattern, r'{manual}{}{}', bre.FORMAT
            )

        assert "Cannot switch to auto format during manual format!" in str(excinfo.value)

    def test_format_bad_capture(self):
        """Test a bad capture."""

        text_pattern = r"(\w)+"
        pattern = re.compile(text_pattern)

        with pytest.raises(ValueError) as excinfo:
            bre.compile_replace(
                pattern, r'{1[0o3f]}', bre.FORMAT
            )

        assert "Capture index must be an integer!" in str(excinfo.value)

    def test_format_bad_capture_range(self):
        """Test a bad capture."""

        text_pattern = r"(\w)+"
        pattern = re.compile(text_pattern)
        expand = bre.compile_replace(
            pattern, r'{1[37]}', bre.FORMAT
        )

        with pytest.raises(IndexError) as excinfo:
            expand(pattern.match('text'))

        assert "is out of range!" in str(excinfo.value)

    def test_require_compiled_pattern(self):
        """Test a bad capture."""

        with pytest.raises(TypeError) as excinfo:
            bre.compile_replace(
                r'\w+', r'\1'
            )

        assert "Pattern must be a compiled regular expression!" in str(excinfo.value)

    def test_none_match(self):
        """Test None match."""

        pattern = re.compile("test")
        expand = bre.compile_replace(pattern, "replace")
        m = pattern.match('wrong')

        with pytest.raises(ValueError) as excinfo:
            expand(m)

        assert "Match is None!" in str(excinfo.value)

    def test_search_flag_on_compiled(self):
        """Test when a compile occurs on a compiled object with flags passed."""

        pattern = bre.compile_search("test")

        with pytest.raises(ValueError) as excinfo:
            pattern = bre.compile_search(pattern, bre.I)

        assert "Cannot process flags argument with a compiled pattern!" in str(excinfo.value)

    def test_bad_value_search(self):
        """Test when the search value is bad."""

        with pytest.raises(TypeError) as excinfo:
            bre.compile_search(None)

        assert "Not a string or compiled pattern!" in str(excinfo.value)

    def test_relace_flag_on_compiled(self):
        """Test when a compile occurs on a compiled object with flags passed."""

        pattern = re.compile('test')
        replace = bre.compile_replace(pattern, "whatever")

        with pytest.raises(ValueError) as excinfo:
            replace = bre.compile_replace(pattern, replace, bre.FORMAT)

        assert "Cannot process flags argument with a compiled pattern!" in str(excinfo.value)

    def test_relace_flag_on_template(self):
        """Test when a compile occurs on a template with flags passed."""

        pattern = re.compile('test')
        template = bre.ReplaceTemplate(pattern, 'whatever')

        with pytest.raises(ValueError) as excinfo:
            bre.compile_replace(pattern, template, bre.FORMAT)

        assert "Cannot process flags argument with a ReplaceTemplate!" in str(excinfo.value)

    def test_bad_pattern_in_replace(self):
        """Test when a bad pattern is passed into replace."""

        with pytest.raises(TypeError) as excinfo:
            bre.compile_replace(None, "whatever", bre.FORMAT)

        assert "Pattern must be a compiled regular expression!" in str(excinfo.value)

    def test_bad_hash(self):
        """Test when pattern hashes don't match."""

        pattern = re.compile('test')
        replace = bre.compile_replace(pattern, 'whatever')
        pattern2 = re.compile('test', re.I)

        with pytest.raises(ValueError) as excinfo:
            bre.compile_replace(pattern2, replace)

        assert "Pattern hash doesn't match hash in compiled replace!" in str(excinfo.value)

    def test_sub_wrong_replace_type(self):
        """Test sending wrong type into `sub`, `subn`."""

        pattern = re.compile('test')
        replace = bre.compile_replace(pattern, 'whatever', bre.FORMAT)

        with pytest.raises(ValueError) as excinfo:
            bre.sub(pattern, replace, 'test')

        assert "Compiled replace cannot be a format object!" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            bre.subn(pattern, replace, 'test')

        assert "Compiled replace cannot be a format object!" in str(excinfo.value)

    def test_sub_wrong_replace_format_type(self):
        """Test sending wrong format type into `sub`, `subn`."""

        pattern = re.compile('test')
        replace = bre.compile_replace(pattern, 'whatever')

        with pytest.raises(ValueError) as excinfo:
            bre.subf(pattern, replace, 'test')

        assert "Compiled replace is not a format object!" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            bre.subfn(pattern, replace, 'test')

        assert "Compiled replace is not a format object!" in str(excinfo.value)

    def test_expand_wrong_values(self):
        """Test expand with wrong values."""

        pattern = re.compile('test')
        replace = bre.compile_replace(pattern, 'whatever', bre.FORMAT)
        m = pattern.match('test')

        with pytest.raises(ValueError) as excinfo:
            bre.expand(m, replace)

        assert "Replace should not be compiled as a format replace!" in str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            bre.expand(m, 0)

        assert "Expected string, buffer, or compiled replace!" in str(excinfo.value)

    def test_expandf_wrong_values(self):
        """Test expand with wrong values."""

        pattern = re.compile('test')
        replace = bre.compile_replace(pattern, 'whatever')
        m = pattern.match('test')

        with pytest.raises(ValueError) as excinfo:
            bre.expandf(m, replace)

        assert "Replace not compiled as a format replace" in str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            bre.expandf(m, 0)

        assert "Expected string, buffer, or compiled replace!" in str(excinfo.value)

    def test_compile_with_function(self):
        """Test that a normal function cannot compile."""

        def repl(m):
            """Replacement function."""

            return "whatever"

        pattern = re.compile('test')

        with pytest.raises(TypeError) as excinfo:
            bre.compile_replace(pattern, repl)

        assert "Not a valid type!" in str(excinfo.value)

    def test_octal_fail(self):
        """Test that octal fails properly."""

        pattern = re.compile(b'Test')

        with pytest.raises(ValueError) as excinfo:
            bre.compile_replace(pattern, br'\666')

        assert "octal escape value outside of range 0-0o377!" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            bre.compile_replace(pattern, br'\C\666\E')

        assert "octal escape value outside of range 0-0o377!" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            bre.compile_replace(pattern, br'\c\666')

        assert "octal escape value outside of range 0-0o377!" in str(excinfo.value)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    def test_match(self):
        """Test that `match` works."""

        m = bre.match(r'This is a test for m[\l]+!', "This is a test for match!")
        self.assertTrue(m is not None)

    def test_search(self):
        """Test that `search` works."""

        m = bre.search(r'test', "This is a test for search!")
        self.assertTrue(m is not None)

    def test_split(self):
        """Test that `split` works."""

        self.assertEqual(
            bre.split(r'\W+', "This is a test for split!"),
            ["This", "is", "a", "test", "for", "split", ""]
        )

    def test_sub(self):
        """Test that `sub` works."""

        self.assertEqual(
            bre.sub(r'tset', 'test', r'This is a tset for sub!'),
            "This is a test for sub!"
        )

    def test_compiled_sub(self):
        """Test that compiled search and replace works."""

        pattern = bre.compile_search(r'tset')
        replace = bre.compile_replace(pattern, 'test')

        self.assertEqual(
            bre.sub(pattern, replace, 'This is a tset for sub!'),
            "This is a test for sub!"
        )

    def test_subn(self):
        """Test that `subn` works."""

        self.assertEqual(
            bre.subn(r'tset', 'test', r'This is a tset for subn! This is a tset for subn!'),
            ('This is a test for subn! This is a test for subn!', 2)
        )

    def test_subf(self):
        """Test that `subf` works."""

        self.assertEqual(
            bre.subf(r'(t)(s)(e)(t)', '{1}{3}{2}{4}', r'This is a tset for subf!'),
            "This is a test for subf!"
        )

    def test_subfn(self):
        """Test that `subfn` works."""

        self.assertEqual(
            bre.subfn(r'(t)(s)(e)(t)', '{1}{3}{2}{4}', r'This is a tset for subfn! This is a tset for subfn!'),
            ('This is a test for subfn! This is a test for subfn!', 2)
        )

    def test_findall(self):
        """Test that `findall` works."""

        self.assertEqual(
            bre.findall(r'\w+', 'This is a test for findall!'),
            ["This", "is", "a", "test", "for", "findall"]
        )

    def test_finditer(self):
        """Test that `finditer` works."""

        count = 0
        for m in bre.finditer(r'\w+', 'This is a test for finditer!'):
            count += 1

        self.assertEqual(count, 6)

    def test_expand(self):
        """Test that `expand` works."""

        pattern = bre.compile_search(r'(This is a test for )(m[\l]+!)')
        m = bre.match(pattern, "This is a test for match!")
        self.assertEqual(
            bre.expand(m, r'\1\C\2\E'),
            'This is a test for MATCH!'
        )

        replace = bre.compile_replace(pattern, r'\1\C\2\E')
        self.assertEqual(
            bre.expand(m, replace),
            'This is a test for MATCH!'
        )

    def test_expandf(self):
        """Test that `expandf` works."""

        pattern = bre.compile_search(r'(This is a test for )(match!)')
        m = bre.match(pattern, "This is a test for match!")
        self.assertEqual(
            bre.expandf(m, r'{1}\C{2}\E'),
            'This is a test for MATCH!'
        )

        replace = bre.compile_replace(pattern, r'{1}\C{2}\E', bre.FORMAT)
        self.assertEqual(
            bre.expandf(m, replace),
            'This is a test for MATCH!'
        )
