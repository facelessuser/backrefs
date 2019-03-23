# -*- coding: utf-8 -*-
"""Test bregex lib."""
from __future__ import unicode_literals
import unittest
from backrefs import bregex
from backrefs import _bregex_parse
import regex
import pytest
import random
import copy
import time
try:
    import _regex_core
except ImportError:
    from regex import _regex_core


class TestSearchTemplate(unittest.TestCase):
    """Search template tests."""

    def test_named_lists(self):
        """Test named lists."""

        kwargs = {'name': ['blue', 'green']}
        self.assertTrue(bregex.compile(r'\L<name>', name=['blue', 'green']).match('green') is not None)
        self.assertTrue(bregex.compile(r'\L<name>', **kwargs).match('green') is not None)
        self.assertTrue(bregex.compile_search(r'\L<name>', name=['blue', 'green']).match('green') is not None)
        self.assertTrue(bregex.compile_search(r'\L<name>', **kwargs).match('green') is not None)
        self.assertTrue(bregex.match(r'\L<name>', 'green', name=['blue', 'green']) is not None)
        self.assertTrue(bregex.match(r'\L<name>', 'green', **kwargs) is not None)

    def test_non_raw_string_unicode(self):
        """Test non raw string Unicode notation."""

        self.assertTrue(bregex.compile('\\u0070\\U00000070').match('pp'))
        self.assertTrue(bregex.compile('\\Q\\u0070\\U00000070\\E').match('\\u0070\\U00000070'))

    def test_compile_attributes(self):
        """Test compile attributes."""

        p = bregex.compile('(?x)test')
        self.assertEqual(p.pattern, p._pattern.pattern)
        self.assertEqual(p.flags, p._pattern.flags)
        self.assertEqual(p.groups, p._pattern.groups)
        self.assertEqual(p.groupindex, p._pattern.groupindex)
        self.assertEqual(p.scanner, p._pattern.scanner)

    def test_compile_passthrough(self):
        """Test conditions where a compile object passes through functions."""

        p = bregex.compile('test')
        self.assertTrue(p == bregex.compile(p))
        with pytest.raises(ValueError):
            bregex.compile(p, bregex.X)
        with pytest.raises(ValueError):
            bregex.compile(p, auto_compile=False)
        with pytest.raises(ValueError):
            bregex.compile_search(p, bregex.X)
        self.assertEqual(bregex.sub(p, 'success', 'test'), 'success')

    def test_hash(self):
        """Test hashing of search."""

        p1 = bregex.compile('test')
        p2 = bregex.compile('test')
        p3 = bregex.compile('test', bregex.X)
        p4 = bregex.compile(b'test')

        self.assertTrue(p1 == p2)
        self.assertTrue(p1 != p3)
        self.assertTrue(p1 != p4)

        p5 = copy.copy(p1)
        self.assertTrue(p1 == p5)
        self.assertTrue(p5 in {p1})

    def test_not_flags(self):
        """Test invalid flags."""

        with pytest.raises(_regex_core.error):
            bregex.compile(r'(?-q:test)')

        with pytest.raises(_regex_core.error):
            bregex.compile(r'(?V2:test)')

    def test_comment_failures(self):
        """Test comment failures."""

        with pytest.raises(SyntaxError):
            bregex.compile(r'test(?#test')

    def test_inverse_posix_property(self):
        """Test inverse POSIX property."""

        self.assertTrue(bregex.compile(r'[[:^xdigit:]]').match('i') is not None)

    def test_posix_property_bad_syntax(self):
        """Test that we ignore an incomplete POSIX syntax."""

        self.assertTrue(bregex.compile(r'[[:a]]', regex.V0).match('a]') is not None)
        self.assertTrue(bregex.compile(r'[[:a]]', regex.V1).match('a') is not None)
        self.assertTrue(bregex.compile(r'[[:a]', regex.V0).match('a') is not None)
        self.assertTrue(bregex.compile(r'[[:graph:a]', regex.V0).match('a') is not None)

    def test_cache(self):
        """Test cache."""

        try:
            from regex import _cache
        except ImportError:
            from regex.regex import _cache

        bregex.purge()
        self.assertEqual(bregex._get_cache_size(), 0)
        self.assertEqual(bregex._get_cache_size(True), 0)
        for x in range(1000):
            value = str(random.randint(1, 10000))
            p = bregex.compile(value)
            p.sub('', value)
            self.assertTrue(bregex._get_cache_size() > 0)
            self.assertTrue(bregex._get_cache_size() > 0)
        self.assertTrue(bregex._get_cache_size() == 500)
        self.assertTrue(bregex._get_cache_size(True) == 500)
        bregex.purge()
        self.assertEqual(bregex._get_cache_size(), 0)
        self.assertEqual(bregex._get_cache_size(True), 0)
        self.assertEqual(len(_cache), 0)

    def test_infinite_loop_catch(self):
        """Test infinite loop catch."""

        with pytest.raises(_bregex_parse.LoopException):
            bregex.compile_search(r'(?-x:(?x))', regex.V0 | regex.VERBOSE)

        with pytest.raises(_bregex_parse.LoopException):
            bregex.compile_search(r'(?V1)(?V0)')

    def test_escape_char(self):
        """Test escape char."""

        pattern = bregex.compile_search(
            r'test\etest[\e]{2}'
        )

        self.assertEqual(
            pattern.pattern,
            r'test\x1btest[\x1b]{2}'
        )

        self.assertTrue(pattern.match('test\x1btest\x1b\x1b') is not None)

    def test_comments_v0(self):
        """Test comments v0."""

        pattern = bregex.compile_search(
            r'''(?uV0)Test # \R(?#\R\))(?x:
            Test #\R(?#\R\)
            (Test # \R
            )Test #\R
            )Test # \R'''
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?uV0)Test # (?>\r\n|[\n\v\f\r\x85\u2028\u2029])(?#\R\))(?x:
            Test #\\R(?#\\R\)
            (Test # \\R
            )Test #\\R
            )Test # (?>\r\n|[\n\v\f\r\x85\u2028\u2029])'''
        )

        self.assertTrue(pattern.match('Test # \nTestTestTestTest # \n') is not None)

    def test_mid_verbose(self):
        """Test mid verbose."""

        pattern = bregex.compile_search(r'(?V1)# \R (?x) # \R')
        self.assertEqual(
            pattern.pattern,
            r'(?V1)# (?>\r\n|[\n\v\f\r\x85\u2028\u2029]) (?x) # \\R'
        )

        self.assertTrue(pattern.match('# \n '))

    def test_comments_v1(self):
        """Test comments v1."""

        pattern = bregex.compile_search(
            r'''(?xuV1)
            Test # \R
            (?-x:Test #\R(?#\R\))((?x)
            Test # \R
            )Test #\R)
            Test # \R
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?xuV1)
            Test # \\R
            (?-x:Test #(?>\r\n|[\n\v\f\r\x85\u2028\u2029])(?#\R\))((?x)
            Test # \\R
            )Test #(?>\r\n|[\n\v\f\r\x85\u2028\u2029]))
            Test # \\R
            '''
        )

        self.assertTrue(pattern.match('TestTest #\nTestTest #\nTest') is not None)

    def test_trailing_bslash(self):
        """Test trailing back slash."""

        with pytest.raises(_regex_core.error):
            pattern = bregex.compile_search('test\\', regex.UNICODE)

        with pytest.raises(_regex_core.error):
            pattern = bregex.compile_search('test[\\', regex.UNICODE)

        with pytest.raises(_regex_core.error):
            pattern = bregex.compile_search('test(\\', regex.UNICODE)

        pattern = bregex.compile_search('\\Qtest\\', regex.UNICODE)
        self.assertEqual(pattern.pattern, 'test\\\\')

    def test_escape_values_in_verbose_comments(self):
        """Test added escapes in verbose comments."""

        pattern = bregex.compile_search(r'(?x)test # \R', regex.UNICODE)
        self.assertEqual(pattern.pattern, r'(?x)test # \\R', regex.UNICODE)

    def test_char_group_nested_opening(self):
        """Test char group with nested opening [."""

        pattern = bregex.compile_search(r'test [[] \R', regex.UNICODE)
        self.assertEqual(pattern.pattern, r'test [[] (?>\r\n|[\n\v\f\r\x85\u2028\u2029])', regex.UNICODE)

    def test_posix_parse(self):
        """Test posix in a group."""

        pattern = bregex.compile_search(r'test [[:graph:]] \R', regex.V0)
        self.assertEqual(pattern.pattern, r'test [[:graph:]] (?>\r\n|[\n\v\f\r\x85\u2028\u2029])')

        pattern = bregex.compile_search(r'test [[:graph:]] \R', regex.V1)
        self.assertEqual(pattern.pattern, r'test [[:graph:]] (?>\r\n|[\n\v\f\r\x85\u2028\u2029])')

    def test_inline_comments(self):
        """Test that we properly find inline comments and avoid them."""
        pattern = bregex.compile_search(r'test(?#\l\p{^IsLatin})', regex.UNICODE)
        m = pattern.match('test')
        self.assertEqual(pattern.pattern, r'test(?#\l\p{^IsLatin})')
        self.assertTrue(m is not None)

    def test_unrecognized_backrefs(self):
        """Test unrecognized backrefs."""

        result = _bregex_parse._SearchParser(r'Testing unrecognized backrefs \k!').parse()
        self.assertEqual(r'Testing unrecognized backrefs \k!', result)

    def test_quote(self):
        """Test quoting/escaping."""

        result = _bregex_parse._SearchParser(r'Testing \Q(\s+[quote]*\s+)?\E!').parse()
        self.assertEqual(r'Testing %s!' % regex.escape(r'(\s+[quote]*\s+)?'), result)

    def test_normal_backrefs(self):
        """
        Test normal builtin backrefs.

        They should all pass through unaltered.
        """

        result = _bregex_parse._SearchParser(r'\a\b\f\n\r\t\v\A\b\B\d\D\s\S\w\W\Z\\[\b]\M\m\G').parse()
        self.assertEqual(r'\a\b\f\n\r\t\v\A\b\B\d\D\s\S\w\W\Z\\[\b]\M\m\G', result)

    def test_quote_no_end(self):
        r"""Test quote where no \E is defined."""

        result = _bregex_parse._SearchParser(r'Testing \Q(quote) with no [end]!').parse()
        self.assertEqual(r'Testing %s' % regex.escape(r'(quote) with no [end]!'), result)

    def test_quote_in_char_groups(self):
        """Test that quote backrefs are handled in character groups."""

        result = _bregex_parse._SearchParser(r'Testing [\Qchar\E block] [\Q(AVOIDANCE)\E]!').parse()
        self.assertEqual(r'Testing [char block] [\(AVOIDANCE\)]!', result)

    def test_quote_in_char_groups_with_right_square_bracket_first(self):
        """Test that quote backrefs are handled in character groups that have a right square bracket as first char."""

        result = _bregex_parse._SearchParser(r'Testing [^]\Qchar\E block] []\Q(AVOIDANCE)\E]!').parse()
        self.assertEqual(r'Testing [^]char block] []\(AVOIDANCE\)]!', result)

    def test_extraneous_end_char(self):
        r"""Test that stray '\E's get removed."""

        result = _bregex_parse._SearchParser(r'Testing \Eextraneous end char\E!').parse()
        self.assertEqual(r'Testing extraneous end char!', result)

    def test_escaped_backrefs(self):
        """Ensure escaped backrefs don't get processed."""

        result = _bregex_parse._SearchParser(r'Testing escaped \\Qbackrefs\\E!').parse()
        self.assertEqual(r'Testing escaped \\Qbackrefs\\E!', result)

    def test_escaped_escaped_backrefs(self):
        """Ensure escaping escaped backrefs do get processed."""

        result = _bregex_parse._SearchParser(r'Testing escaped escaped \\\Qbackrefs\\\E!').parse()
        self.assertEqual(r'Testing escaped escaped \\backrefs\\\\!', result)

    def test_escaped_escaped_escaped_backrefs(self):
        """Ensure escaping escaped escaped backrefs don't get processed."""

        result = _bregex_parse._SearchParser(r'Testing escaped escaped \\\\Qbackrefs\\\\E!').parse()
        self.assertEqual(r'Testing escaped escaped \\\\Qbackrefs\\\\E!', result)

    def test_escaped_escaped_escaped_escaped_backrefs(self):
        """
        Ensure escaping escaped escaped escaped backrefs do get processed.

        This is far enough to prove out that we are handling them well enough.
        """

        result = _bregex_parse._SearchParser(r'Testing escaped escaped \\\\\Qbackrefs\\\\\E!').parse()
        self.assertEqual(r'Testing escaped escaped \\\\backrefs\\\\\\\\!', result)

    def test_normal_escaping(self):
        """Normal escaping should be unaltered."""

        result = _bregex_parse._SearchParser(r'\n \\n \\\n \\\\n \\\\\n').parse()
        self.assertEqual(r'\n \\n \\\n \\\\n \\\\\n', result)

    def test_normal_escaping2(self):
        """Normal escaping should be unaltered part2."""

        result = _bregex_parse._SearchParser(r'\y \\y \\\y \\\\y \\\\\y').parse()
        self.assertEqual(r'\y \\y \\\y \\\\y \\\\\y', result)

    def test_unicode_and_verbose_flag(self):
        """Test that VERBOSE and UNICODE together come through."""

        pattern = bregex.compile_search(r'Some pattern', flags=bregex.VERBOSE | bregex.UNICODE)
        self.assertTrue(pattern.flags & bregex.UNICODE and pattern.flags & bregex.VERBOSE)

    def test_detect_verbose_string_flag_at_end(self):
        """Test verbose string flag `(?x)` at end."""

        template = _bregex_parse._SearchParser(
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
        """Test verbose string flag (?x) in char set."""

        pattern = bregex.compile_search(
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
        """Test verbose string flag (?x) in quote."""

        pattern = bregex.compile_search(
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

    def test_version0_string_flag(self):
        """Test finding V0 string flag."""

        template = _bregex_parse._SearchParser(r'Testing for (?V0) version flag.', False, False)
        template.parse()
        self.assertTrue(template.version & bregex.V0)

    def test_version0_string_flag_in_group(self):
        """Test ignoring V0 string flag in group will still use the default."""

        template = _bregex_parse._SearchParser(r'Testing for [(?V0)] version flag.', False, False)
        template.parse()
        self.assertTrue(template.version & bregex.DEFAULT_VERSION)

    def test_version0_string_flag_escaped(self):
        """Test ignoring V0 string flag in group will still use the default."""

        template = _bregex_parse._SearchParser(r'Testing for \(?V0) version flag.', False, False)
        template.parse()
        self.assertTrue(template.version & bregex.DEFAULT_VERSION)

    def test_version0_string_flag_unescaped(self):
        """Test unescaped V0 string flag."""

        template = _bregex_parse._SearchParser(r'Testing for \\(?V0) version flag.', False, False)
        template.parse()
        self.assertTrue(template.version & bregex.V0)

    def test_version0_string_flag_escaped_deep(self):
        """Test deep escaped V0 flag will still use the default."""

        template = _bregex_parse._SearchParser(r'Testing for \\\(?V0) version flag.', False, False)
        template.parse()
        self.assertTrue(template.version & bregex.DEFAULT_VERSION)

    def test_version1_string_flag(self):
        """Test finding V1 string flag."""

        template = _bregex_parse._SearchParser(r'Testing for (?V1) version flag.', False, False)
        template.parse()
        self.assertTrue(template.version & bregex.V1)

    def test_version1_string_flag_in_group(self):
        """Test ignoring V1 string flag in group."""

        template = _bregex_parse._SearchParser(r'Testing for [(?V1)] version flag.', False, False)
        template.parse()
        self.assertTrue(template.version & bregex.DEFAULT_VERSION)

    def test_version1_string_flag_escaped(self):
        """Test ignoring V1 string flag in group."""

        template = _bregex_parse._SearchParser(r'Testing for \(?V1) version flag.', False, False)
        template.parse()
        self.assertTrue(template.version & bregex.DEFAULT_VERSION)

    def test_version1_string_flag_unescaped(self):
        """Test unescaped V1 string flag."""

        template = _bregex_parse._SearchParser(r'Testing for \\(?V1) version flag.', False, False)
        template.parse()
        self.assertTrue(template.version & bregex.V1)

    def test_version1_string_flag_escaped_deep(self):
        """Test deep escaped V1 flag."""

        template = _bregex_parse._SearchParser(r'Testing for \\\(?V1) version flag.', False, False)
        template.parse()
        self.assertTrue(template.version & bregex.DEFAULT_VERSION)

    def test_verbose_comment_no_nl(self):
        """Test verbose comment with no newline."""

        pattern = bregex.compile_search(
            '(?x)This is a # comment with no new line'
        )

        self.assertEqual(
            pattern.pattern,
            '(?x)This is a # comment with no new line'
        )

    def test_version0_and_verbose_flag(self):
        """Test that VERBOSE and V0 together come through."""

        pattern = bregex.compile_search(r'Some pattern', flags=bregex.VERBOSE | bregex.V0)
        self.assertTrue(pattern.flags & bregex.V0 and pattern.flags & bregex.VERBOSE)

    def test_version1_and_verbose_flag(self):
        """Test that VERBOSE and V1 together come through."""

        pattern = bregex.compile_search(r'Some pattern', flags=bregex.VERBOSE | bregex.V1)
        self.assertTrue(pattern.flags & bregex.V1 and pattern.flags & bregex.VERBOSE)

    def test_no_verbose(self):
        """Test no verbose."""

        pattern = bregex.compile_search(
            r'''
            This is a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [#\ ] \Qcomment\E
            This is not a [\#] \Qcomment\E
            This\ is\ a # \Qcomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''
            This is a # comment
            This is not a \# comment
            This is not a [#\ ] comment
            This is not a [\#] comment
            This\ is\ a # comment
            '''
        )

    def test_other_backrefs_v0(self):
        """Test that other backrefs make it through."""

        pattern = bregex.compile_search(
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

    def test_no_verbose_v1(self):
        """Test no verbose."""

        pattern = bregex.compile_search(
            r'''(?V1)
            This is a # \Qcomment\E
            This is not a \# \Qcomment\E
            This is not a [^#\ ] \Qcomment\E
            This is not a [\#[^\ \t]] \Qcomment\E
            This\ is\ a # \Qcomment also'''
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?V1)
            This is a # comment
            This is not a \# comment
            This is not a [^#\ ] comment
            This is not a [\#[^\ \t]] comment
            This\ is\ a # comment\ also'''
        )

    def test_other_backrefs_v1(self):
        """Test that other backrefs make it through."""

        pattern = bregex.compile_search(
            r'''(?xV1)
            This \bis a # \Qcomment\E
            This is\w+ not a \# \Qcomment\E
            '''
        )

        self.assertEqual(
            pattern.pattern,
            r'''(?xV1)
            This \bis a # comment
            This is\w+ not a \# comment
            '''
        )

    def test_regex_pattern_input(self):
        """Test that search pattern input can be a compiled bregex pattern."""

        pattern1 = regex.compile("(test)")
        pattern2 = bregex.compile_search(pattern1)
        m = pattern2.match('test')
        self.assertTrue(m is not None)


class TestReplaceTemplate(unittest.TestCase):
    """Test replace template."""

    def test_hash(self):
        """Test hashing of replace."""

        p1 = bregex.compile('(test)')
        p2 = bregex.compile('(test)')
        p3 = bregex.compile(b'(test)')
        r1 = p1.compile(r'\1')
        r2 = p1.compile(r'\1')
        r3 = p2.compile(r'\1')
        r4 = p2.compile(r'\1', bregex.FORMAT)
        r5 = p3.compile(br'\1')

        self.assertTrue(r1 == r2)
        self.assertTrue(r2 == r3)
        self.assertTrue(r1 != r4)
        self.assertTrue(r1 != r5)

        r5 = copy.copy(r1)
        self.assertTrue(r1 == r5)
        self.assertTrue(r5 in {r1})

    def test_format_failures(self):
        """Test format parsing failures."""

        with pytest.raises(_regex_core.error):
            bregex.subf('test', r'{1.}', 'test', bregex.FORMAT)

        with pytest.raises(IndexError):
            bregex.subf('test', r'{a.}', 'test', bregex.FORMAT)

        with pytest.raises(SyntaxError):
            bregex.subf('test', r'{1[}', 'test', bregex.FORMAT)

        with pytest.raises(SyntaxError):
            bregex.subf('test', r'{a[}', 'test', bregex.FORMAT)

        with pytest.raises(SyntaxError):
            bregex.subf('test', r'test } test', 'test', bregex.FORMAT)

        with pytest.raises(SyntaxError):
            bregex.subf('test', r'test {test', 'test', bregex.FORMAT)

        with pytest.raises(SyntaxError):
            bregex.subf('test', r'test { test', 'test', bregex.FORMAT)

        with pytest.raises(_regex_core.error):
            bregex.subf(b'test', br'{1.}', b'test', bregex.FORMAT)

        with pytest.raises(IndexError):
            bregex.subf(b'test', br'{a.}', b'test', bregex.FORMAT)

        with pytest.raises(SyntaxError):
            bregex.subf(b'test', br'{1[}', b'test', bregex.FORMAT)

        with pytest.raises(SyntaxError):
            bregex.subf(b'test', br'{a[}', b'test', bregex.FORMAT)

        with pytest.raises(SyntaxError):
            bregex.subf(b'test', br'test } test', b'test', bregex.FORMAT)

        with pytest.raises(SyntaxError):
            bregex.subf(b'test', br'test {test', b'test', bregex.FORMAT)

        with pytest.raises(SyntaxError):
            bregex.subf(b'test', br'test { test', b'test', bregex.FORMAT)

        with pytest.raises(TypeError):
            bregex.subf(b'test', br'{[test]}', b'test', bregex.FORMAT)

    def test_format_conversions(self):
        """Test string format conversion paths."""

        self.assertTrue(bregex.subf('test', r'{0.index}', 'test').startswith('<built-in method'))
        self.assertEqual(bregex.subf('test', r'{0.__class__.__name__}', 'test'), 'str')
        self.assertTrue(bregex.subf('test', r'{0.index!s}', 'test').startswith('<built-in method'))
        self.assertEqual(bregex.subf('test', r'{0.__class__.__name__!s}', 'test'), 'str')
        self.assertTrue(bregex.subf('test', r'{0.index!a}', 'test').startswith('<built-in method'))

        self.assertTrue(bregex.subf(b'test', br'{0.index}', b'test').startswith(b'<built-in method'))
        self.assertEqual(bregex.subf(b'test', br'{0.__class__.__name__}', b'test'), b'bytes')
        self.assertTrue(bregex.subf(b'test', br'{0.index!s}', b'test').startswith(b'<built-in method'))
        self.assertEqual(bregex.subf(b'test', br'{0.__class__.__name__!s}', b'test'), b'bytes')
        self.assertTrue(bregex.subf('test', r'{0.index!a}', 'test').startswith('<built-in method'))

    def test_incompatible_strings(self):
        """Test incompatible string types."""

        with pytest.raises(TypeError):
            bregex.compile('test').compile(b'test')

        p1 = bregex.compile('test')
        repl = bregex.compile(b'test').compile(b'other')
        m = p1.match('test')
        with pytest.raises(TypeError):
            repl(m)

    def test_named_unicode_failures(self):
        """Test named Unicode failures."""

        with pytest.raises(SyntaxError):
            bregex.sub('test', r'\N', 'test')

        with pytest.raises(SyntaxError):
            bregex.sub('test', r'\Na', 'test')

        with pytest.raises(SyntaxError):
            bregex.sub('test', r'\N{A.', 'test')

        with pytest.raises(SyntaxError):
            bregex.sub('test', r'\N{A', 'test')

    def test_group_failures(self):
        """Test group failures."""

        with pytest.raises(SyntaxError):
            bregex.sub('test', r'\g', 'test')

        with pytest.raises(SyntaxError):
            bregex.sub('test', r'\ga', 'test')

        with pytest.raises(SyntaxError):
            bregex.sub('test', r'\g<.', 'test')

        with pytest.raises(SyntaxError):
            bregex.sub('test', r'\g<a.', 'test')

        with pytest.raises(SyntaxError):
            bregex.sub('test', r'\g<3', 'test')

    def test_double_digit_group(self):
        """Test double digit group."""

        self.assertEqual(
            bregex.sub('(t)(e)(s)(t)(i)(n)(g)( )(g)(r)(o)(u)(p)', r'\c\10', 'testing group'),
            'R'
        )

    def test_expand_with_none(self):
        """Test none in expand."""

        with pytest.raises(ValueError):
            bregex.expand(None, "")

    def test_unicode_narrow_value(self):
        """Test Unicode narrow value."""

        pattern = regex.compile(r"(some)(.+?)(pattern)(!)")
        expand = bregex.compile_replace(pattern, r'\u005cg')
        results = expand(pattern.match('some test pattern!'))
        self.assertEqual(r'\g', results)

    def test_unexpected_end(self):
        """Test cases where there is an unexpected end to the replace string."""

        pattern = regex.compile(r"(some)(.+?)(pattern)(!)")
        with pytest.raises(_regex_core.error):
            _bregex_parse._ReplaceParser().parse(pattern, '\\1\\l\\')

        with pytest.raises(_regex_core.error):
            _bregex_parse._ReplaceParser().parse(pattern, '\\1\\L\\')

        with pytest.raises(_regex_core.error):
            _bregex_parse._ReplaceParser().parse(pattern, '\\1\\')

    def test_line_break(self):
        r"""Test line break \R."""

        self.assertEqual(
            bregex.sub(r"\R", ' ', 'line\r\nline\nline\r'),
            'line line line '
        )

    def test_bytes_line_break(self):
        r"""Test bytes line break \R."""

        self.assertEqual(
            bregex.sub(br"\R", b' ', b'line\r\nline\nline\r'),
            b'line line line '
        )

    def test_line_break_in_group(self):
        """Test that line break in group matches a normal R."""

        self.assertEqual(
            bregex.sub(r"[\R]", 'l', 'Rine\r\nRine\nRine\r'),
            'line\r\nline\nline\r'
        )

    def test_replace_unicode_name_ascii_range(self):
        """Test replacing Unicode names in the ASCII range."""

        pattern = regex.compile(r"(some)(.+?)(pattern)(!)")
        expand = bregex.compile_replace(
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

        pattern = regex.compile(r"(some)(.+?)(pattern)(!)")
        expand = bregex.compile_replace(
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

        pattern = regex.compile(r"(some)(.+?)(pattern)(!)")
        expandf = bregex.compile_replace(
            pattern,
            r'{1} \N{Black club suit}\l\N{Greek Capital Letter omega} and '
            r'\LSPAN \N{Greek Capital Letter omega}\E and Escaped \\N{{Greek Capital Letter omega}}\E {3}',
            bregex.FORMAT
        )
        results = expandf(pattern.match('some test pattern!'))

        self.assertEqual(
            'some \u2663\u03c9 and span \u03c9 and Escaped \\N{Greek Capital Letter omega} pattern',
            results
        )

    def test_get_replace_template_string(self):
        """Test retrieval of the replace template original string."""

        pattern = regex.compile(r"(some)(.+?)(pattern)(!)")
        template = _bregex_parse._ReplaceParser()
        template.parse(pattern, r'\c\1\2\C\3\E\4')

        self.assertEqual(r'\c\1\2\C\3\E\4', template.get_base_template())

    def test_uppercase(self):
        """Test uppercase."""

        text = "This is a test for uppercase!"
        pattern = regex.compile(r"(.+?)(uppercase)(!)")
        expand = bregex.compile_replace(pattern, r'\1\c\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for Uppercase!', results)

    def test_lowercase(self):
        """Test lowercase."""

        text = "This is a test for LOWERCASE!"
        pattern = regex.compile(r"(.+?)(LOWERCASE)(!)")
        expand = bregex.compile_replace(pattern, r'\1\l\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for lOWERCASE!', results)

    def test_span_uppercase(self):
        """Test span uppercase."""

        text = "This is a test for uppercase!"
        pattern = regex.compile(r"(.+?)(uppercase)(!)")
        expand = bregex.compile_replace(pattern, r'\1\C\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for UPPERCASE!', results)

    def test_span_lowercase(self):
        """Test span lowercase."""

        text = "This is a test for LOWERCASE!"
        pattern = regex.compile(r"(.+?)(LOWERCASE)(!)")
        expand = bregex.compile_replace(pattern, r'\1\L\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for lowercase!', results)

    def test_single_stacked_case(self):
        """Test stacked casing of non-spans."""

        text = "This is a test for stacking!"
        pattern = regex.compile(r"(.+?)(stacking)(!)")
        expand = bregex.compile_replace(pattern, r'\1\c\l\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for stacking!', results)

    def test_span_stacked_case(self):
        """Test stacked casing of non-spans in and out of a span."""

        text = "This is a test for STACKING!"
        pattern = regex.compile(r"(.+?)(STACKING)(!)")
        expand = bregex.compile_replace(pattern, r'\1\c\L\l\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for stacking!', results)

    def test_single_case_followed_by_bslash(self):
        """Test single backslash following a single case reference."""

        text = "This is a test!"
        pattern = regex.compile(r"(.+?)(test)(!)")
        expand = bregex.compile_replace(pattern, r'\1\c\\\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a \\test!', results)

    def test_span_case_followed_by_bslash(self):
        """Test single backslash following a span case reference."""

        text = "This is a test!"
        pattern = regex.compile(r"(.+?)(test)(!)")
        expand = bregex.compile_replace(pattern, r'\1\C\\\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a \\TEST!', results)

    def test_single_span_stacked_literal(self):
        """Test single backslash before a single case reference before a literal."""

        text = "This is a test!"
        pattern = regex.compile(r"(.+?)(test)(!)")
        expand = bregex.compile_replace(pattern, r'Test \l\Cstacked\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('Test STACKED!', results)

    def test_extraneous_end_char(self):
        """Test for extraneous end characters."""

        text = "This is a test for extraneous \\E chars!"
        pattern = regex.compile(r"(.+?)(extraneous)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for extraneous \\E chars!', results)

    def test_normal_backrefs(self):
        """Test for normal backrefs."""

        text = "This is a test for normal backrefs!"
        pattern = regex.compile(r"(.+?)(normal)(.+)")
        expand = bregex.compile_replace(pattern, '\\1\\2\t\\3 \u0067\147\v\f\n')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for normal\t backrefs! gg\v\f\n', results)

    def test_span_case_no_end(self):
        r"""Test case where no \E is defined."""

        text = "This is a test for uppercase with no end!"
        pattern = regex.compile(r"(.+?)(uppercase)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\C\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a test for UPPERCASE WITH NO END!', results)

    def test_span_upper_after_upper(self):
        """Test uppercase followed by uppercase span."""

        text = "This is a complex uppercase test!"
        pattern = regex.compile(r"(.+?)(uppercase)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\c\C\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE test!', results)

    def test_span_lower_after_lower(self):
        """Test lowercase followed by lowercase span."""

        text = "This is a complex LOWERCASE test!"
        pattern = regex.compile(r"(.+?)(LOWERCASE)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\l\L\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase test!', results)

    def test_span_upper_around_upper(self):
        """Test uppercase span around an uppercase."""

        text = "This is a complex uppercase test!"
        pattern = regex.compile(r"(.+?)(uppercase)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\C\c\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE test!', results)

    def test_span_lower_around_lower(self):
        """Test lowercase span around an lowercase."""

        text = "This is a complex LOWERCASE test!"
        pattern = regex.compile(r"(.+?)(LOWERCASE)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\L\l\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase test!', results)

    def test_upper_after_upper(self):
        """Test uppercase after uppercase."""

        text = "This is a complex uppercase test!"
        pattern = regex.compile(r"(.+?)(uppercase)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\c\c\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex Uppercase test!', results)

    def test_upper_span_inside_upper_span(self):
        """Test uppercase span inside uppercase span."""

        text = "This is a complex uppercase test!"
        pattern = regex.compile(r"(.+?)(uppercase)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\C\C\2\E\3\E')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE test!', results)

    def test_lower_after_lower(self):
        """Test lowercase after lowercase."""

        text = "This is a complex LOWERCASE test!"
        pattern = regex.compile(r"(.+?)(LOWERCASE)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\l\l\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lOWERCASE test!', results)

    def test_lower_span_inside_lower_span(self):
        """Test lowercase span inside lowercase span."""

        text = "This is a complex LOWERCASE TEST!"
        pattern = regex.compile(r"(.+?)(LOWERCASE)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\L\L\2\E\3\E')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase TEST!', results)

    def test_span_upper_after_lower(self):
        """Test lowercase followed by uppercase span."""

        text = "This is a complex uppercase test!"
        pattern = regex.compile(r"(.+?)(uppercase)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\l\C\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex UPPERCASE test!', results)

    def test_span_lower_after_upper(self):
        """Test uppercase followed by lowercase span."""

        text = "This is a complex LOWERCASE test!"
        pattern = regex.compile(r"(.+?)(LOWERCASE)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\c\L\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex lowercase test!', results)

    def test_span_upper_around_lower(self):
        """Test uppercase span around a lowercase."""

        text = "This is a complex uppercase test!"
        pattern = regex.compile(r"(.+?)(uppercase)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\C\l\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex uPPERCASE test!', results)

    def test_span_lower_around_upper(self):
        """Test lowercase span around an uppercase."""

        text = "This is a complex LOWERCASE test!"
        pattern = regex.compile(r"(.+?)(LOWERCASE)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\L\c\2\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a complex Lowercase test!', results)

    def test_end_after_single_case(self):
        r"""Test that \E after a single case such as \l is handled proper."""

        text = "This is a single case end test!"
        pattern = regex.compile(r"(.+?)(case)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\l\E\2\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a single case end test!', results)

    def test_end_after_single_case_nested(self):
        r"""Test that \E after a single case such as \l is handled proper inside a span."""

        text = "This is a nested single case end test!"
        pattern = regex.compile(r"(.+?)(case)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\C\2\c\E\3')
        results = expand(pattern.match(text))

        self.assertEqual('This is a nested single CASE end test!', results)

    def test_single_case_at_end(self):
        """Test when a single case backref is the final char."""

        text = "This is a single case at end test!"
        pattern = regex.compile(r"(.+?)(case)(.+)")
        expand = bregex.compile_replace(pattern, r'\1\2\3\c')
        results = expand(pattern.match(text))

        self.assertEqual('This is a single case at end test!', results)

    def test_single_case_not_on_group(self):
        """Test single case when not applied to a group."""

        text = "This is a single case test that is not on a group!"
        pattern = regex.compile(r"(.+)")
        expand = bregex.compile_replace(pattern, r'\cstill works!')
        results = expand(pattern.match(text))

        self.assertEqual('Still works!', results)

    def test_case_span_not_on_group(self):
        """Test case span when not applied to a group."""

        text = "This is a case test that is not on a group!"
        pattern = regex.compile(r"(.+)")
        expand = bregex.compile_replace(pattern, r'\Cstill\E works!')
        results = expand(pattern.match(text))

        self.assertEqual('STILL works!', results)

    def test_escaped_backrefs(self):
        """Test escaped backrefs."""

        text = "This is a test of escaped backrefs!"
        pattern = regex.compile(r"(.+)")
        expand = bregex.compile_replace(pattern, r'\\\\l\\c\1')
        results = expand(pattern.match(text))

        self.assertEqual(r'\\l\cThis is a test of escaped backrefs!', results)

    def test_escaped_slash_before_backref(self):
        """Test deeper escaped slash."""

        text = "this is a test of escaped slash backrefs!"
        pattern = regex.compile(r"(.+)")
        expand = bregex.compile_replace(pattern, r'\\\\\lTest: \\\c\1')
        results = expand(pattern.match(text))

        self.assertEqual(r'\\test: \This is a test of escaped slash backrefs!', results)

    def test_normal_escaping(self):
        """Test normal escaped slash."""

        text = "This is a test of normal escaping!"
        pattern = regex.compile(r"(.+)")
        repl_pattern = r'\e \\e \\\e \\\\e \\\\\e'
        expand = bregex.compile_replace(pattern, repl_pattern)
        m = pattern.match(text)
        results = expand(m)
        results2 = pattern.sub(repl_pattern, text)

        self.assertEqual(results2, results)
        self.assertEqual('\\e \\e \\\\e \\\\e \\\\\\e', results)

    def test_bytes_normal_escaping(self):
        """Test bytes normal escaped slash."""

        text = b"This is a test of normal escaping!"
        pattern = regex.compile(br"(.+)")
        repl_pattern = br'\e \\e \\\e \\\\e \\\\\e'
        expand = bregex.compile_replace(pattern, repl_pattern)
        m = pattern.match(text)
        results = expand(m)
        results2 = pattern.sub(repl_pattern, text)

        self.assertEqual(results2, results)
        self.assertEqual(b'\\e \\e \\\\e \\\\e \\\\\\e', results)

    def test_escaped_slash_at_eol(self):
        """Test escaped slash at end of line."""

        text = "This is a test of eol escaping!"
        pattern = regex.compile(r"(.+)")
        expand = bregex.compile_replace(pattern, r'\\\\')
        results = expand(pattern.match(text))

        self.assertEqual('\\\\', results)

    def test_unrecognized_backrefs(self):
        """Test unrecognized backrefs, or literal backslash before a char."""

        text = "This is a test of unrecognized backrefs!"
        pattern = regex.compile(r"(.+)")
        expand = bregex.compile_replace(pattern, r'\k\1')
        results = expand(pattern.match(text))

        self.assertEqual(r'\kThis is a test of unrecognized backrefs!', results)

    def test_ignore_group(self):
        """Test that backrefs inserted by matching groups are passed over."""

        text = r"This is a test to see if \Cbackre\Efs in gr\coups get ig\Lnor\led proper!"
        pattern = regex.compile(r"(This is a test to see if \\Cbackre\\Efs )(.+?)(ig\\Lnor\\led )(proper)(!)")
        expand = bregex.compile_replace(pattern, r'Here is the first \C\1\Ethe second \c\2third \L\3\E\4\5')
        results = expand(pattern.match(text))

        self.assertEqual(
            r'Here is the first THIS IS A TEST TO SEE IF \CBACKRE\EFS the second In gr\coups get third '
            r'ig\lnor\led proper!',
            results
        )

    def test_mixed_groups1(self):
        """Test mix of upper and lower case with named groups and a string replace pattern (1)."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.+?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = regex.compile(text_pattern)

        # Use uncompiled pattern when compiling replace.
        expand = bregex.compile_replace(pattern, r'\l\C\g<first>\l\g<second>\L\c\g<third>\E\g<fourth>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('THIS iS A TEST FOR Named capture groups!', results)

    def test_mixed_groups2(self):
        """Test mix of upper and lower case with group indexes and a string replace pattern (2)."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.+?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = regex.compile(text_pattern)

        # This will pass because we do not need to resolve named groups.
        expand = bregex.compile_replace(pattern, r'\l\C\g<1>\l\g<2>\L\c\g<3>\E\g<4>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('THIS iS A TEST FOR Named capture groups!', results)

    def test_mixed_groups3(self):
        """Test mix of upper and lower case with named groups and a compiled replace pattern (3)."""

        text = "this is a test for named capture groups!"
        text_pattern = r"(?P<first>this )(?P<second>.+?)(?P<third>named capture )(?P<fourth>groups)(!)"
        pattern = regex.compile(text_pattern)

        # Now using compiled pattern, we can use named groups in replace template.
        expand = bregex.compile_replace(pattern, r'\l\C\g<first>\l\g<second>\L\c\g<third>\E\g<fourth>\E\5')
        results = expand(pattern.match(text))
        self.assertEqual('THIS iS A TEST FOR Named capture groups!', results)

    def test_as_replace_function(self):
        """Test that replace can be used as a replace function."""

        text = "this will be fed into regex.subn!  Here we go!  this will be fed into regex.subn!  Here we go!"
        text_pattern = r"(?P<first>this )(?P<second>.+?)(!)"
        pattern = bregex.compile_search(text_pattern)
        replace = bregex.compile_replace(pattern, r'\c\g<first>is awesome\g<3>')
        result, count = pattern.subn(replace, text)

        self.assertEqual(result, "This is awesome!  Here we go!  This is awesome!  Here we go!")
        self.assertEqual(count, 2)

    def test_bytes_replace(self):
        """Test that bytes regex result is a bytes string."""

        text = b"This is some bytes text!"
        pattern = bregex.compile_search(br"This is (some bytes text)!")
        expand = bregex.compile_replace(pattern, br'\C\1\E')
        m = pattern.match(text)
        result = expand(m)
        self.assertEqual(result, b"SOME BYTES TEXT")
        self.assertTrue(isinstance(result, bytes))

    def test_template_replace(self):
        """Test replace by passing in replace template."""

        text = "Replace with template test!"
        pattern = bregex.compile_search('(.+)')
        repl = _bregex_parse._ReplaceParser().parse(pattern, 'Success!')
        expand = bregex.compile_replace(pattern, repl)

        m = pattern.match(text)
        result = expand(m)

        self.assertEqual('Success!', result)

    def test_numeric_groups(self):
        """Test numeric capture groups."""

        text = "this is a test for numeric capture groups!"
        text_pattern = r"(this )(.+?)(numeric capture )(groups)(!)"
        pattern = regex.compile(text_pattern)

        expand = bregex.compile_replace(pattern, r'\l\C\g<0001>\l\g<02>\L\c\g<03>\E\g<004>\E\5\n\C\g<000>\E')
        results = expand(pattern.match(text))
        self.assertEqual(
            'THIS iS A TEST FOR Numeric capture groups!\nTHIS IS A TEST FOR NUMERIC CAPTURE GROUPS!',
            results
        )

    def test_numeric_format_groups(self):
        """Test numeric format capture groups."""

        text = "this is a test for numeric capture groups!"
        text_pattern = r"(this )(.+?)(numeric capture )(groups)(!)"
        pattern = regex.compile(text_pattern)

        expandf = bregex.compile_replace(pattern, r'\l\C{0001}\l{02}\L\c{03}\E{004}\E{5}\n\C{000}\E', bregex.FORMAT)
        results = expandf(pattern.match(text))
        self.assertEqual(
            'THIS iS A TEST FOR Numeric capture groups!\nTHIS IS A TEST FOR NUMERIC CAPTURE GROUPS!',
            results
        )

        text = b"this is a test for numeric capture groups!"
        text_pattern = br"(this )(.+?)(numeric capture )(groups)(!)"
        pattern = regex.compile(text_pattern)

        expandf = bregex.compile_replace(pattern, br'\l\C{0001}\l{02}\L\c{03}\E{004}\E{5}\n\C{000}\E', bregex.FORMAT)
        results = expandf(pattern.match(text))
        self.assertEqual(
            b'THIS iS A TEST FOR Numeric capture groups!\nTHIS IS A TEST FOR NUMERIC CAPTURE GROUPS!',
            results
        )

    def test_escaped_format_groups(self):
        """Test escaping of format capture groups."""

        text = "this is a test for format capture groups!"
        text_pattern = r"(this )(.+?)(format capture )(groups)(!)"
        pattern = regex.compile(text_pattern)

        expandf = bregex.compile_replace(
            pattern, r'\l\C{{0001}}\l{{{02}}}\L\c{03}\E{004}\E{5}\n\C{000}\E', bregex.FORMAT
        )
        results = expandf(pattern.match(text))
        self.assertEqual(
            '{0001}{IS A TEST FOR }Format capture groups!\nTHIS IS A TEST FOR FORMAT CAPTURE GROUPS!',
            results
        )

        text = b"this is a test for format capture groups!"
        text_pattern = br"(this )(.+?)(format capture )(groups)(!)"
        pattern = regex.compile(text_pattern)

        expandf = bregex.compile_replace(
            pattern, br'\l\C{{0001}}\l{{{02}}}\L\c{03}\E{004}\E{5}\n\C{000}\E', bregex.FORMAT
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
        pattern = regex.compile(text_pattern)

        expandf = bregex.compile_replace(
            pattern, r'\C{}\E\n\l\C{}\l{}\L\c{}\E{}\E{}{{}}', bregex.FORMAT
        )
        results = expandf(pattern.match(text))
        self.assertEqual(
            'THIS IS A TEST FOR FORMAT CAPTURE GROUPS!\nTHIS iS A TEST FOR Format capture groups!{}',
            results
        )

        text = b"this is a test for format capture groups!"
        text_pattern = br"(this )(.+?)(format capture )(groups)(!)"
        pattern = regex.compile(text_pattern)

        expandf = bregex.compile_replace(
            pattern, br'\C{}\E\n\l\C{}\l{}\L\c{}\E{}\E{}{{}}', bregex.FORMAT
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
        pattern = regex.compile(text_pattern)

        expand = bregex.compile_replace(
            pattern, r'{1[0]}{1[2]}{1[4]}', bregex.FORMAT
        )
        results = expand(pattern.match(text))
        self.assertEqual(
            'aaa',
            results
        )

    def test_format_auto_captures(self):
        """Test format auto capture indexing."""

        text = "abababab"
        text_pattern = r"(\w)+"
        pattern = regex.compile(text_pattern)

        expand = bregex.compile_replace(
            pattern, r'{[-1]}{[3]}', bregex.FORMAT
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
        pattern = regex.compile(text_pattern)

        expand = bregex.compile_replace(
            pattern, r'{1[-0x1]}{1[0o3]}{1[0b101]}', bregex.FORMAT
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
        pattern = regex.compile(text_pattern)

        expand = bregex.compile_replace(
            pattern, br'{1[-0x1]}{1[0o3]}{1[0b101]}', bregex.FORMAT
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
        pattern = regex.compile(text_pattern)

        expand = bregex.compile_replace(
            pattern, r'{1[1]}\g<1>\\g<1>\1\\2\\\3', bregex.FORMAT
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
        pattern = regex.compile(text_pattern)

        expand = bregex.compile_replace(
            pattern, r'\{1[-1]}\\{1[-1]}', bregex.FORMAT
        )
        results = expand(pattern.match(text))
        self.assertEqual(
            '\\b\\b',
            results
        )

    def test_normal_string_escaped_unicode(self):
        """Test normal string escaped Unicode."""

        pattern = bregex.compile('Test')
        result = pattern.sub('\\C\\U00000070\\U0001F360\\E', 'Test')
        self.assertEqual(result, 'P\U0001F360')

    def test_format_inter_escape(self):
        """Test escaped characters inside format group."""

        self.assertEqual(
            bregex.subf(
                r'(Te)(st)(ing)(!)',
                r'\x7b1\x7d-\u007b2\u007d-\U0000007b3\U0000007d-\N{LEFT CURLY BRACKET}4\N{RIGHT CURLY BRACKET}',
                'Testing!'
            ),
            "Te-st-ing-!"
        )
        self.assertEqual(
            bregex.subf(
                r'(Te)(st)(ing)(!)',
                r'\1731\175-{2:\\^6}',
                'Testing!'
            ),
            "Te-\\\\st\\\\"
        )

        with pytest.raises(SyntaxError):
            bregex.subf(r'(test)', r'{\g}', 'test')

        with pytest.raises(ValueError):
            bregex.subf(br'(test)', br'{\777}', b'test')

    def test_format_features(self):
        """Test format features."""

        pattern = bregex.compile(r'(Te)(st)(?P<group>ing)')
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

        pattern = bregex.compile(br'(Te)(st)(?P<group>ing)')
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
        pattern = regex.compile('Test')
        expand = bregex.compile_replace(pattern, r'\C\u0109\n\x77\E\l\x57\c\u0109')
        results = expand(pattern.match('Test'))
        self.assertEqual('\u0108\nWw\u0108', results)

        expandf = bregex.compile_replace(pattern, r'\C\u0109\n\x77\E\l\x57\c\u0109', bregex.FORMAT)
        results = expandf(pattern.match('Test'))
        self.assertEqual('\u0108\nWw\u0108', results)

        # Wide Unicode must be evaluated before narrow Unicode
        pattern = regex.compile('Test')
        expand = bregex.compile_replace(pattern, r'\C\U00000109\n\x77\E\l\x57\c\U00000109')
        results = expand(pattern.match('Test'))
        self.assertEqual('\u0108\nWw\u0108', results)

        expandf = bregex.compile_replace(pattern, r'\C\U00000109\n\x77\E\l\x57\c\U00000109', bregex.FORMAT)
        results = expandf(pattern.match('Test'))
        self.assertEqual('\u0108\nWw\u0108', results)

        # Bytes doesn't care about Unicode, but should evaluate bytes
        pattern = regex.compile(b'Test')
        expand = bregex.compile_replace(pattern, br'\C\u0109\n\x77\E\l\x57\c\u0109')
        results = expand(pattern.match(b'Test'))
        self.assertEqual(b'\\U0109\nWw\\u0109', results)

        expandf = bregex.compile_replace(pattern, br'\C\u0109\n\x77\E\l\x57\c\u0109', bregex.FORMAT)
        results = expandf(pattern.match(b'Test'))
        self.assertEqual(b'\\U0109\nWw\\u0109', results)

        pattern = regex.compile(b'Test')
        expand = bregex.compile_replace(pattern, br'\C\U00000109\n\x77\E\l\x57\c\U00000109')
        results = expand(pattern.match(b'Test'))
        self.assertEqual(b'\U00000109\nWw\U00000109', results)

        expandf = bregex.compile_replace(pattern, br'\C\U00000109\n\x77\E\l\x57\c\U00000109', bregex.FORMAT)
        results = expandf(pattern.match(b'Test'))
        self.assertEqual(b'\U00000109\nWw\U00000109', results)

        # Format doesn't care about groups
        pattern = regex.compile('Test')
        expand = bregex.compile_replace(pattern, r'\127\666\C\167\666\n\E\l\127\c\666', bregex.FORMAT)
        results = expand(pattern.match('Test'))
        self.assertEqual('W\u01b6W\u01b5\nw\u01b5', results)

        pattern = regex.compile(b'Test')
        expandf = bregex.compile_replace(pattern, br'\127\C\167\n\E\l\127', bregex.FORMAT)
        results = expandf(pattern.match(b'Test'))
        self.assertEqual(b'WW\nw', results)

        # Octal behavior in regex grabs \127 before it evaluates \27, so we must match that behavior
        pattern = regex.compile('Test')
        expand = bregex.compile_replace(pattern, r'\127\666\C\167\666\n\E\l\127\c\666')
        results = expand(pattern.match('Test'))
        self.assertEqual('W\u01b6W\u01b5\nw\u01b5', results)

        pattern = regex.compile(b'Test')
        expand = bregex.compile_replace(pattern, br'\127\C\167\n\E\l\127\c')
        results = expand(pattern.match(b'Test'))
        self.assertEqual(b'WW\nw', results)

        # Null should pass through
        pattern = regex.compile('Test')
        expand = bregex.compile_replace(pattern, r'\0\00\000')
        results = expand(pattern.match('Test'))
        self.assertEqual('\x00\x00\x00', results)

        pattern = regex.compile(b'Test')
        expand = bregex.compile_replace(pattern, br'\0\00\000')
        results = expand(pattern.match(b'Test'))
        self.assertEqual(b'\x00\x00\x00', results)

        pattern = regex.compile('Test')
        expandf = bregex.compile_replace(pattern, r'\0\00\000', bregex.FORMAT)
        results = expandf(pattern.match('Test'))
        self.assertEqual('\x00\x00\x00', results)

        pattern = regex.compile(b'Test')
        expandf = bregex.compile_replace(pattern, br'\0\00\000', bregex.FORMAT)
        results = expand(pattern.match(b'Test'))
        self.assertEqual(b'\x00\x00\x00', results)


class TestExceptions(unittest.TestCase):
    """Test Exceptions."""

    def test_immutable(self):
        """Test immutable object."""

        pattern = regex.compile('test')
        replace = bregex.compile_replace(pattern, "whatever")
        with pytest.raises(AttributeError):
            replace.use_format = True

    def test_incomplete_replace_byte(self):
        """Test incomplete byte group."""

        p = bregex.compile_search(r'test')
        with pytest.raises(SyntaxError):
            bregex.compile_replace(p, r'Replace \x fail!')

    def test_switch_from_format_auto(self):
        """Test a switch from auto to manual format."""

        text_pattern = r"(this )(.+?)(format capture )(groups)(!)"
        pattern = regex.compile(text_pattern)

        with pytest.raises(ValueError) as excinfo:
            bregex.compile_replace(
                pattern, r'{}{}{manual}', bregex.FORMAT
            )

        assert "Cannot switch to manual format during auto format!" in str(excinfo.value)

    def test_switch_from_format_manual(self):
        """Test a switch from manual to auto format."""

        text_pattern = r"(this )(.+?)(format capture )(groups)(!)"
        pattern = regex.compile(text_pattern)

        with pytest.raises(ValueError) as excinfo:
            bregex.compile_replace(
                pattern, r'{manual}{}{}', bregex.FORMAT
            )

        assert "Cannot switch to auto format during manual format!" in str(excinfo.value)

    def test_format_bad_capture(self):
        """Test a bad capture."""

        text_pattern = r"(\w)+"
        pattern = regex.compile(text_pattern)

        with pytest.raises(TypeError):
            bregex.subf(
                pattern, r'{1[0o3f]}', 'test'
            )

    def test_format_bad_capture_range(self):
        """Test a bad capture."""

        text_pattern = r"(\w)+"
        pattern = regex.compile(text_pattern)
        expand = bregex.compile_replace(
            pattern, r'{1[37]}', bregex.FORMAT
        )

        with pytest.raises(IndexError):
            expand(pattern.match('text'))

    def test_require_compiled_pattern(self):
        """Test a bad capture."""

        with pytest.raises(TypeError) as excinfo:
            bregex.compile_replace(
                r'\w+', r'\1'
            )

        assert "Pattern must be a compiled regular expression!" in str(excinfo.value)

    def test_none_match(self):
        """Test None match."""

        pattern = regex.compile("test")
        expand = bregex.compile_replace(pattern, "replace")
        m = pattern.match('wrong')

        with pytest.raises(ValueError) as excinfo:
            expand(m)

        assert "Match is None!" in str(excinfo.value)

    def test_search_flag_on_compiled(self):
        """Test when a compile occurs on a compiled object with flags passed."""

        pattern = bregex.compile_search("test")

        with pytest.raises(ValueError) as excinfo:
            pattern = bregex.compile_search(pattern, bregex.I)

        assert "Cannot process flags argument with a compiled pattern!" in str(excinfo.value)

    def test_bad_value_search(self):
        """Test when the search value is bad."""

        with pytest.raises(TypeError) as excinfo:
            bregex.compile_search(None)

        assert "Not a string or compiled pattern!" in str(excinfo.value)

    def test_relace_flag_on_compiled(self):
        """Test when a compile occurs on a compiled object with flags passed."""

        pattern = regex.compile('test')
        replace = bregex.compile_replace(pattern, "whatever")

        with pytest.raises(ValueError) as excinfo:
            replace = bregex.compile_replace(pattern, replace, bregex.FORMAT)

        assert "Cannot process flags argument with a ReplaceTemplate!" in str(excinfo.value)

    def test_relace_flag_on_template(self):
        """Test when a compile occurs on a template with flags passed."""

        pattern = regex.compile('test')
        template = _bregex_parse._ReplaceParser().parse(pattern, 'whatever')

        with pytest.raises(ValueError) as excinfo:
            bregex.compile_replace(pattern, template, bregex.FORMAT)

        assert "Cannot process flags argument with a ReplaceTemplate!" in str(excinfo.value)

    def test_bad_pattern_in_replace(self):
        """Test when a bad pattern is passed into replace."""

        with pytest.raises(TypeError) as excinfo:
            bregex.compile_replace(None, "whatever", bregex.FORMAT)

        assert "Pattern must be a compiled regular expression!" in str(excinfo.value)

    def test_bad_hash(self):
        """Test when pattern hashes don't match."""

        pattern = regex.compile('test')
        replace = bregex.compile_replace(pattern, 'whatever')
        pattern2 = regex.compile('test', regex.I)

        with pytest.raises(ValueError) as excinfo:
            bregex.compile_replace(pattern2, replace)

        assert "Pattern hash doesn't match hash in compiled replace!" in str(excinfo.value)

    def test_sub_wrong_replace_type(self):
        """Test sending wrong type into `sub`, `subn`."""

        pattern = regex.compile('test')
        replace = bregex.compile_replace(pattern, 'whatever', bregex.FORMAT)

        with pytest.raises(ValueError) as excinfo:
            bregex.sub(pattern, replace, 'test')

        assert "Compiled replace cannot be a format object!" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            bregex.subn(pattern, replace, 'test')

        assert "Compiled replace cannot be a format object!" in str(excinfo.value)

    def test_sub_wrong_replace_format_type(self):
        """Test sending wrong format type into `sub`, `subn`."""

        pattern = regex.compile('test')
        replace = bregex.compile_replace(pattern, 'whatever')

        with pytest.raises(ValueError) as excinfo:
            bregex.subf(pattern, replace, 'test')

        assert "Compiled replace is not a format object!" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            bregex.subfn(pattern, replace, 'test')

        assert "Compiled replace is not a format object!" in str(excinfo.value)

    def test_expand_wrong_values(self):
        """Test `expand` with wrong values."""

        pattern = regex.compile('test')
        replace = bregex.compile_replace(pattern, 'whatever', bregex.FORMAT)
        m = pattern.match('test')

        with pytest.raises(ValueError) as excinfo:
            bregex.expand(m, replace)

        assert "Replace should not be compiled as a format replace!" in str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            bregex.expand(m, 0)

        assert "Expected string, buffer, or compiled replace!" in str(excinfo.value)

    def test_expandf_wrong_values(self):
        """Test `expand` with wrong values."""

        pattern = regex.compile('test')
        replace = bregex.compile_replace(pattern, 'whatever')
        m = pattern.match('test')

        with pytest.raises(ValueError) as excinfo:
            bregex.expandf(m, replace)

        assert "Replace not compiled as a format replace" in str(excinfo.value)

        with pytest.raises(TypeError) as excinfo:
            bregex.expandf(m, 0)

        assert "Expected string, buffer, or compiled replace!" in str(excinfo.value)

    def test_compile_with_function(self):
        """Test that a normal function cannot compile."""

        def repl(m):
            """Replacement function."""

            return "whatever"

        pattern = regex.compile('test')

        with pytest.raises(TypeError) as excinfo:
            bregex.compile_replace(pattern, repl)

        assert "Not a valid type!" in str(excinfo.value)

    def test_octal_fail(self):
        """Test that octal fails properly."""

        pattern = regex.compile(b'Test')

        with pytest.raises(ValueError) as excinfo:
            bregex.compile_replace(pattern, br'\666')

        assert "octal escape value outside of range 0-0o377!" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            bregex.compile_replace(pattern, br'\C\666\E')

        assert "octal escape value outside of range 0-0o377!" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            bregex.compile_replace(pattern, br'\c\666')

        assert "octal escape value outside of range 0-0o377!" in str(excinfo.value)

    def test_timeout(self):
        """Test timeout."""

        def fast_replace(m):
            """Fast replace."""
            return 'X'

        def slow_replace(m):
            start = time.time()
            while True:
                elapsed = time.time() - start
                if elapsed >= 0.5:
                    break
            return 'X'

        self.assertEqual(regex.sub(r'[a-z]', fast_replace, 'abcdef', timeout=2), 'XXXXXX')

        with pytest.raises(TimeoutError) as excinfo:
            regex.sub(r'[a-z]', slow_replace, 'abcdef', timeout=2)

        assert "regex timed out" in str(excinfo.value)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    def test_match(self):
        """Test that `match` works."""

        m = bregex.match(r'This is a test for match!', "This is a test for match!")
        self.assertTrue(m is not None)

        p = bregex.compile(r'This is a test for match!')
        m = p.match("This is a test for match!")
        self.assertTrue(m is not None)

    def test_fullmatch(self):
        """Test that `fullmatch` works."""

        m = bregex.fullmatch(r'This is a test for match!', "This is a test for match!")
        self.assertTrue(m is not None)

        p = bregex.compile(r'This is a test for match!')
        m = p.fullmatch("This is a test for match!")
        self.assertTrue(m is not None)

    def test_search(self):
        """Test that `search` works."""

        m = bregex.search(r'test', "This is a test for search!")
        self.assertTrue(m is not None)

        p = bregex.compile(r'test')
        m = p.search("This is a test for search!")
        self.assertTrue(m is not None)

    def test_split(self):
        """Test that `split` works."""

        self.assertEqual(
            bregex.split(r'\W+', "This is a test for split!"),
            ["This", "is", "a", "test", "for", "split", ""]
        )

        p = bregex.compile(r'\W+')
        self.assertEqual(
            p.split("This is a test for split!"),
            ["This", "is", "a", "test", "for", "split", ""]
        )

    def test_splititer(self):
        """Test that `split` works."""

        array = []
        for x in bregex.splititer(r'\W+', "This is a test for split!"):
            array.append(x)

        self.assertEqual(array, ["This", "is", "a", "test", "for", "split", ""])

        array = []
        p = bregex.compile(r'\W+')
        for x in p.splititer("This is a test for split!"):
            array.append(x)

        self.assertEqual(array, ["This", "is", "a", "test", "for", "split", ""])

    def test_sub(self):
        """Test that `sub` works."""

        self.assertEqual(
            bregex.sub(r'tset', 'test', r'This is a tset for sub!'),
            "This is a test for sub!"
        )

        p = bregex.compile(r'tset')
        self.assertEqual(
            p.sub(r'test', r'This is a tset for sub!'),
            "This is a test for sub!"
        )

    def test_compiled_sub(self):
        """Test that compiled search and replace works."""

        pattern = bregex.compile_search(r'tset')
        replace = bregex.compile_replace(pattern, 'test')

        self.assertEqual(
            bregex.sub(pattern, replace, 'This is a tset for sub!'),
            "This is a test for sub!"
        )

        p = bregex.compile(r'tset')
        replace = p.compile('test')
        self.assertEqual(
            p.sub(replace, 'This is a tset for sub!'),
            "This is a test for sub!"
        )

    def test_subn(self):
        """Test that `subn` works."""

        self.assertEqual(
            bregex.subn(r'tset', 'test', r'This is a tset for subn! This is a tset for subn!'),
            ('This is a test for subn! This is a test for subn!', 2)
        )

        p = bregex.compile(r'tset')
        self.assertEqual(
            p.subn('test', r'This is a tset for subn! This is a tset for subn!'),
            ('This is a test for subn! This is a test for subn!', 2)
        )

    def test_subf(self):
        """Test that `subf` works."""

        self.assertEqual(
            bregex.subf(r'(t)(s)(e)(t)', '{1}{3}{2}{4}', r'This is a tset for subf!'),
            "This is a test for subf!"
        )

        p = bregex.compile(r'(t)(s)(e)(t)')
        self.assertEqual(
            p.subf('{1}{3}{2}{4}', r'This is a tset for subf!'),
            "This is a test for subf!"
        )

    def test_subfn(self):
        """Test that `subfn` works."""

        self.assertEqual(
            bregex.subfn(r'(t)(s)(e)(t)', '{1}{3}{2}{4}', r'This is a tset for subfn! This is a tset for subfn!'),
            ('This is a test for subfn! This is a test for subfn!', 2)
        )

        p = bregex.compile(r'(t)(s)(e)(t)')
        self.assertEqual(
            p.subfn('{1}{3}{2}{4}', r'This is a tset for subfn! This is a tset for subfn!'),
            ('This is a test for subfn! This is a test for subfn!', 2)
        )

    def test_findall(self):
        """Test that `findall` works."""

        self.assertEqual(
            bregex.findall(r'\w+', 'This is a test for findall!'),
            ["This", "is", "a", "test", "for", "findall"]
        )

        p = bregex.compile(r'\w+')
        self.assertEqual(
            p.findall('This is a test for findall!'),
            ["This", "is", "a", "test", "for", "findall"]
        )

    def test_finditer(self):
        """Test that `finditer` works."""

        count = 0
        for m in bregex.finditer(r'\w+', 'This is a test for finditer!'):
            count += 1

        self.assertEqual(count, 6)

        count = 0
        p = bregex.compile(r'\w+')
        for m in p.finditer('This is a test for finditer!'):
            count += 1

        self.assertEqual(count, 6)

    def test_expand(self):
        """Test that `expand` works."""

        pattern = bregex.compile_search(r'(This is a test for )(match!)')
        m = bregex.match(pattern, "This is a test for match!")
        self.assertEqual(
            bregex.expand(m, r'\1\C\2\E'),
            'This is a test for MATCH!'
        )

        replace = bregex.compile_replace(pattern, r'\1\C\2\E')
        self.assertEqual(
            bregex.expand(m, replace),
            'This is a test for MATCH!'
        )

    def test_expandf(self):
        """Test that `expandf` works."""

        pattern = bregex.compile_search(r'(This is a test for )(match!)')
        m = bregex.match(pattern, "This is a test for match!")
        self.assertEqual(
            bregex.expandf(m, r'{1}\C{2}\E'),
            'This is a test for MATCH!'
        )

        replace = bregex.compile_replace(pattern, r'{1}\C{2}\E', bregex.FORMAT)
        self.assertEqual(
            bregex.expandf(m, replace),
            'This is a test for MATCH!'
        )

    def test_auto_compile_off(self):
        """Test auto compile off."""

        p = bregex.compile('(test)s', auto_compile=False)
        self.assertTrue(p.match('tests') is not None)

        with pytest.raises(AttributeError):
            p.subf(r'{1}', 'tests')

        replace = p.compile(r'{1}')
        with pytest.raises(ValueError):
            p.subf(replace, 'tests')

        replace = p.compile(r'{1}', bregex.FORMAT)
        self.assertEqual(p.subf(replace, 'tests'), 'test')

        self.assertEqual(p.sub(r'\ltest', 'tests'), r'\ltest')
