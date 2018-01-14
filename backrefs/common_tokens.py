"""
Common tokens shared between the different regex modules.

Licensed under MIT
Copyright (c) 2015 - 2016 Isaac Muse <isaacmuse@gmail.com>
"""

# Unicode string related references
utokens = {
    "empty": "",
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
    "ls_bracket": "[",
    "rs_bracket": "]",
    "lc_bracket": "{",
    "rc_bracket": "}",
    "lr_bracket": "(",
    "rr_bracket": ")",
    "group": "g",
    "group_start": r"\g<",
    "group_end": ">",
    "minus": "-",
    "binary": "b",
    "octal": "o",
    "hex": "x",
    "zero": "0",
    "unicode_narrow": "u",
    "unicode_wide": "U",
    "unicode_name": "N",
    "long_replace_refs": ("u", "U", "g", "x", "N")
}

# Byte string related references
btokens = {
    "empty": b"",
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
    "ls_bracket": b"[",
    "rs_bracket": b"]",
    "lc_bracket": b"{",
    "rc_bracket": b"}",
    "lr_bracket": b"(",
    "rr_bracket": b")",
    "group": b"g",
    "group_start": br"\g<",
    "group_end": b">",
    "minus": b"-",
    "binary": b"b",
    "octal": b"o",
    "hex": b"x",
    "zero": b"0",
    "unicode_narrow": b"u",
    "unicode_wide": b"U",
    "unicode_name": b"N",
    "long_replace_refs": (b"g", b"x")
}
