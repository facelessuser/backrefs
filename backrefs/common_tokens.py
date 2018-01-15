"""
Common tokens shared between the different regex modules.

Licensed under MIT
Copyright (c) 2015 - 2016 Isaac Muse <isaacmuse@gmail.com>
"""

# Unicode string related references
tokens = {
    "ascii_letters": (
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
    ),
    "empty": "",
    "b_slash": "\\",
    "esc_end": "\\E",
    "escape": "e",
    "re_escape": r"\x1b",
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
