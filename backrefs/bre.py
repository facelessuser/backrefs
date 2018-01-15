r"""
Backrefs re.

Add the ability to use the following backrefs with re:

 - `\l`                                                       - Lowercase character class (search)
 - `\c`                                                       - Uppercase character class (search)
 - `\L`                                                       - Inverse of lowercase character class (search)
 - `\C`                                                       - Inverse of uppercase character class (search)
 - `\Q` and `\Q...\E`                                         - Escape/quote chars (search)
 - `\c` and `\C...\E`                                         - Uppercase char or chars (replace)
 - `\l` and `\L...\E`                                         - Lowercase char or chars (replace)
 - `[:ascii:]`                                                - Posix style classes (search)
 - `[:^ascii:]`                                               - Inverse Posix style classes (search)
 - `\p{Lu}` and \p{Letter} and `\p{gc=Uppercase_Letter}`      - Unicode properties (search Unicode)
 - `\p{block=Basic_Latin}` and `\p{InBasic_Latin}`            - Unicode block properties (search Unicode)
 - `\P{Lu}` and `\P{Letter}` and `\P{gc=Uppercase_Letter}`    - Inverse Unicode properties (search Unicode)
 - `\p{^Lu}` and `\p{^Letter}` and `\p{^gc=Uppercase_Letter}` - Inverse Unicode properties (search Unicode)
 - `\N{Black Club Suit}`                                      - Unicode character by name (search & replace)

Note
=========
 -  Various Unicode properties can be specified for `\p` or `\P`. They can also be placed in character groups,
    but you have to specify them separately.

    So the following is okay: `r"[\p{Lu}\p{Ll}]"` or `r"[\p{L}]"` etc.
    The following is *not* okay: `r"[\p{Lul}]"` or `r"[\p{Lu Ll}]"` etc.

 -  Unicode names can be specified in groups as well: `r"[\N{black club suit}]"`.

 -  Your search pattern must be a Unicode string in order to use Unicode property back references,
    but you do *not* have to use `re.UNICODE`.

 -  `\l`, `\L`, `\c`, and `\C` in searches will be ASCII ranges unless `re.UNICODE` is used.  This is to
    give some consistency with re's `\w`, `\W`, `\b`, `\B`, `\d`, `\D`, `\s` and `\S`. Some POSIX classes will
    also be affected.  See docs for more info.

Compiling
=========

~~~.py3
pattern = compile_search(r'somepattern', flags)
replace = compile_replace(pattern, r'\1 some replace pattern')
~~~

Usage
=========
Recommended to use compiling.  Assuming the above compiling:

~~~.py3
    text = pattern.sub(replace, 'sometext')
~~~

--or--

~~~.py3
    m = pattern.match('sometext')
    if m:
        text = replace(m)  # similar to m.expand(template)
~~~

Licensed under MIT
Copyright (c) 2011 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
import sys
import sre_parse
import functools
import re
import unicodedata
from collections import namedtuple
from . import common_tokens as ctok
from . import compat
from . import uniprops

MAXUNICODE = sys.maxunicode
NARROW = sys.maxunicode == 0xFFFF

# Expose some common re flags and methods to
# save having to import re and backrefs libs
DEBUG = re.DEBUG
I = re.I
IGNORECASE = re.IGNORECASE
L = re.L
LOCALE = re.LOCALE
M = re.M
MULTILINE = re.MULTILINE
S = re.S
DOTALL = re.DOTALL
U = re.U
UNICODE = re.UNICODE
X = re.X
VERBOSE = re.VERBOSE
if compat.PY3:
    A = re.A
    ASCII = re.ASCII
escape = re.escape
purge = re.purge
RE_TYPE = type(re.compile('', 0))

# Replace flags
FORMAT = 1

# Case upper or lower
_UPPER = 0
_LOWER = 1

_SEARCH_ASCII = re.ASCII if compat.PY3 else 0

# Unicode string related references
tokens = {
    "re_posix": re.compile(r'(?i)\[:(?:\\.|[^\\:}]+)+:\]', _SEARCH_ASCII),
    "re_comments": re.compile(r'\(\?\#[^)]*\)', _SEARCH_ASCII),
    "re_flags": re.compile((r'\(\?([aiLmsux]+)\)' if compat.PY3 else r'\(\?([iLmsux]+)\)'), _SEARCH_ASCII),
    "re_uniprops": re.compile(r'(?:p|P)(?:\{(?:\\.|[^\\}]+)+\}|[A-Z])?', _SEARCH_ASCII),
    "re_named_props": re.compile(r'N(?:\{[\w ]+\})?', _SEARCH_ASCII),
    "re_property_strip": re.compile(r'[\-_ ]', _SEARCH_ASCII),
    "re_property_gc": re.compile(
        r'''(?x)
        (?:((?:\\.|[^\\}]+)+?)[=:])?
        ((?:\\.|[^\\}]+)+)
        ''',
        _SEARCH_ASCII
    ),
    "replace_group_ref": re.compile(
        r'''(?x)
        (\\)|
        (
            [0-7]{3}|
            [1-9][0-9]?|
            [cClLEabfrtnv]|
            g(?:<(?:[a-zA-Z]+[a-zA-Z\d_]*|0+|0*[1-9][0-9]?)>)?|
            U(?:[0-9a-fA-F]{8})?|
            u(?:[0-9a-fA-F]{4})?|
            x(?:[0-9a-fA-F]{2})?|
            N(?:\{[\w ]+\})?
        )
        ''',
        _SEARCH_ASCII
    ),
    "binary_replace_group_ref": re.compile(
        r'''(?x)
        (\\)|
        (
            [0-7]{3}|
            [1-9][0-9]?|
            [cClLEabfrtnv]|
            g(?:<(?:[a-zA-Z]+[a-zA-Z\d_]*|0+|0*[1-9][0-9]?)>)?|
            x(?:[0-9a-fA-F]{2})?
        )
        ''',
        _SEARCH_ASCII
    ),
    "format_replace_ref": re.compile(
        r'''(?x)
        (\\)|
        (
            [cClLEabfrtnv]|
            U(?:[0-9a-fA-F]{8})?|
            u(?:[0-9a-fA-F]{4})?|
            x(?:[0-9a-fA-F]{2})?|
            [0-7]{1,3}|
            (
                g(?:<(?:[a-zA-Z]+[a-zA-Z\d_]*|0+|0*[1-9][0-9]?)>)?
            )|
            N(?:\{[\w ]+\})?
        )|
        (\{)''',
        _SEARCH_ASCII
    ),
    "binary_format_replace_ref": re.compile(
        r'''(?x)
        (\\)|
        (
            [cClLEabfrtnv]|
            [0-7]{1,3}|
            x(?:[0-9a-fA-F]{2})?|
            (
                g(?:<(?:[a-zA-Z]+[a-zA-Z\d_]*|0+|0*[1-9][0-9]?)>)?
            )
        )|
        (\{)''',
        _SEARCH_ASCII
    ),
    "format_replace_group": re.compile(
        r'(\{{2}|\}{2})|(\{(?:[a-zA-Z]+[a-zA-Z\d_]*|0*(?:[1-9][0-9]?)?)?(?:\[[^\]]+\])?\})',
        _SEARCH_ASCII
    ),
    "uni_prop": "p",
    "inverse_uni_prop": "P",
    "ascii_lower": 'lower',
    "ascii_upper": 'upper',
    "ascii_flag": "a",
    "new_refs": ("e", "l", "L", "c", "C", "p", "P", "N", "Q", "E"),
    "binary_new_refs": ("e", "l", "L", "c", "C", "Q", "E")
}


class RetryException(Exception):
    """Retry exception."""


class GlobalRetryException(Exception):
    """Global retry exception."""


# Break apart template patterns into char tokens
class ReplaceTokens(compat.Tokens):
    """Preprocess replace tokens."""

    def __init__(self, string, use_format=False, is_binary=False):
        """Initialize."""

        self.string = string
        self.binary = is_binary

        ctokens = ctok.tokens

        self.use_format = use_format
        if self.binary:
            if use_format:
                self._replace_ref = tokens["binary_format_replace_ref"]
            else:
                self._replace_ref = tokens["binary_replace_group_ref"]
        else:
            if use_format:
                self._replace_ref = tokens["format_replace_ref"]
            else:
                self._replace_ref = tokens["replace_group_ref"]
        self._format_replace_group = tokens["format_replace_group"]
        self._unicode_narrow = ctokens["unicode_narrow"]
        self._unicode_wide = ctokens["unicode_wide"]
        self._hex = ctokens["hex"]
        self._group = ctokens["group"]
        self._unicode_name = ctokens["unicode_name"]
        self._long_replace_refs = ctokens["long_replace_refs"]
        self._lc_bracket = ctokens["lc_bracket"]
        self._rc_bracket = ctokens["rc_bracket"]
        self._b_slash = ctokens["b_slash"]
        self.max_index = len(string) - 1
        self.index = 0
        self.current = None

    def __iter__(self):
        """Iterate."""

        return self

    def iternext(self):
        """
        Iterate through characters of the string.

        Count escaped l, L, c, C, E and backslash as a single char.
        """

        if self.index > self.max_index:
            raise StopIteration

        char = self.string[self.index]
        if char == self._b_slash:
            m = self._replace_ref.match(self.string, self.index + 1)
            if m:
                ref = m.group(0)
                if len(ref) == 1 and ref in self._long_replace_refs:
                    if ref == self._hex:
                        raise SyntaxError('Format for byte is \\xXX!')
                    elif ref == self._group:
                        raise SyntaxError('Format for group is \\g<group_name_or_index>!')
                    elif ref == self._unicode_name:
                        raise SyntaxError('Format for Unicode name is \\N{name}!')
                    elif ref == self._unicode_narrow:  # pragma: no cover
                        raise SyntaxError('Format for Unicode is \\uXXXX!')
                    elif ref == self._unicode_wide:  # pragma: no cover
                        raise SyntaxError('Format for wide Unicode is \\UXXXXXXXX!')
                if self.use_format and (m.group(3) or m.group(4)):
                    char += self._b_slash
                    self.index -= 1
                if not self.use_format or not m.group(4):
                    char += m.group(1) if m.group(1) else m.group(2)
        elif self.use_format and char in (self._lc_bracket, self._rc_bracket):
            m = self._format_replace_group.match(self.string, self.index)
            if m:
                if m.group(2):
                    char = m.group(2)
                else:
                    self.index += 1
            else:
                raise ValueError("Single unmatched curly bracket!")

        self.index += len(char)
        self.current = char
        return self.current


class SearchTokens(compat.Tokens):
    """Preprocess replace tokens."""

    def __init__(self, string, is_binary=False):
        """Initialize."""

        self.string = string
        self.binary = is_binary

        ctokens = ctok.tokens

        self._re_uniprops = tokens["re_uniprops"]
        self._re_named_props = tokens["re_named_props"]
        self._re_posix = tokens["re_posix"]
        self._unicode_name = ctokens["unicode_name"]
        self._re_flags = tokens["re_flags"]
        self._re_comments = tokens["re_comments"]
        self._uni_prop = tokens["uni_prop"]
        self._inverse_uni_prop = tokens["inverse_uni_prop"]

        self.max_index = len(string) - 1
        self.index = 0
        self.current = None

    def __iter__(self):
        """Iterate."""

        return self

    def rewind(self, index):
        """Rewind."""

        self.index = index

    def get_flags(self):
        """Get flags."""

        text = None
        m = self._re_flags.match(self.string, self.index - 1)
        if m:
            text = m.group(0)
            self.index = m.end(0)
            self.current = text
        return text

    def get_comments(self):
        """Get comments."""

        text = None
        m = self._re_comments.match(self.string, self.index - 1)
        if m:
            self.index = m.end(0)
            text = m.group(0)
            self.current = text
        return text

    def get_posix(self):
        """Get POSIX."""

        text = None
        m = self._re_posix.match(self.string, self.index - 1)
        if m:
            self.index = m.end(0)
            text = m.group(0)[2:-2] if m else None
            self.current = text
        return text

    def get_named_property(self):
        """Get named property."""

        text = None
        m = self._re_named_props.match(self.string, self.index - 1)
        if m:
            text = m.group(0)
            if text == self._unicode_name:
                raise SyntaxError('Format for Unicode name is \\N{name}!')
            self.index = m.end(0)
            self.current = text
            text = text[1:]
        return text

    def get_unicode_property(self):
        """Get Unicode properties."""

        text = None
        m = self._re_uniprops.match(self.string, self.index - 1)
        if m:
            text = m.group(0)
            if text == self._uni_prop:
                raise SyntaxError('Format for Unicode property is \\p{property} or \\pP!')
            elif text == self._inverse_uni_prop:
                raise SyntaxError('Format for inverse Unicode property is \\P{property} or \\PP!')
            self.index = m.end(0)
            self.current = text
            text = text[1:]
        return text

    def iternext(self):
        """
        Iterate through characters of the string.

        Count escaped l, L, c, C, E and backslash as a single char.
        """

        if self.index > self.max_index:
            raise StopIteration

        char = self.string[self.index]

        self.index += 1
        self.current = char
        return self.current


# Templates
class ReplaceTemplate(object):
    """Pre-replace template."""

    def __init__(self, pattern, template, use_format=False):
        """Initialize."""

        if isinstance(template, compat.binary_type):
            self.binary = True
        else:
            self.binary = False

        ctokens = ctok.tokens

        self._original = template
        self.use_format = use_format
        self._ascii_letters = ctokens["ascii_letters"]
        self._esc_end = ctokens["esc_end"]
        self._end = ctokens["end"]
        self._lc = ctokens["lc"]
        self._ls_bracket = ctokens["ls_bracket"]
        self._lc_bracket = ctokens["lc_bracket"]
        self._lc_span = ctokens["lc_span"]
        self._uc = ctokens["uc"]
        self._uc_span = ctokens["uc_span"]
        self._group = ctokens["group"]
        self._empty = ctokens["empty"]
        self._group_start = ctokens["group_start"]
        self._group_end = ctokens["group_end"]
        self._binary = ctokens["binary"]
        self._octal = ctokens["octal"]
        self._hex = ctokens["hex"]
        self._unicode_name = ctokens['unicode_name']
        self._minus = ctokens["minus"]
        self._zero = ctokens["zero"]
        self._unicode_narrow = ctokens["unicode_narrow"]
        self._unicode_wide = ctokens["unicode_wide"]
        self.end_found = False
        self.group_slots = []
        self.literal_slots = []
        self.result = []
        self.span_stack = []
        self.single_stack = []
        self.slot = 0
        self.manual = False
        self.auto = False
        self.auto_index = 0
        self.pattern_hash = hash(pattern)

        self.parse_template(pattern)

    def parse_template(self, pattern):
        """Parse template."""

        i = ReplaceTokens(
            (self._original.decode('latin-1') if self.binary else self._original),
            use_format=self.use_format,
            is_binary=self.binary
        )
        iter(i)
        self.result = [self._empty]

        for t in i:
            if len(t) > 1:
                if self.use_format and t[0] == self._lc_bracket:
                    self.handle_format_group(t[1:-1].strip())
                else:
                    c = t[1:]
                    first = c[0]
                    if first.isdigit() and (self.use_format or len(c) == 3):
                        value = int(c, 8)
                        if value > 0xFF:
                            if self.binary:
                                # Re fails on octal greater than 0o377 or 0xFF
                                raise ValueError("octal escape value outside of range 0-0o377!")
                            self.result.append(compat.uchr(value))
                        else:
                            self.result.append('\\%03o' % value)
                    elif not self.use_format and (c[0].isdigit() or c[0] == self._group):
                        self.handle_group(t)
                    elif c == self._lc:
                        self.single_case(i, _LOWER)
                    elif c == self._lc_span:
                        self.span_case(i, _LOWER)
                    elif c == self._uc:
                        self.single_case(i, _UPPER)
                    elif c == self._uc_span:
                        self.span_case(i, _UPPER)
                    elif c == self._end:
                        # This is here just as a reminder that \E is ignored
                        pass
                    elif not self.binary and first == self._unicode_name:
                        value = ord(unicodedata.lookup(t[3:-1]))
                        if value <= 0xFF:
                            self.result.append('\\%03o' % value)
                        else:
                            self.result.append(compat.uchr(value))
                    elif (
                        not self.binary and
                        (first == self._unicode_narrow or (not NARROW and first == self._unicode_wide))
                    ):
                        value = int(t[2:], 16)
                        if value <= 0xFF:
                            self.result.append('\\%03o' % value)
                        else:
                            self.result.append(compat.uchr(value))
                    elif first == self._hex:
                        self.result.append('\\%03o' % int(t[2:], 16))
                    else:
                        self.result.append(t)
            else:
                self.result.append(t)

        if len(self.result) > 1:
            self.literal_slots.append(self._empty.join(self.result))
            del self.result[:]
            self.result.append(self._empty)
            self.slot += 1

        if self.binary:
            self._template = self._empty.join(self.literal_slots).encode('latin-1')
        else:
            self._template = self._empty.join(self.literal_slots)
        self.groups, self.literals = sre_parse.parse_template(self._template, pattern)

    def span_case(self, i, case):
        """Uppercase or lowercase the next range of characters until end marker is found."""

        self.span_stack.append(case)
        try:
            t = next(i)
            while t != self._esc_end:
                if len(t) > 1:
                    if self.use_format and t[0] == self._lc_bracket:
                        self.handle_format_group(t[1:-1].strip())
                    else:
                        c = t[1:]
                        first = c[0]
                        if first.isdigit() and (self.use_format or len(c) == 3):
                            value = int(c, 8)
                            if self.binary:
                                if value > 0xFF:
                                    # Re fails on octal greater than 0o377 or 0xFF
                                    raise ValueError("octal escape value outside of range 0-0o377!")
                                text = self.convert_case(compat.uchr(value), case)
                                single = self.get_single_stack()
                                value = ord(self.convert_case(text, single)) if single is not None else ord(text)
                                self.result.append('\\%03o' % value)
                            else:
                                text = self.convert_case(compat.uchr(value), case)
                                single = self.get_single_stack()
                                value = ord(self.convert_case(text, single)) if single is not None else ord(text)
                                if value <= 0xFF:
                                    self.result.append('\\%03o' % value)
                                else:
                                    self.result.append(compat.uchr(value))
                        elif not self.use_format and (c[0].isdigit() or c[0] == self._group):
                            self.handle_group(t)
                        elif c == self._uc:
                            self.single_case(i, _UPPER)
                        elif c == self._lc:
                            self.single_case(i, _LOWER)
                        elif c == self._uc_span:
                            self.span_case(i, _UPPER)
                        elif c == self._lc_span:
                            self.span_case(i, _LOWER)
                        elif not self.binary and first == self._unicode_name:
                            uc = unicodedata.lookup(t[3:-1])
                            text = self.convert_case(uc, case)
                            single = self.get_single_stack()
                            value = ord(self.convert_case(text, single)) if single is not None else ord(text)
                            if value <= 0xFF:
                                self.result.append('\\%03o' % value)
                            else:
                                self.result.append(compat.uchr(value))
                        elif (
                            not self.binary and
                            (first == self._unicode_narrow or (not NARROW and first == self._unicode_wide))
                        ):
                            uc = compat.uchr(int(t[2:], 16))
                            text = self.convert_case(uc, case)
                            single = self.get_single_stack()
                            value = ord(self.convert_case(text, single)) if single is not None else ord(text)
                            if value <= 0xFF:
                                self.result.append('\\%03o' % value)
                            else:
                                self.result.append(compat.uchr(value))
                        elif first == self._hex:
                            hc = chr(int(t[2:], 16))
                            text = self.convert_case(hc, case)
                            single = self.get_single_stack()
                            value = ord(self.convert_case(text, single)) if single is not None else ord(text)
                            self.result.append("\\%03o" % value)
                        else:
                            self.get_single_stack()
                            self.result.append(t)
                elif self.single_stack:
                    single = self.get_single_stack()
                    text = self.convert_case(t, case)
                    if single is not None:
                        self.result.append(self.convert_case(text[0], single) + text[1:])
                else:
                    self.result.append(self.convert_case(t, case))
                if self.end_found:
                    self.end_found = False
                    break
                t = next(i)
        except StopIteration:
            pass
        self.span_stack.pop()

    def convert_case(self, value, case):
        """Convert case."""

        if self.binary:
            cased = []
            for c in value:
                if c in self._ascii_letters:
                    cased.append(c.lower() if case == _LOWER else c.upper())
                else:
                    cased.append(c)
            return self._empty.join(cased)
        else:
            return value.lower() if case == _LOWER else value.upper()

    def single_case(self, i, case):
        """Uppercase or lowercase the next character."""

        self.single_stack.append(case)
        try:
            t = next(i)
            if len(t) > 1:
                if self.use_format and t[0:1] == self._lc_bracket:
                    self.handle_format_group(t[1:-1].strip())
                else:
                    c = t[1:]
                    first = c[0:1]
                    if first.isdigit() and (self.use_format or len(c) == 3):
                        value = int(c, 8)
                        if self.binary:
                            if value > 0xFF:
                                # Re fails on octal greater than 0o377 or 0xFF
                                raise ValueError("octal escape value outside of range 0-0o377!")
                            value = ord(self.convert_case(compat.uchr(value), self.get_single_stack()))
                            self.result.append('\\%03o' % value)
                        else:
                            value = ord(self.convert_case(compat.uchr(value), self.get_single_stack()))
                            if value <= 0xFF:
                                self.result.append('\\%03o' % value)
                            else:
                                self.result.append(compat.uchr(value))
                    elif not self.use_format and (c[0:1].isdigit() or c[0:1] == self._group):
                        self.handle_group(t)
                    elif c == self._uc:
                        self.single_case(i, _UPPER)
                    elif c == self._lc:
                        self.single_case(i, _LOWER)
                    elif c == self._uc_span:
                        self.span_case(i, _UPPER)
                    elif c == self._lc_span:
                        self.span_case(i, _LOWER)
                    elif c == self._end:
                        self.end_found = True
                    elif not self.binary and first == self._unicode_name:
                        uc = unicodedata.lookup(t[3:-1])
                        value = ord(self.convert_case(uc, self.get_single_stack()))
                        if value <= 0xFF:
                            self.result.append('\\%03o' % value)
                        else:
                            self.result.append(compat.uchr(value))
                    elif (
                        not self.binary and
                        (first == self._unicode_narrow or (not NARROW and first == self._unicode_wide))
                    ):
                        uc = compat.uchr(int(t[2:], 16))
                        value = ord(self.convert_case(uc, self.get_single_stack()))
                        if value <= 0xFF:
                            self.result.append('\\%03o' % value)
                        else:
                            self.result.append(compat.uchr(value))
                    elif first == self._hex:
                        hc = chr(int(t[2:], 16))
                        self.result.append(
                            "\\%03o" % ord(self.convert_case(hc, self.get_single_stack()))
                        )
                    else:
                        self.get_single_stack()
                        self.result.append(t)
            else:
                self.result.append(self.convert_case(t, self.get_single_stack()))

        except StopIteration:
            pass

    def get_single_stack(self):
        """Get the correct single stack item to use."""

        single = None
        while self.single_stack:
            single = self.single_stack.pop()
        return single

    def handle_format_group(self, text):
        """Handle groups."""

        capture = -1
        base = 10
        try:
            index = text.index(self._ls_bracket)
            capture = text[index + 1:-1]
            text = text[:index]
            prefix = capture[1:3] if capture[0:1] == self._minus else capture[:2]
            if prefix[0:1] == self._zero:
                char = prefix[-1:]
                if char == self._binary:
                    base = 2
                elif char == self._octal:
                    base = 8
                elif char == self._hex:
                    base = 16
        except ValueError:
            pass

        if not isinstance(capture, int):
            try:
                capture = int(capture, base)
            except ValueError:
                raise ValueError("Capture index must be an integer!")

        # Handle auto or manual format
        if text == self._empty:
            if self.auto:
                text = compat.int2str(self.auto_index)
                self.auto_index += 1
            elif not self.manual and not self.auto:
                self.auto = True
                text = compat.int2str(self.auto_index)
                self.auto_index += 1
            else:
                raise ValueError("Cannot switch to auto format during manual format!")
        elif not self.manual and not self.auto:
            self.manual = True
        elif not self.manual:
            raise ValueError("Cannot switch to manual format during auto format!")

        if len(self.result) > 1:
            self.literal_slots.append(self._empty.join(self.result))
            self.literal_slots.extend([self._group_start, text, self._group_end])
            del self.result[:]
            self.result.append(self._empty)
            self.slot += 1
        else:
            self.literal_slots.extend([self._group_start, text, self._group_end])

        single = self.get_single_stack()

        self.group_slots.append(
            (
                self.slot,
                (
                    self.span_stack[-1] if self.span_stack else None,
                    single,
                    capture
                )
            )
        )
        self.slot += 1

    def handle_group(self, text):
        """Handle groups."""

        if len(self.result) > 1:
            self.literal_slots.append(self._empty.join(self.result))
            self.literal_slots.append(text)
            del self.result[:]
            self.result.append(self._empty)
            self.slot += 1
        else:
            self.literal_slots.append(text)

        single = self.get_single_stack()

        self.group_slots.append(
            (
                self.slot,
                (
                    self.span_stack[-1] if self.span_stack else None,
                    single,
                    -1
                )
            )
        )
        self.slot += 1

    def get_base_template(self):
        """Return the unmodified template before expansion."""

        return self._original

    def get_group_index(self, index):
        """Find and return the appropriate group index."""

        g_index = None
        for group in self.groups:
            if group[0] == index:
                g_index = group[1]
                break
        return g_index

    def get_group_attributes(self, index):
        """Find and return the appropriate group case."""

        g_case = (None, None, -1)
        for group in self.group_slots:
            if group[0] == index:
                g_case = group[1]
                break
        return g_case


class SearchTemplate(object):
    """Search Template."""

    def __init__(self, search, re_verbose=False, re_unicode=None):
        """Initialize."""

        if isinstance(search, compat.binary_type):
            self.binary = True
        else:
            self.binary = False

        ctokens = ctok.tokens

        self._verbose_flag = ctokens["verbose_flag"]
        self._empty = ctokens["empty"]
        self._b_slash = ctokens["b_slash"]
        self._ls_bracket = ctokens["ls_bracket"]
        self._rs_bracket = ctokens["rs_bracket"]
        self._lc_bracket = ctokens["lc_bracket"]
        self._unicode_flag = ctokens["unicode_flag"]
        self._ascii_flag = tokens["ascii_flag"]
        self._end = ctokens["end"]
        self._re_property_strip = tokens['re_property_strip']
        self._re_property_gc = tokens.get('re_property_gc', None)
        self._uni_prop = tokens["uni_prop"]
        self._inverse_uni_prop = tokens["inverse_uni_prop"]
        self._lc = ctokens["lc"]
        self._lc_span = ctokens["lc_span"]
        self._uc = ctokens["uc"]
        self._uc_span = ctokens["uc_span"]
        self._quote = ctokens["quote"]
        self._negate = ctokens["negate"]
        self._ascii_upper = tokens["ascii_upper"]
        self._ascii_lower = tokens["ascii_lower"]
        self._re_flags = tokens["re_flags"]
        self._re_posix = tokens["re_posix"]
        self._nl = ctokens["nl"]
        self._lr_bracket = ctokens["lr_bracket"]
        self._rr_bracket = ctokens["rr_bracket"]
        self._hashtag = ctokens["hashtag"]
        self._unicode_name = ctokens["unicode_name"]
        self._escape = ctokens["escape"]
        self._re_escape = ctokens["re_escape"]
        if self.binary:
            self._new_refs = tokens["binary_new_refs"]
        else:
            self._new_refs = tokens["new_refs"]
        self.search = search
        self.re_verbose = re_verbose
        self.re_unicode = re_unicode

    def process_quotes(self, string):
        """Process quotes."""

        escaped = False
        in_quotes = False
        current = []
        quoted = []
        i = SearchTokens(string, is_binary=self.binary)
        iter(i)
        for t in i:
            if not escaped and t == self._b_slash:
                escaped = True
            elif escaped:
                escaped = False
                if t == self._end:
                    if in_quotes:
                        current.append(escape(self._empty.join(quoted)))
                        quoted = []
                        in_quotes = False
                elif t == self._quote and not in_quotes:
                    in_quotes = True
                elif in_quotes:
                    quoted.extend([self._b_slash, t])
                else:
                    current.extend([self._b_slash, t])
            elif in_quotes:
                quoted.extend(t)
            else:
                current.append(t)

        if in_quotes and escaped:
            quoted.append(self._b_slash)
        elif escaped:
            current.append(self._b_slash)

        if quoted:
            current.append(escape(self._empty.join(quoted)))

        return self._empty.join(current)

    def verbose_comment(self, t, i):
        """Handle verbose comments."""

        current = []
        escaped = False

        try:
            while t != self._nl:
                if not escaped and t == self._b_slash:
                    escaped = True
                    current.append(t)
                elif escaped:
                    escaped = False
                    if t in self._new_refs:
                        current.append(self._b_slash)
                    current.append(t)
                else:
                    current.append(t)
                t = next(i)
        except StopIteration:
            pass

        if t == self._nl:
            current.append(t)
        return current

    def flags(self, text):
        """Analyze flags."""

        retry = False
        if compat.PY3 and self._ascii_flag in text and self.unicode:
            self.unicode = False
            retry = True
        if self._unicode_flag in text and not self.unicode:
            self.unicode = True
            retry = True
        if self._verbose_flag in text and not self.verbose:
            self.verbose = True
        if retry:
            raise GlobalRetryException('Global Retry')

    def reference(self, t, i):
        """Handle references."""

        current = []

        try:
            t = next(i)
        except StopIteration:
            return [t]

        if t == self._escape:
            current.append(self._re_escape)
        elif t == self._lc:
            current.extend(self.letter_case_props(_LOWER, False))
        elif t == self._lc_span:
            current.extend(self.letter_case_props(_LOWER, False, negate=True))
        elif t == self._uc:
            current.extend(self.letter_case_props(_UPPER, False))
        elif t == self._uc_span:
            current.extend(self.letter_case_props(_UPPER, False, negate=True))

        elif t == self._uni_prop:
            text = i.get_unicode_property()
            if text.startswith(self._lc_bracket):
                text = text[1:-1]
            current.extend(self.unicode_props(text, False))
        elif t == self._inverse_uni_prop:
            text = i.get_unicode_property()
            if text.startswith(self._lc_bracket):
                text = text[1:-1]
            current.extend(self.unicode_props(text, False, negate=True))
        elif not self.binary and t == self._unicode_name:
            text = i.get_named_property()[1:-1]
            current.extend(self.unicode_name(text))
        else:
            current.extend([self._b_slash, t])
        return current

    def subgroup(self, t, i):
        """Handle parenthesis."""

        current = []

        # (?flags)
        flags = i.get_flags()
        if flags:
            self.flags(flags[2:-1])
            return [flags]

        # (?#comment)
        comments = i.get_comments()
        if comments:
            return [comments]

        verbose = self.verbose
        # index = i.index
        start = t
        retry = True
        while retry:
            t = start
            retry = False
            current = []
            try:
                while t != self._rr_bracket:
                    if not current:
                        current.append(t)
                    else:
                        current.extend(self.normal(t, i))

                    t = next(i)
            # except RetryException:
            #     i.rewind(index)
            #     retry = True
            except StopIteration:
                pass
        self.verbose = verbose

        if t == self._rr_bracket:
            current.append(t)
        return current

    def char_groups(self, t, i):
        """Handle character groups."""

        current = []
        pos = i.index - 1
        found = False
        escaped = False
        first = None
        found_property = False

        try:
            while True:
                if not escaped and t == self._b_slash:
                    escaped = True
                elif escaped:
                    escaped = False
                    if t == self._escape:
                        current.append(self._re_escape)
                    elif t == self._lc:
                        current.extend(self.letter_case_props(_LOWER, True))
                    elif t == self._lc_span:
                        current.extend(self.letter_case_props(_LOWER, True, negate=True))
                    elif t == self._uc:
                        current.extend(self.letter_case_props(_UPPER, True))
                    elif t == self._uc_span:
                        current.extend(self.letter_case_props(_UPPER, True, negate=True))
                    elif t == self._uni_prop:
                        text = i.get_unicode_property()
                        if text.startswith(self._lc_bracket):
                            text = text[1:-1]
                        current.extend(self.unicode_props(text, True))
                        found_property = True
                    elif t == self._inverse_uni_prop:
                        text = i.get_unicode_property()
                        if text.startswith(self._lc_bracket):
                            text = text[1:-1]
                        current.extend(self.unicode_props(text, True, negate=True))
                        found_property = True
                    elif not self.binary and t == self._unicode_name:
                        text = i.get_named_property()[1:-1]
                        current.extend(self.unicode_name(text))
                    else:
                        current.extend([self._b_slash, t])
                elif t == self._ls_bracket and not found:
                    found = True
                    first = pos
                    current.append(t)
                elif t == self._ls_bracket:
                    posix = i.get_posix()
                    if posix:
                        current.extend(self.posix_props(posix, in_group=True))
                        found_property = True
                        pos = i.index - 2
                    else:
                        current.append(t)
                elif t == self._negate and found and (pos == first + 1):
                    first = pos
                    current.append(t)
                elif t == self._rs_bracket and found and (pos != first + 1):
                    found = False
                    current.append(t)
                    break
                else:
                    current.append(t)
                pos += 1
                t = next(i)
        except StopIteration:
            pass

        if escaped:
            current.append(t)

        # Handle properties that return an empty string.
        # This will occur when a property's values exceed
        # either the Unicode char limit on a narrow system,
        # or the ASCII limit in a byte string pattern.
        if found_property:
            value = self._empty.join(current)
            if value == '[]':
                # We specified some properities, but they are all
                # out of reach.  Therefore we can match nothing.
                current = ['[^%s]' % ('\x00-\xff' if self.binary else uniprops.UNICODE_RANGE)]
            elif value == '[^]':
                current = ['[%s]' % ('\x00-\xff' if self.binary else uniprops.UNICODE_RANGE)]
            else:
                current = [value]

        return current

    def normal(self, t, i):
        """Handle normal chars."""

        current = []

        if t == self._b_slash:
            current.extend(self.reference(t, i))
        elif t == self._lr_bracket:
            current.extend(self.subgroup(t, i))
        elif self.verbose and t == self._hashtag:
            current.extend(self.verbose_comment(t, i))
        elif t == self._ls_bracket:
            current.extend(self.char_groups(t, i))
        else:
            current.append(t)
        return current

    def posix_props(self, prop, in_group=False):
        """
        Insert POSIX properties.

        Posix style properties are not as forgiving
        as Unicode properties.  Case does matter,
        and whitespace and '-' and '_' will not be tolerated.
        """

        try:
            if self.binary or not self.unicode:
                pattern = uniprops.get_posix_property(prop, (uniprops.POSIX_BINARY if self.binary else uniprops.POSIX))
            else:
                pattern = uniprops.get_posix_property(prop, uniprops.POSIX_UNICODE)
        except Exception:
            raise ValueError('Invalid POSIX property!')
        if not in_group and not pattern:
            pattern = '^%s' % ('\x00-\xff' if self.binary else uniprops.UNICODE_RANGE)

        return [pattern]

    def unicode_name(self, name):
        """Insert Unicode value by its name."""

        value = ord(unicodedata.lookup(name))
        return ['\\%03o' % value if value <= 0xFF else compat.uchr(value)]

    def unicode_props(self, props, in_group, negate=False):
        """
        Insert Unicode properties.

        Unicode properties are very forgiving.
        Case doesn't matter and `[ -_]` will be stripped out.
        """

        # 'GC = Some_Unpredictable-Category Name' -> 'gc=someunpredictablecategoryname'
        props = self._re_property_strip.sub(self._empty, props.lower())
        category = None

        # \p{^negated} Strip off the caret after evaluation.
        if props.startswith(self._negate):
            negate = not negate
        if props.startswith(self._negate):
            props = props[1:]

        # Get the property and value.
        # If a property is present and not block,
        # we can assume GC as that is all we support.
        # If we are wrong it will fail.
        m = self._re_property_gc.match(props)
        props = m.group(2)
        if m.group(1):
            if uniprops.is_enum(m.group(1)):
                category = m.group(1)
            elif props in ('y', 'yes', 't', 'true'):
                category = 'binary'
            elif props in ('n', 'no', 'f', 'false'):
                category = 'binary'
                negate = not negate
            else:
                raise ValueError('Invalid Unicode property!')

        v = uniprops.get_unicode_property((self._negate if negate else self._empty) + props, category, self.binary)
        if not in_group:
            if not v:
                v = '^%s' % ('\x00-\xff' if self.binary else uniprops.UNICODE_RANGE)
            v = self._ls_bracket + v + self._rs_bracket
        properties = [v]

        return properties

    def letter_case_props(self, case, in_group, negate=False):
        """Insert letter (ASCII or Unicode) case properties."""

        # Use traditional ASCII upper/lower case unless:
        #    1. The strings fed in are not binary
        #    2. And the the unicode flag was used
        if not in_group:
            v = self.posix_props(
                (self._negate if negate else self._empty) +
                (self._ascii_upper if case == _UPPER else self._ascii_lower),
                in_group=in_group
            )
            v[0] = self._ls_bracket + v[0] + self._rs_bracket
        else:
            v = self.posix_props(
                (self._negate if negate else self._empty) +
                (self._ascii_upper if case == _UPPER else self._ascii_lower),
                in_group=in_group
            )
        return v

    def main_group(self, i):
        """The main group: group 0."""

        current = []
        while True:
            try:
                t = next(i)
                current.extend(self.normal(t, i))
            except StopIteration:
                break
        return current

    def apply(self):
        """Apply search template."""

        self.verbose = bool(self.re_verbose)
        self.unicode = bool(self.re_unicode)
        if compat.PY3:
            self.ascii = self.re_unicode is not None and not self.re_unicode
        else:
            self.ascii = False
        if compat.PY3 and not self.unicode and not self.ascii:
            self.unicode = True

        new_pattern = []
        string = self.process_quotes(self.search.decode('latin-1') if self.binary else self.search)

        i = SearchTokens(string, is_binary=self.binary)
        iter(i)

        retry = True
        while retry:
            retry = False
            try:
                new_pattern = self.main_group(i)
            # except RetryException:
            #     i.rewind(0)
            #     retry = True
            except GlobalRetryException:
                i.rewind(0)
                retry = True

        return self._empty.join(new_pattern).encode('latin-1') if self.binary else self._empty.join(new_pattern)


# Template expander
class ReplaceTemplateExpander(object):
    """Replacement template expander."""

    def __init__(self, match, template):
        """Initialize."""

        self.template = template
        self.index = -1
        self.end_found = False
        self.parent_span = []
        self.match = match

    def expand(self):
        """Using the template, expand the string."""

        sep = self.match.string[:0]
        text = []
        # Expand string
        for x in range(0, len(self.template.literals)):
            index = x
            l = self.template.literals[x]
            if l is None:
                g_index = self.template.get_group_index(index)
                span_case, single_case, capture = self.template.get_group_attributes(index)
                if capture not in (0, -1):
                    raise IndexError("'%d' is out of range!" % capture)
                l = self.match.group(g_index)
                if span_case is not None:
                    if span_case == _LOWER:
                        l = l.lower()
                    else:
                        l = l.upper()
                if single_case is not None:
                    if single_case == _LOWER:
                        l = l[0:1].lower() + l[1:]
                    else:
                        l = l[0:1].upper() + l[1:]
            text.append(l)

        return sep.join(text)


class Replace(namedtuple('Replace', ['func', 'use_format', 'pattern_hash'])):
    """Bre compiled replace object."""

    def __call__(self, *args, **kwargs):
        """Call."""

        return self.func(*args, **kwargs)


def _is_replace(obj):
    """Check if object is a replace object."""

    return isinstance(obj, (ReplaceTemplate, Replace))


def _apply_replace_backrefs(m, repl=None, flags=0):
    """Expand with either the `ReplaceTemplate` or compile on the fly, or return None."""

    if m is None:
        raise ValueError("Match is None!")
    else:
        if isinstance(repl, Replace):
            return repl(m)
        elif isinstance(repl, ReplaceTemplate):
            return ReplaceTemplateExpander(m, repl).expand()
        elif isinstance(repl, (compat.string_type, compat.binary_type)):
            return ReplaceTemplateExpander(m, ReplaceTemplate(m.re, repl, bool(flags & FORMAT))).expand()


def _apply_search_backrefs(pattern, flags=0):
    """Apply the search backrefs to the search pattern."""

    if isinstance(pattern, (compat.string_type, compat.binary_type)):
        re_verbose = bool(VERBOSE & flags)
        re_unicode = None
        if compat.PY3 and bool(ASCII & flags):
            re_unicode = False
        elif bool(UNICODE & flags):
            re_unicode = True
        pattern = SearchTemplate(pattern, re_verbose, re_unicode).apply()
    elif isinstance(pattern, RE_TYPE):
        if flags:
            raise ValueError("Cannot process flags argument with a compiled pattern!")
    else:
        raise TypeError("Not a string or compiled pattern!")
    return pattern


def compile_search(pattern, flags=0):
    """Compile with extended search references."""

    return re.compile(_apply_search_backrefs(pattern, flags), flags)


def compile_replace(pattern, repl, flags=0):
    """Construct a method that can be used as a replace method for `sub`, `subn`, etc."""

    call = None
    if pattern is not None and isinstance(pattern, RE_TYPE):
        if isinstance(repl, (compat.string_type, compat.binary_type)):
            repl = ReplaceTemplate(pattern, repl, bool(flags & FORMAT))
            call = Replace(
                functools.partial(_apply_replace_backrefs, repl=repl), repl.use_format, repl.pattern_hash
            )
        elif isinstance(repl, Replace):
            if flags:
                raise ValueError("Cannot process flags argument with a compiled pattern!")
            if repl.pattern_hash != hash(pattern):
                raise ValueError("Pattern hash doesn't match hash in compiled replace!")
            call = repl
        elif isinstance(repl, ReplaceTemplate):
            if flags:
                raise ValueError("Cannot process flags argument with a ReplaceTemplate!")
            call = Replace(
                functools.partial(_apply_replace_backrefs, repl=repl), repl.use_format, repl.pattern_hash
            )
        else:
            raise TypeError("Not a valid type!")
    else:
        raise TypeError("Pattern must be a compiled regular expression!")
    return call


# Convenience methods like re has, but slower due to overhead on each call.
# It is recommended to use compile_search and compile_replace
def expand(m, repl):
    """Expand the string using the replace pattern or function."""

    if isinstance(repl, (Replace, ReplaceTemplate)):
        if repl.use_format:
            raise ValueError("Replace should not be compiled as a format replace!")
    elif not isinstance(repl, (compat.string_type, compat.binary_type)):
        raise TypeError("Expected string, buffer, or compiled replace!")
    return _apply_replace_backrefs(m, repl)


def expandf(m, format):  # noqa B002
    """Expand the string using the format replace pattern or function."""

    if isinstance(format, (Replace, ReplaceTemplate)):
        if not format.use_format:
            raise ValueError("Replace not compiled as a format replace")
    elif not isinstance(format, (compat.string_type, compat.binary_type)):
        raise TypeError("Expected string, buffer, or compiled replace!")
    return _apply_replace_backrefs(m, format, flags=FORMAT)


def search(pattern, string, flags=0):
    """Apply `search` after applying backrefs."""

    return re.search(_apply_search_backrefs(pattern, flags), string, flags)


def match(pattern, string, flags=0):
    """Apply `match` after applying backrefs."""

    return re.match(_apply_search_backrefs(pattern, flags), string, flags)


def split(pattern, string, maxsplit=0, flags=0):
    """Apply `split` after applying backrefs."""

    return re.split(_apply_search_backrefs(pattern, flags), string, maxsplit, flags)


def findall(pattern, string, flags=0):
    """Apply `findall` after applying backrefs."""

    return re.findall(_apply_search_backrefs(pattern, flags), string, flags)


def finditer(pattern, string, flags=0):
    """Apply `finditer` after applying backrefs."""

    return re.finditer(_apply_search_backrefs(pattern, flags), string, flags)


def sub(pattern, repl, string, count=0, flags=0):
    """Apply `sub` after applying backrefs."""

    is_replace = _is_replace(repl)
    is_string = isinstance(repl, (compat.string_type, compat.binary_type))
    if is_replace and repl.use_format:
        raise ValueError("Compiled replace cannot be a format object!")

    pattern = compile_search(pattern, flags)
    return re.sub(
        pattern, (compile_replace(pattern, repl) if is_replace or is_string else repl), string, count, flags
    )


def subf(pattern, format, string, count=0, flags=0):  # noqa B002
    """Apply `sub` with format style replace."""

    is_replace = _is_replace(format)
    is_string = isinstance(format, (compat.string_type, compat.binary_type))
    if is_replace and not format.use_format:
        raise ValueError("Compiled replace is not a format object!")

    pattern = compile_search(pattern, flags)
    rflags = FORMAT if is_string else 0
    return re.sub(
        pattern, (compile_replace(pattern, format, flags=rflags) if is_replace or is_string else format),
        string, count, flags
    )


def subn(pattern, repl, string, count=0, flags=0):
    """Apply `subn` with format style replace."""

    is_replace = _is_replace(repl)
    is_string = isinstance(repl, (compat.string_type, compat.binary_type))
    if is_replace and repl.use_format:
        raise ValueError("Compiled replace cannot be a format object!")

    pattern = compile_search(pattern, flags)
    return re.subn(
        pattern, (compile_replace(pattern, repl) if is_replace or is_string else repl), string, count, flags
    )

def subfn(pattern, format, string, count=0, flags=0):  # noqa B002
    """Apply `subn` after applying backrefs."""

    is_replace = _is_replace(format)
    is_string = isinstance(format, (compat.string_type, compat.binary_type))
    if is_replace and not format.use_format:
        raise ValueError("Compiled replace is not a format object!")

    pattern = compile_search(pattern, flags)
    rflags = FORMAT if is_string else 0
    return re.subn(
        pattern, (compile_replace(pattern, format, flags=rflags) if is_replace or is_string else format),
        string, count, flags
    )
