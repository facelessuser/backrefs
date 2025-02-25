# -*- coding: utf-8 -*-
"""Test `bre` lib."""
import unittest
from backrefs import bre
import re
import sys
import pytest
import random
from backrefs import _bre_parse
import copy

PY39_PLUS = (3, 9) <= sys.version_info
PY311_PLUS = (3, 11) <= sys.version_info

if PY311_PLUS:
    import re._constants as _constants
else:
    import sre_constants as _constants


class TestSearchTemplate(unittest.TestCase):
    """Search template tests."""

    def test_custom_binary_properties(self):
        """Test new custom binary properties."""

        self.assertEqual(
            bool(
                bre.fullmatch(
                    r'\p{HorizSpace}+',
                    '\t \xA0\u1680\u180E\u2000\u2001\u2002\u2003\u2004'
                    '\u2005\u2006\u2007\u2008\u2009\u200A\u202F\u205F\u3000'
                )
            ),
            True
        )
        self.assertEqual(bool(bre.fullmatch(r'\p{VertSpace}+', '\n\v\f\r\x85\u2028\u2029')), True)

    def test_posix_unicode_and_range(self):
        """POSIX and Unicode classes should not be part of a range."""

        self.assertTrue(bre.match(r'[[:upper:]-[:digit:]]', '-') is not None)
        self.assertTrue(bre.match(r'[[:upper:]-[:digit:]]', 'Z') is not None)
        self.assertTrue(bre.match(r'[[:upper:]-[:digit:]]', '0') is not None)
        self.assertTrue(bre.match(r'[[:upper:]-[:digit:]]', '5') is not None)

        self.assertTrue(bre.match(r'[[:digit:]-[:upper:]]', 'A') is not None)
        self.assertTrue(bre.match(r'[[:digit:]-[:upper:]]', '9') is not None)
        self.assertTrue(bre.match(r'[[:digit:]-[:upper:]]', '-') is not None)
        self.assertTrue(bre.match(r'[[:digit:]-[:upper:]]', 'D') is not None)

        self.assertTrue(bre.match(r'[0-[:upper:]]', '-') is not None)
        self.assertTrue(bre.match(r'[0-[:upper:]]', '0') is not None)
        self.assertTrue(bre.match(r'[0-[:upper:]]', 'A') is not None)
        self.assertTrue(bre.match(r'[0-[:upper:]]', 'D') is not None)

        self.assertTrue(bre.match(r'[[:digit:]-Z]', 'Z') is not None)
        self.assertTrue(bre.match(r'[[:digit:]-Z]', '9') is not None)
        self.assertTrue(bre.match(r'[[:digit:]-Z]', '-') is not None)
        self.assertTrue(bre.match(r'[[:digit:]-Z]', '5') is not None)

        self.assertTrue(bre.match(r'[\p{digit}-Z]', 'Z') is not None)
        self.assertTrue(bre.match(r'[\p{digit}-Z]', '9') is not None)
        self.assertTrue(bre.match(r'[\p{digit}-Z]', '-') is not None)
        self.assertTrue(bre.match(r'[\p{digit}-Z]', '5') is not None)

        self.assertTrue(bre.match(r'[0-\p{upper}]', '-') is not None)
        self.assertTrue(bre.match(r'[0-\p{upper}]', '0') is not None)
        self.assertTrue(bre.match(r'[0-\p{upper}]', 'A') is not None)
        self.assertTrue(bre.match(r'[0-\p{upper}]', 'D') is not None)

        self.assertTrue(bre.match(r'[\p{HorizSpace}-Z]', 'Z') is not None)
        self.assertTrue(bre.match(r'[\p{HorizSpace}-Z]', '\x20') is not None)
        self.assertTrue(bre.match(r'[\p{HorizSpace}-Z]', '-') is not None)

    def test_non_raw_string_unicode(self):
        """Test non raw string Unicode notation."""

        self.assertTrue(bre.compile('\\u0070\\U00000070').match('pp') is not None)
        self.assertTrue(bre.compile('\\Q\\u0070\\U00000070\\E').match('\\u0070\\U00000070') is not None)

    def test_compile_attributes(self):
        """Test compile attributes."""

        p = bre.compile('(?x)test')
        self.assertEqual(p.pattern, p._pattern.pattern)
        self.assertEqual(p.flags, p._pattern.flags)
        self.assertEqual(p.groups, p._pattern.groups)
        self.assertEqual(p.groupindex, p._pattern.groupindex)
        self.assertEqual(p.scanner, p._pattern.scanner)

    def test_compile_passthrough(self):
        """Test conditions where a compile object passes through functions."""

        p = bre.compile('test')
        self.assertTrue(p == bre.compile(p))
        with pytest.raises(ValueError):
            bre.compile(p, bre.X)
        with pytest.raises(ValueError):
            bre.compile(p, auto_compile=False)
        with pytest.raises(ValueError):
            bre.compile_search(p, bre.X)
        self.assertEqual(bre.sub(p, 'success', 'test'), 'success')

    def test_hash(self):
        """Test hashing of search."""

        p1 = bre.compile('test')
        p2 = bre.compile('test')
        p3 = bre.compile('test', bre.X)
        p4 = bre.compile(b'test')

        self.assertTrue(p1 == p2)
        self.assertTrue(p1 != p3)
        self.assertTrue(p1 != p4)

        p5 = copy.copy(p1)
        self.assertTrue(p1 == p5)
        self.assertTrue(p5 in {p1})

    def test_not_flags(self):
        """Test invalid flags."""

        with pytest.raises(_constants.error):
            bre.compile(r'(?-q:test)')

    def test_comment_failures(self):
        """Test comment failures."""

        with pytest.raises(SyntaxError):
            bre.compile(r'test(?#test')

    def test_inverse_posix_property(self):
        """Test inverse POSIX property."""

        self.assertTrue(bre.compile(r'[[:^xdigit:]]').match('i') is not None)

    def test_posix_property_bad_syntax(self):
        """Test that we ignore an incomplete POSIX syntax."""

        with pytest.warns(FutureWarning):
            self.assertTrue(bre.compile(r'[[:a]]').match('a]') is not None)
        with pytest.warns(FutureWarning):
            self.assertTrue(bre.compile(r'[[:a]').match('a') is not None)
        with pytest.warns(FutureWarning):
            self.assertTrue(bre.compile(r'[[:graph:a]').match('a') is not None)

    def test_unicode_property_failures(self):
        """Test Unicode property."""

        with pytest.raises(SyntaxError):
            bre.compile(r'\p')

        with pytest.raises(SyntaxError):
            bre.compile(r'\p.')

        with pytest.raises(SyntaxError):
            bre.compile(r'\p{')

        with pytest.raises(SyntaxError):
            bre.compile(r'\p{A.')

        with pytest.raises(SyntaxError):
            bre.compile(r'\p{A')

        with pytest.raises(SyntaxError):
            bre.compile(r'\p{a:}')

        with pytest.raises(SyntaxError):
            bre.compile(r'\p{a:.')

    def test_named_unicode_failures(self):
        """Test named Unicode failures."""

        with pytest.raises(SyntaxError):
            bre.compile(r'\N')

        with pytest.raises(SyntaxError):
            bre.compile(r'\Na')

        with pytest.raises(SyntaxError):
            bre.compile(r'\N{A.')

        with pytest.raises(SyntaxError):
            bre.compile(r'\N{A')

    def test_word_boundary(self):
        """Test word boundary."""

        pattern = bre.compile_search(r'\mtest')
        self.assertEqual(
            pattern.pattern,
            r"\b(?=\w)test"
        )
        pattern = bre.compile_search(r'test\M')
        self.assertEqual(
            pattern.pattern,
            r"test\b(?<=\w)"
        )

        with pytest.raises(_constants.error):
            bre.compile_search(r'[\m]test')

    def test_cache(self):
        """Test cache."""

        bre.purge()
        self.assertEqual(bre._get_cache_size(), 0)
        self.assertEqual(bre._get_cache_size(True), 0)
        for _ in range(1000):
            value = str(random.randint(1, 10000))
            p = bre.compile(value)
            p.sub('', value)
            self.assertTrue(bre._get_cache_size() > 0)
            self.assertTrue(bre._get_cache_size() > 0)
        self.assertTrue(bre._get_cache_size() == 500)
        self.assertTrue(bre._get_cache_size(True) == 500)
        bre.purge()
        self.assertEqual(bre._get_cache_size(), 0)
        self.assertEqual(bre._get_cache_size(True), 0)
        self.assertEqual(len(re._cache), 0)

    def test_infinite_loop_catch(self):
        """Test infinite loop catch."""

        with pytest.raises(_bre_parse.LoopException):
            bre.compile_search(r'((?a)(?u))')

        with pytest.raises(_bre_parse.LoopException):
            bre.compile_search(r'(?-x:(?x))', re.VERBOSE)

    def test_unicode_ascii_swap(self):
        """Test Unicode ASCII swapping."""

        pattern = bre.compile_search(r'(?u:\w{2})(?a:\w{2})(?u:\w{2})')
        self.assertTrue(pattern.match('ÀÀAAÀÀ') is not None)
        self.assertTrue(pattern.match('ÀÀAÀÀÀ') is None)
        self.assertTrue(pattern.match('ÀÀÀAÀÀ') is None)

    def test_comments_with_scoped_verbose(self):
        """Test scoped verbose with comments (Python 3.6+)."""

        pattern = bre.compile_search(
            r'''(?u)Test # \R(?#\R)(?x:
            Test #\R(?#\R)
            (Test # \R
            )Test #\R
            )Test # \R'''
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?u)Test # (?:\r\n|(?!\r\n)[\n\v\f\r\x85\u2028\u2029])(?#\R)(?x:
            Test #\\R(?#\\R)
            (Test # \\R
            )Test #\\R
            )Test # (?:\r\n|(?!\r\n)[\n\v\f\r\x85\u2028\u2029])'''
        )

        self.assertTrue(pattern.match('Test # \nTestTestTestTest # \r\n') is not None)

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

        with pytest.warns(DeprecationWarning):
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
            Test \p{PosixXDigit}
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

        with pytest.raises(_constants.error):
            pattern = bre.compile_search('test\\', re.UNICODE)

        with pytest.raises(_constants.error):
            pattern = bre.compile_search('test[\\', re.UNICODE)

        with pytest.raises(_constants.error):
            pattern = bre.compile_search('test(\\', re.UNICODE)

        pattern = bre.compile_search('\\Qtest\\', re.UNICODE)
        self.assertEqual(pattern.pattern, 'test\\\\')

    def test_escape_values_in_verbose_comments(self):
        """Test added escapes in verbose comments."""

        pattern = bre.compile_search(r'(?x)test # \l \p{numbers}', re.UNICODE)
        self.assertEqual(pattern.pattern, r'(?x)test # \\l \\p{numbers}', re.UNICODE)

    def test_char_group_nested_opening(self):
        """Test char group with nested opening [."""

        with pytest.warns(FutureWarning):
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

        pattern = bre.compile_search(r'Test [[:graph:]]', re.ASCII)
        pattern2 = bre.compile_search('Test [!-\\~]', re.ASCII)
        self.assertEqual(pattern.pattern, pattern2.pattern)

    def test_not_posix_at_start_group(self):
        """Test a situation that is not a POSIX at the start of a group."""

        pattern = bre.compile_search(r'Test [:graph:]]')
        self.assertEqual(pattern.pattern, r'Test [:graph:]]')

    def test_unrecognized_backrefs(self):
        """Test unrecognized backrefs."""

        result = _bre_parse._SearchParser(r'Testing unrecognized backrefs \k!').parse()
        self.assertEqual(r'Testing unrecognized backrefs \k!', result)

    def test_quote(self):
        """Test quoting/escaping."""

        result = _bre_parse._SearchParser(r'Testing \Q(\s+[quote]*\s+)?\E!').parse()
        self.assertEqual(r'Testing %s!' % re.escape(r'(\s+[quote]*\s+)?'), result)

    def test_normal_backrefs(self):
        """
        Test normal builtin backrefs.

        They should all pass through unaltered.
        """

        result = _bre_parse._SearchParser(r'\a\b\f\n\r\t\v\A\b\B\d\D\s\S\w\W\Z\\[\b]').parse()
        self.assertEqual(r'\a\b\f\n\r\t\v\A\b\B\d\D\s\S\w\W\Z\\[\b]', result)

    def test_quote_no_end(self):
        r"""Test quote where no `\E` is defined."""

        result = _bre_parse._SearchParser(r'Testing \Q(quote) with no [end]!').parse()
        self.assertEqual(r'Testing %s' % re.escape(r'(quote) with no [end]!'), result)

    def test_quote_in_char_groups(self):
        """Test that quote backrefs are handled in character groups."""

        result = _bre_parse._SearchParser(r'Testing [\Qchar\E block] [\Q(AVOIDANCE)\E]!').parse()
        self.assertEqual(r'Testing [char block] [\(AVOIDANCE\)]!', result)

    def test_quote_in_char_groups_with_right_square_bracket_first(self):
        """Test that quote backrefs are handled in character groups that have a right square bracket as first char."""

        result = _bre_parse._SearchParser(r'Testing [^]\Qchar\E block] []\Q(AVOIDANCE)\E]!').parse()
        self.assertEqual(r'Testing [^]char block] []\(AVOIDANCE\)]!', result)

    def test_extraneous_end_char(self):
        r"""Test that stray '\E's get removed."""

        result = _bre_parse._SearchParser(r'Testing \Eextraneous end char\E!').parse()
        self.assertEqual(r'Testing extraneous end char!', result)

    def test_escaped_backrefs(self):
        """Ensure escaped backrefs don't get processed."""

        result = _bre_parse._SearchParser(r'\\cTesting\\C \\lescaped\\L \\Qbackrefs\\E!').parse()
        self.assertEqual(r'\\cTesting\\C \\lescaped\\L \\Qbackrefs\\E!', result)

    def test_escaped_escaped_backrefs(self):
        """Ensure escaping escaped backrefs do get processed."""

        result = _bre_parse._SearchParser(r'Testing escaped escaped \\\Qbackrefs\\\E!').parse()
        self.assertEqual(r'Testing escaped escaped \\backrefs\\\\!', result)

    def test_escaped_escaped_escaped_backrefs(self):
        """Ensure escaping escaped escaped backrefs don't get processed."""

        result = _bre_parse._SearchParser(r'Testing escaped escaped \\\\Qbackrefs\\\\E!').parse()
        self.assertEqual(r'Testing escaped escaped \\\\Qbackrefs\\\\E!', result)

    def test_escaped_escaped_escaped_escaped_backrefs(self):
        """
        Ensure escaping escaped escaped escaped backrefs do get processed.

        This is far enough to prove out that we are handling them well enough.
        """

        result = _bre_parse._SearchParser(r'Testing escaped escaped \\\\\Qbackrefs\\\\\E!').parse()
        self.assertEqual(r'Testing escaped escaped \\\\backrefs\\\\\\\\!', result)

    def test_normal_escaping(self):
        """Normal escaping should be unaltered."""

        result = _bre_parse._SearchParser(r'\n \\n \\\n \\\\n \\\\\n').parse()
        self.assertEqual(r'\n \\n \\\n \\\\n \\\\\n', result)

    def test_normal_escaping2(self):
        """Normal escaping should be unaltered part2."""

        result = _bre_parse._SearchParser(r'\y \\y \\\y \\\\y \\\\\y').parse()
        self.assertEqual(r'\y \\y \\\y \\\\y \\\\\y', result)

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

    def test_unicode_properties_inverse_value_inverse(self):
        """Exercising inverse Unicode properties that are using inverse values."""

        pattern = bre.compile_search(r'\P{^Po}', re.UNICODE)
        m = pattern.match(r'·')
        self.assertTrue(m is not None)
        m = pattern.match(r'P')
        self.assertTrue(m is None)

    def test_negated_unicode_properties_inverse(self):
        """Exercising negated inverse Unicode properties."""

        pattern = bre.compile_search(r'[^\P{Po}]', re.UNICODE)
        m = pattern.match(r'·')
        self.assertTrue(m is not None)
        m = pattern.match(r'P')
        self.assertTrue(m is None)

    def test_bytes_property(self):
        r"""Byte patterns should match `\p` references."""

        pattern = bre.compile_search(br'EX\p{Lu}MPLE')
        m = pattern.match(br'EXAMPLE')
        self.assertTrue(m is not None)

    def test_bytes_property_no_value(self):
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

        template = _bre_parse._SearchParser(
            r'''
            This is a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [#\ ] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ a # \Qcomment\E (?x)
            '''
        )
        template.parse()

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

        template = _bre_parse._SearchParser(r'Testing for (?ia) ASCII flag.', False, None)
        template.parse()
        self.assertFalse(template.unicode)

    def test_unicode_string_flag_in_group(self):
        """Test ignoring Unicode/ASCII string flag in group."""

        template = _bre_parse._SearchParser(r'Testing for [(?ia)] ASCII flag.', False, None)
        template.parse()
        self.assertTrue(template.unicode)

    def test_unicode_string_flag_escaped(self):
        """Test ignoring Unicode/ASCII string flag in group."""

        template = _bre_parse._SearchParser(r'Testing for \(?ia) ASCII flag.', False, None)
        template.parse()
        self.assertTrue(template.unicode)

    def test_unicode_string_flag_unescaped(self):
        """Test unescaped Unicode string flag."""

        template = _bre_parse._SearchParser(r'Testing for \\(?ia) ASCII flag.', False, None)
        template.parse()
        self.assertFalse(template.unicode)

    def test_unicode_string_flag_escaped_deep(self):
        """Test deep escaped Unicode flag."""

        template = _bre_parse._SearchParser(r'Testing for \\\(?ia) ASCII flag.', False, None)
        template.parse()
        self.assertTrue(template.unicode)

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

    @unittest.skipUnless(PY39_PLUS, "Python 3.9 required")
    def test_emoji_property(self):
        """Test new emoji properties."""

        self.assertEqual(len(bre.findall(r'\p{emoji}', '\U0001F600 test \U0001F600')), 2)


class TestReplaceTemplate(unittest.TestCase):
    """Test replace template."""

    def test_format_existing_group_no_match(self):
        """Test format replacement with existing group with no match."""

        self.assertEqual(bre.compile(r'(test)|(what)').subf(R'{1}{2}', 'test'), 'test')

    def test_existing_group_no_match(self):
        """Test existing group with no match."""

        self.assertEqual(bre.compile(r'(test)|(what)').sub(r'\2', 'test'), '')

    def test_hash(self):
        """Test hashing of replace."""

        p1 = bre.compile('(test)')
        p2 = bre.compile('(test)')
        p3 = bre.compile(b'(test)')
        r1 = p1.compile(r'\1')
        r2 = p1.compile(r'\1')
        r3 = p2.compile(r'\1')
        r4 = p2.compile(r'\1', bre.FORMAT)
        r5 = p3.compile(br'\1')

        self.assertTrue(r1 == r2)
        self.assertTrue(r2 == r3)
        self.assertTrue(r1 != r4)
        self.assertTrue(r1 != r5)

        r6 = copy.copy(r1)
        self.assertTrue(r1 == r6)
        self.assertTrue(r6 in {r1})

    def test_format_failures(self):
        """Test format parsing failures."""

        with pytest.raises(_constants.error):
            bre.subf('test', r'{1.}', 'test', bre.FORMAT)

        with pytest.raises(IndexError):
            bre.subf('test', r'{a.}', 'test', bre.FORMAT)

        with pytest.raises(SyntaxError):
            bre.subf('test', r'{1[}', 'test', bre.FORMAT)

        with pytest.raises(SyntaxError):
            bre.subf('test', r'{a[}', 'test', bre.FORMAT)

        with pytest.raises(SyntaxError):
            bre.subf('test', r'test } test', 'test', bre.FORMAT)

        with pytest.raises(SyntaxError):
            bre.subf('test', r'test {test', 'test', bre.FORMAT)

        with pytest.raises(SyntaxError):
            bre.subf('test', r'test { test', 'test', bre.FORMAT)

        with pytest.raises(_constants.error):
            bre.subf(b'test', br'{1.}', b'test', bre.FORMAT)

        with pytest.raises(IndexError):
            bre.subf(b'test', br'{a.}', b'test', bre.FORMAT)

        with pytest.raises(SyntaxError):
            bre.subf(b'test', br'{1[}', b'test', bre.FORMAT)

        with pytest.raises(SyntaxError):
            bre.subf(b'test', br'{a[}', b'test', bre.FORMAT)

        with pytest.raises(SyntaxError):
            bre.subf(b'test', br'test } test', b'test', bre.FORMAT)

        with pytest.raises(SyntaxError):
            bre.subf(b'test', br'test {test', b'test', bre.FORMAT)

        with pytest.raises(SyntaxError):
            bre.subf(b'test', br'test { test', b'test', bre.FORMAT)

        with pytest.raises(TypeError):
            bre.subf(b'test', br'{[test]}', b'test', bre.FORMAT)

    def test_format_ascii_align(self):
        """Test format ASCII."""

        self.assertEqual(bre.subf('test', r'{0!a:|^8}', 'test'), "|'test'|")

    def test_format_conversions(self):
        """Test string format conversion paths."""

        self.assertTrue(bre.subf('test', r'{0.index}', 'test').startswith(('<built-in method', '<bound method')))
        self.assertEqual(bre.subf('test', r'{0.__class__.__name__}', 'test'), 'str')
        self.assertTrue(bre.subf('test', r'{0.index!s}', 'test').startswith(('<built-in method', '<bound method')))
        self.assertEqual(bre.subf('test', r'{0.__class__.__name__!s}', 'test'), 'str')
        self.assertTrue(bre.subf('test', r'{0.index!a}', 'test').startswith(('<built-in method', '<bound method')))

        self.assertTrue(bre.subf(b'test', br'{0.index}', b'test').startswith((b'<built-in method', b'<bound method')))
        self.assertEqual(bre.subf(b'test', br'{0.__class__.__name__}', b'test'), b'bytes')
        self.assertTrue(bre.subf(b'test', br'{0.index!s}', b'test').startswith((b'<built-in method', b'<bound method')))
        self.assertEqual(bre.subf(b'test', br'{0.__class__.__name__!s}', b'test'), b'bytes')
        self.assertTrue(bre.subf('test', r'{0.index!a}', 'test').startswith(('<built-in method', '<bound method')))

    def test_incompatible_strings(self):
        """Test incompatible string types."""

        with pytest.raises(TypeError):
            bre.compile('test').compile(b'test')

        p1 = bre.compile('test')
        repl = bre.compile(b'test').compile(b'other')
        m = p1.match('test')
        with pytest.raises(TypeError):
            repl(m)

    def test_named_unicode_failures(self):
        """Test named Unicode failures."""

        with pytest.raises(SyntaxError):
            bre.sub('test', r'\N', 'test')

        with pytest.raises(SyntaxError):
            bre.sub('test', r'\Na', 'test')

        with pytest.raises(SyntaxError):
            bre.sub('test', r'\N{A.', 'test')

        with pytest.raises(SyntaxError):
            bre.sub('test', r'\N{A', 'test')

    def test_group_failures(self):
        """Test group failures."""

        with pytest.raises(SyntaxError):
            bre.sub('test', r'\g', 'test')

        with pytest.raises(SyntaxError):
            bre.sub('test', r'\ga', 'test')

        with pytest.raises(SyntaxError):
            bre.sub('test', r'\g<.', 'test')

        with pytest.raises(SyntaxError):
            bre.sub('test', r'\g<a.', 'test')

        with pytest.raises(SyntaxError):
            bre.sub('test', r'\g<3', 'test')

    def test_double_digit_group(self):
        """Test double digit group."""

        self.assertEqual(
            bre.sub('(t)(e)(s)(t)(i)(n)(g)( )(g)(r)(o)(u)(p)', r'\c\10', 'testing group'),
            'R'
        )

    def test_expand_with_none(self):
        """Test none in expand."""

        with pytest.raises(ValueError):
            bre.expand(None, "")

    def test_unicode_narrow_value(self):
        """Test Unicode narrow value."""

        pattern = re.compile(r"(some)(.+?)(pattern)(!)")
        expand = bre.compile_replace(pattern, r'\u005cg')
        results = expand(pattern.match('some test pattern!'))
        self.assertEqual(r'\g', results)

    def test_unexpected_end(self):
        """Test cases where there is an unexpected end to the replace string."""

        pattern = re.compile(r"(some)(.+?)(pattern)(!)")
        with pytest.raises(_constants.error):
            _bre_parse._ReplaceParser(pattern, '\\1\\l\\').parse()

        with pytest.raises(_constants.error):
            _bre_parse._ReplaceParser(pattern, '\\1\\L\\').parse()

        with pytest.raises(_constants.error):
            _bre_parse._ReplaceParser(pattern, '\\1\\').parse()

    def test_line_break(self):
        r"""Test line break \R."""

        self.assertEqual(
            bre.sub(r"\R", ' ', 'line\r\nline\nline\r'),
            'line line line '
        )

    def test_bytes_line_break(self):
        r"""Test bytes line break \R."""

        self.assertEqual(
            bre.sub(br"\R", b' ', b'line\r\nline\nline\r'),
            b'line line line '
        )

    def test_line_break_in_group(self):
        """Test that line break in group matches a normal R."""

        with pytest.raises(_constants.error):
            bre.sub(r"[\R]", 'l', 'Rine\r\nRine\nRine\r')

    def test_horizontal_ws(self):
        """Test horizontal whitespace."""

        with pytest.warns(DeprecationWarning):
            self.assertEqual(
                bre.sub(r'\h*', '', '    \t\ttest    \t'),
                'test'
            )

    def test_horizontal_ws_in_group(self):
        """Test horizontal whitespace."""

        with pytest.warns(DeprecationWarning):
            self.assertEqual(
                bre.sub(r'[\ht]*', '', '    \t\ttest    \t'),
                'es'
            )

    def test_horizontal_ws_in_inverse_group(self):
        """Test horizontal whitespace."""

        with pytest.warns(DeprecationWarning):
            self.assertEqual(
                bre.sub(r'[^\ht]*', '', '    \t\ttest    \t'),
                '    \t\ttt    \t'
            )

    def test_horizontal_ws_bytes(self):
        """Test horizontal whitespace as byte string."""

        with pytest.warns(DeprecationWarning):
            self.assertEqual(
                bre.sub(br'\h*', b'', b'    \t\ttest    \t'),
                b'test'
            )

    def test_grapheme_cluster(self):
        """Test simple grapheme cluster."""

        self.assertEqual(
            bre.compile(r'\X').pattern,
            bre.compile(r'(?:\PM\pM*(?!\pM))').pattern
        )

        self.assertEqual(bre.match(r"\X", "\xE0").span(), (0, 1))
        self.assertEqual(bre.match(r"\X", "a\u0300").span(), (0, 2))

        self.assertEqual(
            bre.findall(r"\X", "a\xE0a\u0300e\xE9e\u0301"),
            ['a', '\xe0', 'a\u0300', 'e', '\xe9', 'e\u0301']
        )
        self.assertEqual(
            bre.findall(r"\X{3}", "a\xE0a\u0300e\xE9e\u0301"),
            ['a\xe0a\u0300', 'e\xe9e\u0301']
        )
        # `self.assertEqual(regex.findall(r"\X", "\r\r\n\u0301A\u0301"), ['\r', '\r\n', '\u0301', 'A\u0301'])`
        self.assertEqual(bre.search(r'\X$', 'ab\u2103').group(), '\u2103')

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
        template = _bre_parse._ReplaceParser(pattern, r'\c\1\2\C\3\E\4')
        template.parse()

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

        self.assertEqual('This is a test for stacking!', results)

    def test_span_stacked_case(self):
        """Test stacked casing of non-spans in and out of a span."""

        text = "This is a test for STACKING!"
        pattern = re.compile(r"(.+?)(STACKING)(!)")
        expand = bre.compile_replace(pattern, r'\1\c\L\l\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for stacking!', results)

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

        self.assertEqual('Test STACKED!', results)

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

        self.assertEqual('This is a complex UPPERCASE test!', results)

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

        self.assertEqual('This is a complex lowercase TEST!', results)

    def test_span_upper_after_lower(self):
        """Test lowercase followed by uppercase span."""

        text = "This is a complex uppercase test!"
        pattern = re.compile(r"(.+?)(uppercase)(.+)")
        expand = bre.compile_replace(pattern, r'\1\l\C\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE test!', results)

    def test_span_lower_after_upper(self):
        """Test uppercase followed by lowercase span."""

        text = "This is a complex LOWERCASE test!"
        pattern = re.compile(r"(.+?)(LOWERCASE)(.+)")
        expand = bre.compile_replace(pattern, r'\1\c\L\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase test!', results)

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

    def test_normal_escaping_replace(self):
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

    def test_bytes_normal_escaping_replace(self):
        """Test bytes normal escaped slash."""

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
        self.assertEqual('THIS iS A TEST FOR Named capture groups!', results)

    def test_mixed_groups2(self):
        """Test mix of upper and lower case with group indexes and a string replace pattern."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.+?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = re.compile(text_pattern)

        # This will pass because we do not need to resolve named groups.
        expand = bre.compile_replace(pattern, r'\l\C\g<1>\l\g<2>\L\c\g<3>\E\g<4>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('THIS iS A TEST FOR Named capture groups!', results)

    def test_mixed_groups3(self):
        """Test mix of upper and lower case with named groups and a compiled replace pattern."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.+?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = re.compile(text_pattern)

        # Now using compiled pattern, we can use named groups in replace template.
        expand = bre.compile_replace(pattern, r'\l\C\g<first>\l\g<second>\L\c\g<third>\E\g<fourth>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('THIS iS A TEST FOR Named capture groups!', results)

    def test_as_replace_function(self):
        """Test that replace can be used as a replace function."""

        text = "this will be fed into re.subn!  Here we go!  this will be fed into re.subn!  Here we go!"
        text_pattern = r"(?P<first>this )(?P<second>.+?)(!)"
        pattern = bre.compile_search(text_pattern)
        replace = bre.compile_replace(pattern, r'\c\g<first>is awesome\g<3>')
        result, count = pattern.subn(replace, text)

        self.assertEqual(result, "This is awesome!  Here we go!  This is awesome!  Here we go!")
        self.assertEqual(count, 2)

    def test_bytes_replace(self):
        """Test that bytes regex result is a bytes string."""

        text = b"This is some bytes text!"
        pattern = bre.compile_search(br"This is (some bytes text)!")
        expand = bre.compile_replace(pattern, br'\C\1\E')
        m = pattern.match(text)
        result = expand(m)
        self.assertEqual(result, b"SOME BYTES TEXT")
        self.assertTrue(isinstance(result, bytes))

    def test_template_replace(self):
        """Test replace by passing in replace function."""

        text = "Replace with function test!"
        pattern = bre.compile_search('(.+)')
        repl = _bre_parse._ReplaceParser(pattern, 'Success!').parse()
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
            'THIS iS A TEST FOR Numeric capture groups!\nTHIS IS A TEST FOR NUMERIC CAPTURE GROUPS!',
            results
        )

    def test_numeric_format_groups(self):
        """Test numeric format capture groups."""

        text = "this is a test for numeric capture groups!"
        text_pattern = r"(this )(.+?)(numeric capture )(groups)(!)"
        pattern = re.compile(text_pattern)

        expandf = bre.compile_replace(pattern, r'\l\C{0001}\l{02}\L\c{03}\E{004}\E{5}\n\C{000}\E', bre.FORMAT)
        results = expandf(pattern.match(text))
        self.assertEqual(
            'THIS iS A TEST FOR Numeric capture groups!\nTHIS IS A TEST FOR NUMERIC CAPTURE GROUPS!',
            results
        )

        text = b"this is a test for numeric capture groups!"
        text_pattern = br"(this )(.+?)(numeric capture )(groups)(!)"
        pattern = re.compile(text_pattern)

        expandf = bre.compile_replace(pattern, br'\l\C{0001}\l{02}\L\c{03}\E{004}\E{5}\n\C{000}\E', bre.FORMAT)
        results = expandf(pattern.match(text))
        self.assertEqual(
            b'THIS iS A TEST FOR Numeric capture groups!\nTHIS IS A TEST FOR NUMERIC CAPTURE GROUPS!',
            results
        )

    def test_escaped_format_groups(self):
        """Test escaping of format capture groups."""

        text = "this is a test for format capture groups!"
        text_pattern = r"(this )(.+?)(format capture )(groups)(!)"
        pattern = re.compile(text_pattern)

        expandf = bre.compile_replace(
            pattern, r'\l\C{{0001}}\l{{{02}}}\L\c{03}\E{004}\E{5}\n\C{000}\E', bre.FORMAT
        )
        results = expandf(pattern.match(text))
        self.assertEqual(
            '{0001}{IS A TEST FOR }Format capture groups!\nTHIS IS A TEST FOR FORMAT CAPTURE GROUPS!',
            results
        )

        text = b"this is a test for format capture groups!"
        text_pattern = br"(this )(.+?)(format capture )(groups)(!)"
        pattern = re.compile(text_pattern)

        expandf = bre.compile_replace(
            pattern, br'\l\C{{0001}}\l{{{02}}}\L\c{03}\E{004}\E{5}\n\C{000}\E', bre.FORMAT
        )
        results = expandf(pattern.match(text))
        self.assertEqual(
            b'{0001}{IS A TEST FOR }Format capture groups!\nTHIS IS A TEST FOR FORMAT CAPTURE GROUPS!',
            results
        )

    def test_format_auto(self):
        """Test auto format capture groups."""

        text = "this is a test for format capture groups!"
        text_pattern = r"(this )(.+?)(format capture )(groups)(!)"
        pattern = re.compile(text_pattern)

        expandf = bre.compile_replace(
            pattern, r'\C{}\E\n\l\C{}\l{}\L\c{}\E{}\E{}{{}}', bre.FORMAT
        )
        results = expandf(pattern.match(text))
        self.assertEqual(
            'THIS IS A TEST FOR FORMAT CAPTURE GROUPS!\nTHIS iS A TEST FOR Format capture groups!{}',
            results
        )

        text = b"this is a test for format capture groups!"
        text_pattern = br"(this )(.+?)(format capture )(groups)(!)"
        pattern = re.compile(text_pattern)

        expandf = bre.compile_replace(
            pattern, br'\C{}\E\n\l\C{}\l{}\L\c{}\E{}\E{}{{}}', bre.FORMAT
        )
        results = expandf(pattern.match(text))
        self.assertEqual(
            b'THIS IS A TEST FOR FORMAT CAPTURE GROUPS!\nTHIS iS A TEST FOR Format capture groups!{}',
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
        text_pattern = r"(\w{2})+"
        pattern = re.compile(text_pattern)

        expand = bre.compile_replace(
            pattern, r'{[-1]}{[0]}', bre.FORMAT
        )
        results = expand(pattern.match(text))
        self.assertEqual(
            'ababababab',
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

    def test_bytes_format_capture_bases(self):
        """Test capture bases."""

        text = b"abababab"
        text_pattern = br"(\w)+"
        pattern = re.compile(text_pattern)

        expand = bre.compile_replace(
            pattern, br'{1[-0x1]}{1[-0o1]}{1[-0b1]}', bre.FORMAT
        )

        results = expand(pattern.match(text))
        self.assertEqual(b'bbb', results)

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
            pattern, r'\{1}\\{1}', bre.FORMAT
        )
        results = expand(pattern.match(text))
        self.assertEqual(
            '\\b\\b',
            results
        )

    def test_normal_string_escaped_unicode(self):
        """Test normal string escaped Unicode."""

        pattern = bre.compile('Test')
        result = pattern.sub('\\C\\U00000070\\U0001F360\\E', 'Test')
        self.assertEqual(result, 'P\U0001F360')

    def test_format_inter_escape(self):
        """Test escaped characters inside format group."""

        self.assertEqual(
            bre.subf(
                r'(Te)(st)(ing)(!)',
                r'\x7b1\x7d-\u007b2\u007d-\U0000007b3\U0000007d-\N{LEFT CURLY BRACKET}4\N{RIGHT CURLY BRACKET}',
                'Testing!'
            ),
            "Te-st-ing-!"
        )
        self.assertEqual(
            bre.subf(
                r'(Te)(st)(ing)(!)',
                r'\1731\175-{2:\\^6}',
                'Testing!'
            ),
            "Te-\\\\st\\\\"
        )

        with pytest.raises(SyntaxError):
            bre.subf(r'(test)', r'{\g}', 'test')

        with pytest.raises(ValueError):
            bre.subf(br'(test)', br'{\777}', b'test')

    def test_format_features(self):
        """Test format features."""

        pattern = bre.compile(r'(Te)(st)(?P<group>ing)')
        self.assertEqual(pattern.subf(r'{.__class__.__name__}', 'Testing'), 'str')
        self.assertEqual(pattern.subf(r'{1:<30}', 'Testing'), 'Te                            ')
        self.assertEqual(pattern.subf(r'{1:30}', 'Testing'), 'Te                            ')
        self.assertEqual(pattern.subf(r'{1:>30}', 'Testing'), '                            Te')
        self.assertEqual(pattern.subf(r'{1:^30}', 'Testing'), '              Te              ')
        self.assertEqual(pattern.subf(r'{1:*^30}', 'Testing'), '**************Te**************')
        self.assertEqual(pattern.subf(r'{1:^030}', 'Testing'), '00000000000000Te00000000000000')
        self.assertEqual(pattern.subf(r'{1:^^30}', 'Testing'), '^^^^^^^^^^^^^^Te^^^^^^^^^^^^^^')
        self.assertEqual(pattern.subf(r'{1:1^30}', 'Testing'), '11111111111111Te11111111111111')
        self.assertEqual(pattern.subf(r'{1:<30s}', 'Testing'), 'Te                            ')
        self.assertEqual(pattern.subf(r'{1:s}', 'Testing'), 'Te')
        self.assertEqual(pattern.subf(r'{2!r}', 'Testing'), "'st'")

        with pytest.raises(SyntaxError):
            pattern.subf(r'{2!x}', 'Testing')

        with pytest.raises(SyntaxError):
            pattern.subf(r'{2$}', 'Testing')

        with pytest.raises(SyntaxError):
            pattern.subf(r'{2$}', 'Testing')

        with pytest.raises(SyntaxError):
            pattern.subf(r'{a$}', 'Testing')

        with pytest.raises(SyntaxError):
            pattern.subf(r'{:ss}', 'Testing')

        with pytest.raises(ValueError):
            pattern.subf(r'{:030}', 'Testing')

        pattern = bre.compile(br'(Te)(st)(?P<group>ing)')
        self.assertEqual(pattern.subf(br'{.__class__.__name__}', b'Testing'), b'bytes')
        self.assertEqual(pattern.subf(br'{1:<30}', b'Testing'), b'Te                            ')
        self.assertEqual(pattern.subf(br'{1:30}', b'Testing'), b'Te                            ')
        self.assertEqual(pattern.subf(br'{1:>30}', b'Testing'), b'                            Te')
        self.assertEqual(pattern.subf(br'{1:^30}', b'Testing'), b'              Te              ')
        self.assertEqual(pattern.subf(br'{1:*^30}', b'Testing'), b'**************Te**************')
        self.assertEqual(pattern.subf(br'{1:^030}', b'Testing'), b'00000000000000Te00000000000000')
        self.assertEqual(pattern.subf(br'{1:^^30}', b'Testing'), b'^^^^^^^^^^^^^^Te^^^^^^^^^^^^^^')
        self.assertEqual(pattern.subf(br'{1:1^30}', b'Testing'), b'11111111111111Te11111111111111')
        self.assertEqual(pattern.subf(br'{1:<30s}', b'Testing'), b'Te                            ')
        self.assertEqual(pattern.subf(br'{1:s}', b'Testing'), b'Te')
        self.assertEqual(pattern.subf(br'{2!r}', b'Testing'), b"b'st'")

        with pytest.raises(SyntaxError):
            pattern.subf(br'{2!x}', b'Testing')

        with pytest.raises(SyntaxError):
            pattern.subf(br'{2$}', b'Testing')

        with pytest.raises(SyntaxError):
            pattern.subf(br'{2$}', b'Testing')

        with pytest.raises(SyntaxError):
            pattern.subf(br'{a$}', b'Testing')

        with pytest.raises(SyntaxError):
            pattern.subf(br'{:ss}', b'Testing')

        with pytest.raises(ValueError):
            pattern.subf(br'{:030}', b'Testing')

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

    def test_format_existing_group_no_match_with_index(self):
        """Test format group with no match and attempt at indexing."""

        with pytest.raises(IndexError):
            bre.compile(r'(test)|(what)').subf(r'{2[0]}', 'test')

    def test_immutable(self):
        """Test immutable object."""

        pattern = re.compile('test')
        replace = bre.compile_replace(pattern, "whatever")
        with pytest.raises(AttributeError):
            replace.use_format = True

    def test_not_posix_at_end_group(self):
        """Test a situation that is not a POSIX at the end of a group."""

        with pytest.raises(_constants.error) as excinfo:
            bre.compile_search(r'Test [[:graph:]')
        self.assertTrue(excinfo is not None)

    def test_incomplete_replace_byte(self):
        """Test incomplete byte group."""

        p = bre.compile_search(r'test')
        with pytest.raises(SyntaxError):
            bre.compile_replace(p, r'Replace \x fail!')

    def test_bad_posix(self):
        """Test bad posix."""

        with pytest.raises(ValueError) as e:
            bre.compile_search(r'[[:bad:]]', re.UNICODE)

        self.assertEqual(str(e.value), "'bad' does not appear to be a valid property")

    def test_bad_bytes(self):
        """Test bad bytes."""

        with pytest.raises(ValueError):
            bre.compile_search(r'\p{bad_bytes:n}', re.UNICODE)

        with pytest.raises(ValueError):
            bre.compile_search(r'\p{bad_bytes:y}', re.UNICODE)

    def test_bad_category(self):
        """Test bad category."""

        with pytest.raises(ValueError):
            bre.compile_search(r'\p{alphanumeric: bad}', re.UNICODE)

    def test_bad_short_category(self):
        """Test bad category."""

        with pytest.raises(ValueError):
            bre.compile_search(r'\pQ', re.UNICODE)

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

        with pytest.raises(TypeError):
            bre.subf(
                pattern, r'{1[0o3f]}', 'test'
            )

    def test_format_bad_capture_range(self):
        """Test a bad capture."""

        text_pattern = r"(\w)+"
        pattern = re.compile(text_pattern)
        expand = bre.compile_replace(
            pattern, r'{1[37]}', bre.FORMAT
        )

        with pytest.raises(IndexError):
            expand(pattern.match('text'))

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

        assert "Cannot process flags argument with a ReplaceTemplate!" in str(excinfo.value)

    def test_relace_flag_on_template(self):
        """Test when a compile occurs on a template with flags passed."""

        pattern = re.compile('test')
        template = _bre_parse._ReplaceParser(pattern, 'whatever').parse()

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

        m = bre.match(r'This is a test for m[[:lower:]]+!', "This is a test for match!")
        self.assertTrue(m is not None)

        p = bre.compile(r'This is a test for m[[:lower:]]+!')
        m = p.match("This is a test for match!")
        self.assertTrue(m is not None)

    def test_posix_value(self):
        """Test posix values."""

        m = bre.match(r'This is a test for m[[:lower=t:]]+!', "This is a test for match!")
        self.assertTrue(m is not None)

        m = bre.match(r'This is a test for m[[:lower:t:]]+!', "This is a test for match!")
        self.assertTrue(m is not None)

    def test_incomplete_posix_value(self):
        """Test incomplete POSIX value."""

        with pytest.raises(re.error):
            with pytest.warns(FutureWarning):
                bre.match(r'This is a test for m[[:lower=t', "This is a test for m[[:lower=t")

        with pytest.raises(re.error):
            with pytest.warns(FutureWarning):
                bre.match(r'This is a test for m[[:lower=t:', "This is a test for m[[:lower=t:")

        with pytest.raises(re.error):
            with pytest.warns(FutureWarning):
                bre.match(r'This is a test for m[[:lower=t: ', "This is a test for m[[:lower=t: ")

    def test_fullmatch(self):
        """Test that `fullmatch` works."""

        m = bre.fullmatch(r'This is a test for match!', "This is a test for match!")
        self.assertTrue(m is not None)

        p = bre.compile(r'This is a test for match!')
        m = p.fullmatch("This is a test for match!")
        self.assertTrue(m is not None)

    def test_search(self):
        """Test that `search` works."""

        m = bre.search(r'test', "This is a test for search!")
        self.assertTrue(m is not None)

        p = bre.compile(r'test')
        m = p.search("This is a test for search!")
        self.assertTrue(m is not None)

    def test_split(self):
        """Test that `split` works."""

        self.assertEqual(
            bre.split(r'\W+', "This is a test for split!"),
            ["This", "is", "a", "test", "for", "split", ""]
        )

        p = bre.compile(r'\W+')
        self.assertEqual(
            p.split("This is a test for split!"),
            ["This", "is", "a", "test", "for", "split", ""]
        )

    def test_sub(self):
        """Test that `sub` works."""

        self.assertEqual(
            bre.sub(r'tset', 'test', r'This is a tset for sub!'),
            "This is a test for sub!"
        )

        p = bre.compile(r'tset')
        self.assertEqual(
            p.sub(r'test', r'This is a tset for sub!'),
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

        p = bre.compile(r'tset')
        replace = p.compile('test')
        self.assertEqual(
            p.sub(replace, 'This is a tset for sub!'),
            "This is a test for sub!"
        )

    def test_subn(self):
        """Test that `subn` works."""

        self.assertEqual(
            bre.subn(r'tset', 'test', r'This is a tset for subn! This is a tset for subn!'),
            ('This is a test for subn! This is a test for subn!', 2)
        )

        p = bre.compile(r'tset')
        self.assertEqual(
            p.subn('test', r'This is a tset for subn! This is a tset for subn!'),
            ('This is a test for subn! This is a test for subn!', 2)
        )

    def test_subf(self):
        """Test that `subf` works."""

        self.assertEqual(
            bre.subf(r'(t)(s)(e)(t)', '{1}{3}{2}{4}', r'This is a tset for subf!'),
            "This is a test for subf!"
        )

        p = bre.compile(r'(t)(s)(e)(t)')
        self.assertEqual(
            p.subf('{1}{3}{2}{4}', r'This is a tset for subf!'),
            "This is a test for subf!"
        )

    def test_subfn(self):
        """Test that `subfn` works."""

        self.assertEqual(
            bre.subfn(r'(t)(s)(e)(t)', '{1}{3}{2}{4}', r'This is a tset for subfn! This is a tset for subfn!'),
            ('This is a test for subfn! This is a test for subfn!', 2)
        )

        p = bre.compile(r'(t)(s)(e)(t)')
        self.assertEqual(
            p.subfn('{1}{3}{2}{4}', r'This is a tset for subfn! This is a tset for subfn!'),
            ('This is a test for subfn! This is a test for subfn!', 2)
        )

    def test_findall(self):
        """Test that `findall` works."""

        self.assertEqual(
            bre.findall(r'\w+', 'This is a test for findall!'),
            ["This", "is", "a", "test", "for", "findall"]
        )

        p = bre.compile(r'\w+')
        self.assertEqual(
            p.findall('This is a test for findall!'),
            ["This", "is", "a", "test", "for", "findall"]
        )

    def test_finditer(self):
        """Test that `finditer` works."""

        count = 0
        for _ in bre.finditer(r'\w+', 'This is a test for finditer!'):
            count += 1

        self.assertEqual(count, 6)

        count = 0
        p = bre.compile(r'\w+')
        for _ in p.finditer('This is a test for finditer!'):
            count += 1

        self.assertEqual(count, 6)

    def test_expand(self):
        """Test that `expand` works."""

        pattern = bre.compile_search(r'(This is a test for )(m[[:lower:]]+!)')
        m = bre.match(pattern, "This is a test for match!")
        self.assertEqual(
            bre.expand(m, R'\1\C\2\E'),
            'This is a test for MATCH!'
        )

        replace = bre.compile_replace(pattern, R'\1\C\2\E')
        self.assertEqual(
            bre.expand(m, replace),
            'This is a test for MATCH!'
        )

    def test_expandf(self):
        """Test that `expandf` works."""

        pattern = bre.compile_search(r'(This is a test for )(match!)')
        m = bre.match(pattern, "This is a test for match!")
        self.assertEqual(
            bre.expandf(m, R'{1}\C{2}\E'),
            'This is a test for MATCH!'
        )

        replace = bre.compile_replace(pattern, R'{1}\C{2}\E', bre.FORMAT)
        self.assertEqual(
            bre.expandf(m, replace),
            'This is a test for MATCH!'
        )

    def test_auto_compile_off(self):
        """Test auto compile off."""

        p = bre.compile('(test)s', auto_compile=False)
        self.assertTrue(p.match('tests') is not None)

        with pytest.raises(AttributeError):
            p.subf('{1}', 'tests')

        replace = p.compile('{1}')
        with pytest.raises(ValueError):
            p.subf(replace, 'tests')

        replace = p.compile('{1}', bre.FORMAT)
        self.assertEqual(p.subf(replace, 'tests'), 'test')

        # Fail due to `\l` being an invalid escape.
        with pytest.raises(re.error):
            p.sub(r'\ltest', 'tests')
