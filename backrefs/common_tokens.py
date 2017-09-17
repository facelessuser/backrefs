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
    "re_replace_ref": re.compile(
        r'''(?x)
        (\\)+
        (
            [cClLE]
        )? |
        (
            [cClLE]
        )
        '''
    ),
    "re_replace_group_ref": re.compile(
        r'''(?x)
        (\\)+
        (
            [1-9][0-9]?|[cClLE]|g<(?:[a-zA-Z]+[a-zA-Z\d_]*|[1-9][0-9]?)>
        )? |
        (
            [1-9][0-9]?|[cClLE]|g<(?:[a-zA-Z]+[a-zA-Z\d_]*|[1-9][0-9]?)>
        )
        '''
    ),
    "unicode_flag": 'u'
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
    "re_replace_ref": re.compile(
        br'''(?x)
        (\\)+
        (
            [cClLE]
        )? |
        (
            [cClLE]
        )
        '''
    ),
    "re_replace_group_ref": re.compile(
        br'''(?x)
        (\\)+
        (
            [1-9][0-9]?|[cClLE]|g<(?:[a-zA-Z]+[a-zA-Z\d_]*|[1-9][0-9])>
        )? |
        (
            [1-9][0-9]?|[cClLE]|g<(?:[a-zA-Z]+[a-zA-Z\d_]*|[1-9][0-9])>
        )
        '''
    ),
    "unicode_flag": b'u'
}
