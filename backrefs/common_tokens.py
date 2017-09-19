"""
Common tokens shared between the different regex modules.

Licensed under MIT
Copyright (c) 2015 - 2016 Isaac Muse <isaacmuse@gmail.com>
"""
import re

# Unicode string related references
utokens = {
    "replace_tokens": set("cCElL"),
    "verbose_tokens": set("# "),
    "empty": "",
    "ls_bracket": "[",
    "rs_bracket": "]",
    "b_slash": "\\",
    "esc_end": "\\E",
    "end": "E",
    "quote": "Q",
    "lc": "l",
    "lc_span": "L",
    "uc": "c",
    "uc_span": "C",
    "hashtag": '#',
    "nl": '\n',
    "negate": '^',
    "verbose_flag": 'x',
    "unicode_flag": 'u',
    "group": "g",
    "lc_bracket": "{",
    "rc_bracket": "}",
    "group_start": r"\g<",
    "group_end": ">",
    "replace_group_ref": re.compile(
        r'(\\)|([1-9][0-9]?|[cClLE]|g<(?:[a-zA-Z]+[a-zA-Z\d_]*|0+|0*[1-9][0-9]?)>)'
    ),
    "format_replace_ref": re.compile(r'(\\)|([cClLE])'),
    "format_replace_group": re.compile(
        r'(\{{2}|\}{2})|(\{(?:[a-zA-Z]+[a-zA-Z\d_]*|0+|0*[1-9][0-9]?)?(?:\[-?\d+\])?\})'
    )
}

# Byte string related references
btokens = {
    "replace_tokens": set(
        [b"c", b"C", b"E", b"l", b"L"]
    ),
    "verbose_tokens": set([b"#", b" "]),
    "empty": b"",
    "ls_bracket": b"[",
    "rs_bracket": b"]",
    "b_slash": b"\\",
    "esc_end": b"\\E",
    "end": b"E",
    "quote": b"Q",
    "lc": b"l",
    "lc_span": b"L",
    "uc": b"c",
    "uc_span": b"C",
    "hashtag": b'#',
    "nl": b'\n',
    "negate": b'^',
    "verbose_flag": b'x',
    "unicode_flag": b'u',
    "group": b"g",
    "lc_bracket": b"{",
    "rc_bracket": b"}",
    "group_start": br"\g<",
    "group_end": b">",
    "replace_group_ref": re.compile(
        br'(\\)|([1-9][0-9]?|[cClLE]|g<(?:[a-zA-Z]+[a-zA-Z\d_]*|0+|0*[1-9][0-9]?)>)'
    ),
    "format_replace_ref": re.compile(br'(\\)|([cClLE])'),
    "format_replace_group": re.compile(
        br'(\{{2}|\}{2})|(\{(?:[a-zA-Z]+[a-zA-Z\d_]*|0+|0*[1-9][0-9]?)?(?:\[-?\d+\])?\})'
    )
}
