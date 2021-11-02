"""
Backrefs Re parser.

Licensed under MIT
Copyright (c) 2011 - 2020 Isaac Muse <isaacmuse@gmail.com>
"""
import re as _re
import copyreg as _copyreg
from . import util as _util
import sre_parse as _sre_parse
import unicodedata as _unicodedata
from . import uniprops as _uniprops
from typing import Generic, Tuple, AnyStr, Optional, Match, List, Any, Dict, Union, Pattern

__all__ = ("ReplaceTemplate",)

_ASCII_LETTERS = frozenset(
    (
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
    )
)
_DIGIT = frozenset(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'))
_OCTAL = frozenset(('0', '1', '2', '3', '4', '5', '6', '7'))
_HEX = frozenset(('a', 'b', 'c', 'd', 'e', 'f', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'))
_LETTERS_UNDERSCORE = _ASCII_LETTERS | frozenset(('_',))
_WORD = _LETTERS_UNDERSCORE | _DIGIT
_STANDARD_ESCAPES = frozenset(('a', 'b', 'f', 'n', 'r', 't', 'v'))
_CURLY_BRACKETS = frozenset(('{', '}'))
_PROPERTY_STRIP = frozenset((' ', '-', '_'))
_PROPERTY = _WORD | _DIGIT | _PROPERTY_STRIP
_GLOBAL_FLAGS = frozenset(('a', 'u', 'L'))
_SCOPED_FLAGS = frozenset(('i', 'm', 's', 'u', 'x'))

_CURLY_BRACKETS_ORD = frozenset((0x7b, 0x7d))

# Case upper or lower
_UPPER = 1
_LOWER = 2

# Format Constants
_BACK_SLASH_TRANSLATION = {
    "\\a": '\a',
    "\\b": '\b',
    "\\f": '\f',
    "\\r": '\r',
    "\\t": '\t',
    "\\n": '\n',
    "\\v": '\v',
    "\\\\": '\\'
}

_FMT_CONV_TYPE = ('a', 'r', 's')


class LoopException(Exception):
    """Loop exception."""


class GlobalRetryException(Exception):
    """Global retry exception."""


class _SearchParser(Generic[AnyStr]):
    """Search Template."""

    _new_refs = ("c", "C", "e", "E", "h", "l", "L", "m", "M", "N", "p", "P", "Q", "R", "X")
    _re_escape = r"\x1b"
    _re_start_wb = r"\b(?=\w)"
    _re_end_wb = r"\b(?<=\w)"
    _line_break = r'(?:\r\n|(?!\r\n)[\n\v\f\r\x85\u2028\u2029])'
    _bytes_line_break = r'(?:\r\n|(?!\r\n)[\n\v\f\r\x85])'
    _grapheme_cluster = r'(?:{}{}*(?!{}))'

    verbose: bool
    unicode: bool
    global_flag_swap: Dict[str, bool]
    temp_global_flag_swap: Dict[str, bool]
    ascii: bool  # noqa: A003
    is_bytes: bool
    search: AnyStr

    def __init__(self, search: AnyStr, re_verbose: bool = False, re_unicode: Optional[bool] = None) -> None:
        """Initialize."""

        if isinstance(search, bytes):
            self.is_bytes = True
        else:
            self.is_bytes = False

        if self.is_bytes:
            self._re_line_break = self._bytes_line_break
        else:
            self._re_line_break = self._line_break
        self.search = search
        self.re_verbose = re_verbose
        self.re_unicode = re_unicode

    def process_quotes(self, text: str) -> str:
        """Process quotes."""

        escaped = False
        in_quotes = False
        current = []
        quoted = []  # type: List[str]
        i = _util.StringIter(text)

        for t in i:
            if not escaped and t == "\\":
                escaped = True
            elif escaped:
                escaped = False
                if t == "E":
                    if in_quotes:
                        current.append(_re.escape("".join(quoted)))
                        quoted = []
                        in_quotes = False
                elif t == "Q" and not in_quotes:
                    in_quotes = True
                elif in_quotes:
                    quoted.extend(["\\", t])
                else:
                    current.extend(["\\", t])
            elif in_quotes:
                quoted.extend(t)
            else:
                current.append(t)

        if in_quotes and escaped:
            quoted.append("\\")
        elif escaped:
            current.append("\\")

        if quoted:
            current.append(_re.escape("".join(quoted)))

        return "".join(current)

    def verbose_comment(self, t: str, i: _util.StringIter) -> List[str]:
        """Handle verbose comments."""

        current = []
        escaped = False

        try:
            while t != "\n":
                if not escaped and t == "\\":
                    escaped = True
                    current.append(t)
                elif escaped:
                    escaped = False
                    if t in self._new_refs:
                        current.append("\\")
                    current.append(t)
                else:
                    current.append(t)
                t = next(i)
        except StopIteration:
            pass

        if t == "\n":
            current.append(t)
        return current

    def flags(self, text: str, scoped: bool = False) -> None:
        """Analyze flags."""

        global_retry = False
        if ('a' in text or 'L' in text) and self.unicode:
            self.unicode = False
            if not scoped:
                self.temp_global_flag_swap["unicode"] = True
                global_retry = True
        elif 'u' in text and not self.unicode and not self.is_bytes:
            self.unicode = True
            if not scoped:
                self.temp_global_flag_swap["unicode"] = True
                global_retry = True
        if '-x' in text and self.verbose:
            self.verbose = False
        elif 'x' in text and not self.verbose:
            self.verbose = True
            if not scoped:
                self.temp_global_flag_swap["verbose"] = True
                global_retry = True
        if global_retry:
            raise GlobalRetryException('Global Retry')

    def get_unicode_property(self, i: _util.StringIter, brackets: bool = False) -> Tuple[str, str]:
        """Get Unicode property."""

        index = i.index
        prop = []
        value = []
        try:
            c = next(i)
            if c.upper() in _ASCII_LETTERS:
                prop.append(c)
            elif not brackets and c != '{' or brackets and c != ':':
                raise SyntaxError("Unicode property missing '{{' at {}!".format(i.index - 1))
            else:
                c = next(i)
                if c == '^':
                    prop.append(c)
                    c = next(i)

                while c not in (':', '=', '}'):
                    if c not in _PROPERTY:
                        raise SyntaxError('Invalid Unicode property character at {}!'.format(i.index - 1))
                    if c not in _PROPERTY_STRIP:
                        prop.append(c)
                    c = next(i)

                if c in (':', '='):
                    skip = False
                    if brackets:
                        is_colon = c == ':'
                        c = next(i)
                        if is_colon and c == ']':
                            # That's the end of the property
                            skip = True
                        end = ':'
                    else:
                        c = next(i)
                        end = '}'

                    # Get the property value
                    if not skip:
                        while c != end:
                            if c not in _PROPERTY:
                                raise SyntaxError('Invalid Unicode property character at {}!'.format(i.index - 1))
                            if c not in _PROPERTY_STRIP:
                                value.append(c)
                            c = next(i)
                        if brackets and c == ':':
                            c = next(i)
                            if c != ']':
                                raise SyntaxError('Invalid Unicode property character at {}!'.format(i.index - 1))
                        if not value:
                            raise SyntaxError('Invalid Unicode property!')

        except StopIteration:
            if brackets:
                raise SyntaxError("Missing or unmatched ':]' at {}!".format(index))
            else:
                raise SyntaxError("Missing or unmatched '{{' at {}!".format(index))

        return ''.join(prop).lower(), ''.join(value).lower()

    def get_named_unicode(self, i: _util.StringIter) -> str:
        """Get Unicode name."""

        index = i.index
        value = []
        try:
            if next(i) != '{':
                raise ValueError("Named Unicode missing '{{' {}!".format(i.index - 1))
            c = next(i)
            while c != '}':
                value.append(c)
                c = next(i)
        except Exception:
            raise SyntaxError("Unmatched '{{' at {}!".format(index))

        return ''.join(value)

    def reference(self, t: str, i: _util.StringIter, in_group: bool = False) -> List[str]:
        """Handle references."""

        current = []

        if not in_group and t == "m":
            current.append(self._re_start_wb)
        elif not in_group and t == "M":
            current.append(self._re_end_wb)
        elif not in_group and t == "R":
            current.append(self._re_line_break)
        elif not in_group and t == "X":
            no_mark = self.unicode_props("^m", None, in_group=False)[0]
            mark = self.unicode_props("m", None, in_group=False)[0]
            current.extend(self._grapheme_cluster.format(no_mark, mark, mark))
        elif t == "e":
            current.append(self._re_escape)
        elif t == "h":
            current.extend(self.unicode_props('blank', None, in_group=in_group))
            if in_group:
                self.found_property = True
        elif t == 'p':
            prop = self.get_unicode_property(i)
            current.extend(self.unicode_props(prop[0], prop[1], in_group=in_group))
            if in_group:
                self.found_property = True
        elif t == 'P':
            prop = self.get_unicode_property(i)
            current.extend(self.unicode_props(prop[0], prop[1], in_group=in_group, negate=True))
            if in_group:
                self.found_property = True
        elif t == "N":
            text = self.get_named_unicode(i)
            current.extend(self.unicode_name(text, in_group))
            if in_group:
                self.found_named_unicode = True
        else:
            current.extend(["\\", t])
        return current

    def get_comments(self, i: _util.StringIter) -> Optional[str]:
        """Get comments."""

        index = i.index
        value = ['(']
        escaped = False
        try:
            c = next(i)
            if c != '?':
                i.rewind(1)
                return None
            value.append(c)
            c = next(i)
            if c != '#':
                i.rewind(2)
                return None
            value.append(c)
            c = next(i)
            while c != ')' or escaped is True:
                if escaped:
                    escaped = False
                elif c == '\\':
                    escaped = True
                value.append(c)
                c = next(i)
            value.append(c)
        except StopIteration:
            raise SyntaxError("Unmatched '(' at {}!".format(index - 1))

        return ''.join(value)

    def get_flags(self, i: _util.StringIter, scoped: bool = False) -> Optional[str]:
        """Get flags."""

        index = i.index
        value = ['(']
        toggle = False
        end = ':' if scoped else ')'
        try:
            c = next(i)
            if c != '?':
                i.rewind(1)
                return None
            value.append(c)
            c = next(i)
            while c != end:
                if toggle:
                    if c not in _SCOPED_FLAGS:
                        raise ValueError('Bad scope')
                    toggle = False
                elif scoped and c == '-':
                    toggle = True
                elif not _util.PY37 and scoped and c in _GLOBAL_FLAGS:
                    raise ValueError("Bad flag")
                elif c not in _GLOBAL_FLAGS and c not in _SCOPED_FLAGS:
                    raise ValueError("Bad flag")
                value.append(c)
                c = next(i)
            value.append(c)
        except Exception:
            i.rewind(i.index - index)
            value = []

        return ''.join(value) if value else None

    def subgroup(self, t: str, i: _util.StringIter) -> List[str]:
        """Handle parenthesis."""

        current = []  # type: List[str]

        # (?flags)
        flags = self.get_flags(i)
        if flags:
            self.flags(flags[2:-1])
            return [flags]

        # (?#comment)
        comments = self.get_comments(i)
        if comments:
            return [comments]

        verbose = self.verbose
        unicode_flag = self.unicode

        # (?flags:pattern)
        flags = self.get_flags(i, True)
        if flags:  # pragma: no cover
            t = flags
            self.flags(flags[2:-1], scoped=True)

        current = []
        try:
            while t != ')':
                if not current:
                    current.append(t)
                else:
                    current.extend(self.normal(t, i))

                t = next(i)
        except StopIteration:
            pass

        # Restore flags after group
        self.verbose = verbose
        self.unicode = unicode_flag

        if t == ")":
            current.append(t)
        return current

    def char_groups(self, t: str, i: _util.StringIter) -> List[str]:
        """Handle character groups."""

        current = []
        pos = i.index - 1
        found = False
        escaped = False
        first = 0
        found_property = False
        self.found_property = False
        self.found_named_unicode = False

        try:
            while True:
                # Prevent POSIX/Unicode class from being part of a range.
                if self.found_property and t == '-':
                    current.append(_re.escape(t))
                    pos += 1
                    t = next(i)
                    self.found_property = False
                    continue
                else:
                    self.found_property = False

                if not escaped and t == "\\":
                    escaped = True
                elif escaped:
                    escaped = False
                    idx = len(current) - 1
                    current.extend(self.reference(t, i, True))
                    if self.found_property:
                        # Prevent Unicode class from being part of a range.
                        if idx >= 0 and current[idx] == '-':
                            current[idx] = _re.escape('-')
                        found_property = True
                elif t == "[" and not found:
                    found = True
                    first = pos
                    current.append(t)
                elif t == "[":
                    index = i.index
                    try:
                        prop = self.get_unicode_property(i, True)  # type: Optional[Tuple[str, str]]
                    except Exception:
                        prop = None
                        i.rewind(i.index - index)
                    if prop is not None:
                        value = self.unicode_props(prop[0], prop[1], in_group=True)
                        if current[-1] == '-':
                            current[-1] = _re.escape('-')
                        current.extend(value)
                        found_property = True
                        pos = i.index - 2
                    else:
                        current.append(t)
                elif t == "^" and found and (pos == first + 1):
                    first = pos
                    current.append(t)
                elif t == "]" and found and (pos != first + 1):
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
        if found_property or self.found_named_unicode:
            temp = "".join(current)
            if temp == '[]':
                # We specified some properties, but they are all
                # out of reach.  Therefore we can match nothing.
                current = ['[^{}]'.format(_uniprops.ASCII_RANGE if self.is_bytes else _uniprops.UNICODE_RANGE)]
            elif temp == '[^]':
                current = ['[{}]'.format(_uniprops.ASCII_RANGE if self.is_bytes else _uniprops.UNICODE_RANGE)]
            else:
                current = [temp]

        return current

    def normal(self, t: str, i: _util.StringIter) -> List[str]:
        """Handle normal chars."""

        current = []

        if t == "\\":
            try:
                t = next(i)
                current.extend(self.reference(t, i))
            except StopIteration:
                current.append(t)
        elif t == "(":
            current.extend(self.subgroup(t, i))
        elif self.verbose and t == "#":
            current.extend(self.verbose_comment(t, i))
        elif t == "[":
            current.extend(self.char_groups(t, i))
        else:
            current.append(t)
        return current

    def unicode_name(self, name: str, in_group: bool = False) -> List[str]:
        """Insert Unicode value by its name."""

        value = ord(_unicodedata.lookup(name))
        if self.is_bytes and value > 0xFF:
            if not in_group:
                return ['[^{}]'.format(_uniprops.ASCII_RANGE if self.is_bytes else _uniprops.UNICODE_RANGE)]
            else:
                return ['']
        return ['\\{:03o}'.format(value) if value <= 0xFF else chr(value)]

    def unicode_props(
        self,
        props: str,
        prop_value: Optional[str],
        in_group: bool = False,
        negate: bool = False
    ) -> List[str]:
        """
        Insert Unicode properties.

        Unicode properties are very forgiving.
        Case doesn't matter and `[ -_]` will be stripped out.
        """

        if props.startswith("^"):
            if negate:
                props = props[1:]
        elif negate:
            props = '^' + props
        if not prop_value and prop_value is not None:
            prop_value = None

        if self.is_bytes:
            mode = _uniprops.MODE_ASCII
        elif not self.unicode:
            mode = _uniprops.MODE_NORMAL
        else:
            mode = _uniprops.MODE_UNICODE

        v = _uniprops.get_unicode_property(props, prop_value, mode)
        if not in_group:
            if not v:
                v = '^{}'.format(_uniprops.ASCII_RANGE if self.is_bytes else _uniprops.UNICODE_RANGE)
            v = "[{}]".format(v)
        properties = [v]

        return properties

    def main_group(self, i: _util.StringIter) -> List[str]:
        """The main group: group 0."""

        current = []
        while True:
            try:
                t = next(i)
                current.extend(self.normal(t, i))
            except StopIteration:
                break
        return current

    def _parse(self, search: str) -> str:
        """Begin parsing."""

        self.verbose = bool(self.re_verbose)
        self.unicode = bool(self.re_unicode)
        self.global_flag_swap = {
            "unicode": ((self.re_unicode is not None) if not _util.PY37 else False),
            "verbose": False
        }
        self.temp_global_flag_swap = {
            "unicode": False,
            "verbose": False
        }
        self.ascii = self.re_unicode is not None and not self.re_unicode
        if not self.unicode and not self.ascii:
            self.unicode = True

        new_pattern = []
        i = _util.StringIter(self.process_quotes(search))

        retry = True
        while retry:
            retry = False
            try:
                new_pattern = self.main_group(i)
            except GlobalRetryException:
                # Prevent a loop of retry over and over for a pattern like ((?u)(?a))
                # or (?-x:(?x))
                if self.temp_global_flag_swap['unicode']:
                    if self.global_flag_swap['unicode']:
                        raise LoopException('Global unicode flag recursion.')
                    else:
                        self.global_flag_swap["unicode"] = True
                if self.temp_global_flag_swap['verbose']:
                    if self.global_flag_swap['verbose']:
                        raise LoopException('Global verbose flag recursion.')
                    else:
                        self.global_flag_swap['verbose'] = True
                self.temp_global_flag_swap = {
                    "unicode": False,
                    "verbose": False
                }
                i.rewind(i.index)
                retry = True
        return "".join(new_pattern)

    def parse(self) -> AnyStr:
        """Apply search template."""

        if isinstance(self.search, bytes):
            return self._parse(self.search.decode('latin-1')).encode('latin-1')
        else:
            return self._parse(self.search)


class _ReplaceParser(Generic[AnyStr]):
    """Pre-replace template."""

    def __init__(self, pattern: Pattern[AnyStr], template: AnyStr, use_format: bool = False) -> None:
        """Initialize."""

        self.pattern = pattern  # type: Pattern[AnyStr]
        self._original = template  # type: AnyStr
        self._template = template  # type: AnyStr
        self.use_format = use_format
        self.end_found = False
        self.group_slots = []  # type: List[Tuple[int, Tuple[Optional[int], Optional[int], Any]]]
        self.literal_slots = []  # type: List[str]
        self.result = []  # type: List[str]
        self.span_stack = []  # type: List[int]
        self.single_stack = []  # type: List[int]
        self.literals = []  # type: List[Optional[AnyStr]]
        self.groups = []  # type: List[Tuple[int, int]]
        self.slot = 0
        self.manual = False
        self.auto = False
        self.auto_index = 0
        self.is_bytes = isinstance(self._original, bytes)

    def parse_format_index(self, text: str) -> Union[int, str]:
        """Parse format index."""

        base = 10
        prefix = text[1:3] if text[0] == "-" else text[:2]
        if prefix[0:1] == "0":
            char = prefix[-1]
            if char == "b":
                base = 2
            elif char == "o":
                base = 8
            elif char == "x":
                base = 16
        try:
            idx = int(text, base)  # type: Union[int, str]
        except Exception:
            idx = text
        return idx

    def get_format(self, c: str, i: _util.StringIter) -> Tuple[str, List[Tuple[int, Any]]]:
        """Get format group."""

        index = i.index
        field = ''
        value = []  # type: List[Tuple[int, Any]]

        try:
            if c == '}':
                value.append((_util.FMT_FIELD, ''))
                value.append((_util.FMT_INDEX, -1))
            else:
                # Field
                temp = []  # type: List[str]
                if c in _LETTERS_UNDERSCORE:
                    # Handle name
                    temp.append(c)
                    c = self.format_next(i)
                    while c in _WORD:
                        temp.append(c)
                        c = self.format_next(i)
                elif c in _DIGIT:
                    # Handle group number
                    temp.append(c)
                    c = self.format_next(i)
                    while c in _DIGIT:
                        temp.append(c)
                        c = self.format_next(i)

                # Try and covert to integer index
                field = ''.join(temp).strip()
                try:
                    value = [(_util.FMT_FIELD, str(int(field, 10)))]
                except ValueError:
                    value = [(_util.FMT_FIELD, field)]
                    pass

                # Attributes and indexes
                count = 0
                while c in ('[', '.'):
                    if c == '[':
                        findex = []
                        sindex = i.index - 1
                        c = self.format_next(i)
                        try:
                            while c != ']':
                                findex.append(c)
                                c = self.format_next(i)
                        except StopIteration:
                            raise SyntaxError("Unmatched '[' at {}".format(sindex - 1))
                        idx = self.parse_format_index(''.join(findex))
                        value.append((_util.FMT_INDEX, idx))
                        c = self.format_next(i)
                    else:
                        if count == 0:
                            value.append((_util.FMT_INDEX, -1))
                        findex = []
                        c = self.format_next(i)
                        while c in _WORD:
                            findex.append(c)
                            c = self.format_next(i)
                        value.append((_util.FMT_ATTR, ''.join(findex)))
                    count += 1

                if count == 0:
                    value.append((_util.FMT_INDEX, -1))

                # Conversion
                if c == '!':
                    c = self.format_next(i)
                    if c not in _FMT_CONV_TYPE:
                        raise SyntaxError("Invalid conversion type at {}!".format(i.index - 1))
                    value.append((_util.FMT_CONV, c))
                    c = self.format_next(i)

                # Format spec
                if c == ':':
                    fill = None  # type: Optional[str]
                    width = []
                    align = None
                    convert = None
                    c = self.format_next(i)

                    if c in ('<', '>', '^'):
                        # Get fill and alignment
                        align = c
                        c = self.format_next(i)
                        if c in ('<', '>', '^'):
                            fill = align
                            align = c
                            c = self.format_next(i)
                    elif c in _DIGIT:
                        # Get Width
                        fill = c
                        c = self.format_next(i)
                        if c in ('<', '>', '^'):
                            align = c
                            c = self.format_next(i)
                        else:
                            width.append(fill)
                            fill = None
                    else:
                        fill = c
                        c = self.format_next(i)
                        if fill == 's' and c == '}':
                            convert = fill
                            fill = None
                        if fill is not None:
                            if c not in ('<', '>', '^'):
                                raise SyntaxError('Invalid format spec char at {}!'.format(i.index - 1))
                            align = c
                            c = self.format_next(i)

                    while c in _DIGIT:
                        width.append(c)
                        c = self.format_next(i)

                    if not align and len(width) and width[0] == '0':
                        raise ValueError("'=' alignment is not supported!")
                    if align and not fill and len(width) and width[0] == '0':
                        fill = '0'

                    if c == 's':
                        convert = c
                        c = self.format_next(i)

                    if not fill:
                        fill = ' '

                    value.append(
                        (
                            _util.FMT_SPEC,
                            (
                                fill.encode('latin-1') if self.is_bytes else fill,
                                align,
                                (int(''.join(width)) if width else 0),
                                convert
                            )
                        )
                    )

            if c != '}':
                raise SyntaxError("Unmatched '{{' at {}".format(index - 1))
        except StopIteration:
            raise SyntaxError("Unmatched '{{' at {}!".format(index - 1))

        return field, value

    def handle_format(self, t: str, i: _util.StringIter) -> None:
        """Handle format."""

        if t == '{':
            t = self.format_next(i)
            if t == '{':
                self.get_single_stack()
                self.result.append(t)
            else:
                field, text = self.get_format(t, i)
                self.handle_format_group(field, text)
        else:
            t = self.format_next(i)
            if t == '}':
                self.get_single_stack()
                self.result.append(t)
            else:
                raise SyntaxError("Unmatched '}}' at {}!".format(i.index - 2))

    def get_octal(self, c: str, i: _util.StringIter) -> Optional[str]:
        """Get octal."""

        index = i.index
        value = []
        zero_count = 0
        try:
            if c == '0':
                for x in range(3):
                    if c != '0':
                        break
                    value.append(c)
                    c = next(i)
            zero_count = len(value)
            if zero_count < 3:
                for x in range(3 - zero_count):
                    if c not in _OCTAL:
                        break
                    value.append(c)
                    c = next(i)
            i.rewind(1)
        except StopIteration:
            pass

        octal_count = len(value)
        if not (self.use_format and octal_count) and not (zero_count and octal_count < 3) and octal_count != 3:
            i.rewind(i.index - index)
            value = []

        return ''.join(value) if value else None

    def parse_octal(self, text: str, i: _util.StringIter) -> None:
        """Parse octal value."""

        value = int(text, 8)
        if value > 0xFF and self.is_bytes:
            # Re fails on octal greater than `0o377` or `0xFF`
            raise ValueError("octal escape value outside of range 0-0o377!")
        else:
            single = self.get_single_stack()
            if self.span_stack:
                text = self.convert_case(chr(value), self.span_stack[-1])
                value = ord(self.convert_case(text, single)) if single is not None else ord(text)
            elif single:
                value = ord(self.convert_case(chr(value), single))
            if self.use_format and value in _CURLY_BRACKETS_ORD:
                self.handle_format(chr(value), i)
            elif value <= 0xFF:
                self.result.append('\\{:03o}'.format(value))
            else:
                self.result.append(chr(value))

    def get_named_unicode(self, i: _util.StringIter) -> str:
        """Get named Unicode."""

        index = i.index
        value = []
        try:
            if next(i) != '{':
                raise SyntaxError("Named Unicode missing '{{' at {}!".format(i.index - 1))
            c = next(i)
            while c != '}':
                value.append(c)
                c = next(i)
        except StopIteration:
            raise SyntaxError("Unmatched '}}' at {}!".format(index))

        return ''.join(value)

    def parse_named_unicode(self, i: _util.StringIter) -> None:
        """Parse named Unicode."""

        value = ord(_unicodedata.lookup(self.get_named_unicode(i)))
        single = self.get_single_stack()
        if self.span_stack:
            text = self.convert_case(chr(value), self.span_stack[-1])
            value = ord(self.convert_case(text, single)) if single is not None else ord(text)
        elif single:
            value = ord(self.convert_case(chr(value), single))
        if self.use_format and value in _CURLY_BRACKETS_ORD:
            self.handle_format(chr(value), i)
        elif value <= 0xFF:
            self.result.append('\\{:03o}'.format(value))
        else:
            self.result.append(chr(value))

    def get_wide_unicode(self, i: _util.StringIter) -> str:
        """Get narrow Unicode."""

        value = []
        for x in range(3):
            c = next(i)
            if c == '0':
                value.append(c)
            else:  # pragma: no cover
                raise SyntaxError('Invalid wide Unicode character at {}!'.format(i.index - 1))

        c = next(i)
        if c in ('0', '1'):
            value.append(c)
        else:  # pragma: no cover
            raise SyntaxError('Invalid wide Unicode character at {}!'.format(i.index - 1))

        for x in range(4):
            c = next(i)
            if c.lower() in _HEX:
                value.append(c)
            else:  # pragma: no cover
                raise SyntaxError('Invalid wide Unicode character at {}!'.format(i.index - 1))
        return ''.join(value)

    def get_narrow_unicode(self, i: _util.StringIter) -> str:
        """Get narrow Unicode."""

        value = []
        for x in range(4):
            c = next(i)
            if c.lower() in _HEX:
                value.append(c)
            else:  # pragma: no cover
                raise SyntaxError('Invalid Unicode character at {}!'.format(i.index - 1))
        return ''.join(value)

    def parse_unicode(self, i: _util.StringIter, wide: bool = False) -> None:
        """Parse Unicode."""

        text = self.get_wide_unicode(i) if wide else self.get_narrow_unicode(i)
        value = int(text, 16)
        single = self.get_single_stack()
        if self.span_stack:
            text = self.convert_case(chr(value), self.span_stack[-1])
            value = ord(self.convert_case(text, single)) if single is not None else ord(text)
        elif single:
            value = ord(self.convert_case(chr(value), single))
        if self.use_format and value in _CURLY_BRACKETS_ORD:
            self.handle_format(chr(value), i)
        elif value <= 0xFF:
            self.result.append('\\{:03o}'.format(value))
        else:
            self.result.append(chr(value))

    def get_byte(self, i: _util.StringIter) -> str:
        """Get byte."""

        value = []
        for x in range(2):
            c = next(i)
            if c.lower() in _HEX:
                value.append(c)
            else:  # pragma: no cover
                raise SyntaxError('Invalid byte character at {}!'.format(i.index - 1))
        return ''.join(value)

    def parse_bytes(self, i: _util.StringIter) -> None:
        """Parse byte."""

        value = int(self.get_byte(i), 16)
        single = self.get_single_stack()
        if self.span_stack:
            text = self.convert_case(chr(value), self.span_stack[-1])
            value = ord(self.convert_case(text, single)) if single is not None else ord(text)
        elif single:
            value = ord(self.convert_case(chr(value), single))
        if self.use_format and value in _CURLY_BRACKETS_ORD:
            self.handle_format(chr(value), i)
        else:
            self.result.append('\\{:03o}'.format(value))

    def get_named_group(self, t: str, i: _util.StringIter) -> str:
        """Get group number."""

        index = i.index
        value = [t]
        try:
            c = next(i)
            if c != "<":
                raise SyntaxError("Group missing '<' at {}!".format(i.index - 1))
            value.append(c)
            c = next(i)
            if c in _DIGIT:
                value.append(c)
                c = next(i)
                while c != '>':
                    if c in _DIGIT:
                        value.append(c)
                    c = next(i)
                value.append(c)
            elif c in _LETTERS_UNDERSCORE:
                value.append(c)
                c = next(i)
                while c != '>':
                    if c in _WORD:
                        value.append(c)
                    c = next(i)
                value.append(c)
            else:
                raise SyntaxError("Invalid group character at {}!".format(i.index - 1))
        except StopIteration:
            raise SyntaxError("Unmatched '<' at {}!".format(index))

        return ''.join(value)

    def get_group(self, t: str, i: _util.StringIter) -> Optional[str]:
        """Get group number."""

        value = []
        try:
            if t in _DIGIT and t != '0':
                value.append(t)
                t = next(i)
                if t in _DIGIT:
                    value.append(t)
                else:
                    i.rewind(1)
        except StopIteration:
            pass
        return ''.join(value) if value else None

    def format_next(self, i: _util.StringIter) -> str:
        """Get next format char."""

        c = next(i)
        return self.format_references(next(i), i) if c == '\\' else c

    def format_references(self, t: str, i: _util.StringIter) -> str:
        """Handle format references."""

        octal = self.get_octal(t, i)
        if octal:
            o = int(octal, 8)
            if o > 0xFF and self.is_bytes:
                # Re fails on octal greater than `0o377` or `0xFF`
                raise ValueError("octal escape value outside of range 0-0o377!")
            value = chr(o)
        elif t in _STANDARD_ESCAPES or t == '\\':
            value = _BACK_SLASH_TRANSLATION['\\' + t]
        elif not self.is_bytes and t == "U":
            value = chr(int(self.get_wide_unicode(i), 16))
        elif not self.is_bytes and t == "u":
            value = chr(int(self.get_narrow_unicode(i), 16))
        elif not self.is_bytes and t == "N":
            value = _unicodedata.lookup(self.get_named_unicode(i))
        elif t == "x":
            value = chr(int(self.get_byte(i), 16))
        else:
            i.rewind(1)
            value = '\\'
        return value

    def reference(self, t: str, i: _util.StringIter) -> None:
        """Handle references."""
        octal = self.get_octal(t, i)
        if t in _OCTAL and octal:
            self.parse_octal(octal, i)
        elif (t in _DIGIT or t == 'g') and not self.use_format:
            group = self.get_group(t, i)
            if not group:
                group = self.get_named_group(t, i)
            self.handle_group('\\' + group)
        elif t in _STANDARD_ESCAPES:
            self.get_single_stack()
            self.result.append('\\' + t)
        elif t == "l":
            self.single_case(i, _LOWER)
        elif t == "L":
            self.span_case(i, _LOWER)
        elif t == "c":
            self.single_case(i, _UPPER)
        elif t == "C":
            self.span_case(i, _UPPER)
        elif t == "E":
            self.end_found = True
        elif not self.is_bytes and t == "U":
            self.parse_unicode(i, True)
        elif not self.is_bytes and t == "u":
            self.parse_unicode(i)
        elif not self.is_bytes and t == "N":
            self.parse_named_unicode(i)
        elif t == "x":
            self.parse_bytes(i)
        elif self.use_format and t in _CURLY_BRACKETS:
            self.result.append('\\\\')
            self.handle_format(t, i)
        elif self.use_format and t == 'g':
            self.result.append('\\\\')
            self.result.append(t)
        else:
            value = '\\' + t
            self.get_single_stack()
            if self.span_stack:
                value = self.convert_case(value, self.span_stack[-1])
            self.result.append(value)

    def _parse_template(self, template: str) -> str:
        """Parse template."""

        self.result = [""]

        i = _util.StringIter(template)

        while True:
            try:
                t = next(i)
                if self.use_format and t in _CURLY_BRACKETS:
                    self.handle_format(t, i)
                elif t == '\\':
                    try:
                        t = next(i)
                        self.reference(t, i)
                    except StopIteration:
                        self.result.append(t)
                        raise
                else:
                    self.result.append(t)

            except StopIteration:
                break

        if len(self.result) > 1:
            self.literal_slots.append("".join(self.result))
            del self.result[:]
            self.result.append("")
            self.slot += 1

        return "".join(self.literal_slots)

    def parse_template(self) -> None:
        """Parse template."""

        if isinstance(self._original, bytes):
            self._template = self._parse_template(self._original.decode('latin-1')).encode('latin-1')
        else:
            self._template = self._parse_template(self._original)

        self.groups, self.literals = _sre_parse.parse_template(self._template, self.pattern)

    def span_case(self, i: _util.StringIter, case: int) -> None:
        """Uppercase or lowercase the next range of characters until end marker is found."""

        # A new \L, \C or \E should pop the last in the stack.
        if self.span_stack:
            self.span_stack.pop()
        if self.single_stack:
            self.single_stack.pop()
        self.span_stack.append(case)
        count = len(self.span_stack)
        self.end_found = False
        try:
            while not self.end_found:
                t = next(i)
                if self.use_format and t in _CURLY_BRACKETS:
                    self.handle_format(t, i)
                elif t == '\\':
                    try:
                        t = next(i)
                        self.reference(t, i)
                    except StopIteration:
                        self.result.append(t)
                        raise
                else:
                    self.result.append(self.convert_case(t, case))
                if self.end_found or count > len(self.span_stack):
                    self.end_found = False
                    break
        except StopIteration:
            pass
        if count == len(self.span_stack):
            self.span_stack.pop()

    def convert_case(self, value: str, case: int) -> str:
        """Convert case."""

        if self.is_bytes:
            cased = []
            for c in value:
                if c in _ASCII_LETTERS:
                    cased.append(c.lower() if case == _LOWER else c.upper())
                else:
                    cased.append(c)
            return "".join(cased)
        else:
            return value.lower() if case == _LOWER else value.upper()

    def single_case(self, i: _util.StringIter, case: int) -> None:
        """Uppercase or lowercase the next character."""

        # Pop a previous case if we have consecutive ones.
        if self.single_stack:
            self.single_stack.pop()
        self.single_stack.append(case)
        try:
            t = next(i)
            if self.use_format and t in _CURLY_BRACKETS:
                self.handle_format(t, i)
            elif t == '\\':
                try:
                    t = next(i)
                    self.reference(t, i)
                except StopIteration:
                    self.result.append(t)
                    raise
            elif self.single_stack:
                this_case = self.get_single_stack()
                if this_case is not None:
                    self.result.append(self.convert_case(t, this_case))
        except StopIteration:
            pass

    def get_single_stack(self) -> Optional[int]:
        """Get the correct single stack item to use."""

        single = None
        while self.single_stack:
            single = self.single_stack.pop()
        return single

    def handle_format_group(self, field: str, text: List[Tuple[int, Any]]) -> None:
        """Handle format group."""

        # Handle auto incrementing group indexes
        if field == '':
            if self.auto:
                field = str(self.auto_index)
                text[0] = (_util.FMT_FIELD, field)
                self.auto_index += 1
            elif not self.manual and not self.auto:
                self.auto = True
                field = str(self.auto_index)
                text[0] = (_util.FMT_FIELD, field)
                self.auto_index += 1
            else:
                raise ValueError("Cannot switch to auto format during manual format!")
        elif not self.manual and not self.auto:
            self.manual = True
        elif not self.manual:
            raise ValueError("Cannot switch to manual format during auto format!")

        self.handle_group(field, tuple(text), True)

    def handle_group(
        self,
        text: str,
        capture: Optional[Tuple[Tuple[int, Any], ...]] = None,
        is_format: bool = False
    ) -> None:
        """Handle groups."""

        if len(self.result) > 1:
            self.literal_slots.append("".join(self.result))
            if is_format:
                self.literal_slots.extend(["\\g<", text, ">"])
            else:
                self.literal_slots.append(text)
            del self.result[:]
            self.result.append("")
            self.slot += 1
        elif is_format:
            self.literal_slots.extend(["\\g<", text, ">"])
        else:
            self.literal_slots.append(text)

        self.group_slots.append(
            (
                self.slot,
                (
                    (self.span_stack[-1] if self.span_stack else None),
                    self.get_single_stack(),
                    (tuple() if self.is_bytes else '') if capture is None else capture
                )
            )
        )
        self.slot += 1

    def get_base_template(self) -> AnyStr:
        """Return the unmodified template before expansion."""

        return self._original

    def parse(self) -> 'ReplaceTemplate[AnyStr]':
        """Parse template."""

        if not isinstance(self.pattern.pattern, type(self._original)):
            raise TypeError('Pattern string type must match replace template string type!')

        self.parse_template()

        return ReplaceTemplate(
            tuple(self.groups),
            tuple(self.group_slots),
            tuple(self.literals),
            hash(self.pattern),
            self.use_format,
            self.is_bytes
        )


class ReplaceTemplate(_util.Immutable, Generic[AnyStr]):
    """Replacement template expander."""

    __slots__ = ("groups", "group_slots", "literals", "pattern_hash", "use_format", "_hash", "_bytes")

    groups: Tuple[Tuple[int, int], ...]
    group_slots: Tuple[Tuple[int, Tuple[Optional[int], Optional[int], Any]], ...]
    literals: Tuple[Optional[AnyStr], ...]
    pattern_hash: int
    use_format: bool
    _hash: int
    _bytes: bool

    def __init__(
        self,
        groups: Tuple[Tuple[int, int], ...],
        group_slots: Tuple[Tuple[int, Tuple[Optional[int], Optional[int], Any]], ...],
        literals: Tuple[Optional[AnyStr], ...],
        pattern_hash: int,
        use_format: bool,
        is_bytes: bool
    ) -> None:
        """Initialize."""

        super().__init__(
            use_format=use_format,
            groups=groups,
            group_slots=group_slots,
            literals=literals,
            pattern_hash=pattern_hash,
            _bytes=is_bytes,
            _hash=hash(
                (
                    type(self),
                    groups, group_slots, literals,
                    pattern_hash, use_format, is_bytes
                )
            )
        )

    def __call__(self, m: Optional[Match[AnyStr]]) -> AnyStr:
        """Call."""

        return self.expand(m)

    def __hash__(self) -> int:
        """Hash."""

        return self._hash

    def __eq__(self, other: Any) -> bool:
        """Equal."""

        return (
            isinstance(other, ReplaceTemplate) and
            self.groups == other.groups and
            self.group_slots == other.group_slots and
            self.literals == other.literals and
            self.pattern_hash == other.pattern_hash and
            self.use_format == other.use_format and
            self._bytes == other._bytes
        )

    def __ne__(self, other: Any) -> bool:
        """Equal."""

        return (
            not isinstance(other, ReplaceTemplate) or
            self.groups != other.groups or
            self.group_slots != other.group_slots or
            self.literals != other.literals or
            self.pattern_hash != other.pattern_hash or
            self.use_format != other.use_format or
            self._bytes != self._bytes
        )

    def __repr__(self) -> str:  # pragma: no cover
        """Representation."""

        return "{}.{}({!r}, {!r}, {!r}, {!r}, {!r})".format(
            self.__module__, self.__class__.__name__,
            self.groups, self.group_slots, self.literals,
            self.pattern_hash, self.use_format
        )

    def _get_group_index(self, index: int) -> int:
        """Find and return the appropriate group index."""

        g_index = 0
        for group in self.groups:
            if group[0] == index:
                g_index = group[1]
                break
        return g_index

    def _get_group_attributes(self, index: int) -> Tuple[Optional[int], Optional[int], Any]:
        """Find and return the appropriate group case."""

        g_case = (None, None, -1)  # type: Tuple[Optional[int], Optional[int], Any]
        for group in self.group_slots:
            if group[0] == index:
                g_case = group[1]
                break
        return g_case

    def expand(self, m: Optional[Match[AnyStr]]) -> AnyStr:
        """Using the template, expand the string."""

        if m is None:
            raise ValueError("Match is None!")

        sep = m.string[:0]
        if not isinstance(sep, bytes if self._bytes else str):
            raise TypeError('Match string type does not match expander string type!')
        text = []
        # Expand string
        for x in range(0, len(self.literals)):
            index = x
            l = self.literals[x]
            if l is None:
                g_index = self._get_group_index(index)
                span_case, single_case, capture = self._get_group_attributes(index)
                if not self.use_format:
                    # Non format replace
                    try:
                        l = m.group(g_index)
                        if l is None:
                            l = sep
                    except IndexError:  # pragma: no cover
                        raise IndexError("'{}' is out of range!".format(g_index))
                else:
                    # String format replace
                    try:
                        obj = m.group(g_index)
                    except IndexError:  # pragma: no cover
                        raise IndexError("'{}' is out of range!".format(g_index))
                    if isinstance(sep, bytes):
                        l = _util.format_bytes([] if obj is None else [obj], capture)
                    else:
                        l = _util.format_string([] if obj is None else [obj], capture)
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


def _pickle(r):  # type: ignore[no-untyped-def]
    """Pickle."""

    return ReplaceTemplate, (r.groups, r.group_slots, r.literals, r.pattern_hash, r.use_format, r._bytes)


_copyreg.pickle(ReplaceTemplate, _pickle)
