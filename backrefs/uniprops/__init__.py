"""Unicode Properties."""
from __future__ import unicode_literals
from . import unidata
import sys

UNICODE_RANGE = '\u0000-\U0010ffff'

PY35 = sys.version_info >= (3, 5)
PY37 = sys.version_info >= (3, 7)

POSIX = 0
POSIX_BYTES = 1
POSIX_UNICODE = 2


def get_posix_property(value, mode=POSIX):
    """Retrieve the posix category."""

    if mode == POSIX_BYTES:
        return unidata.ascii_posix_properties[value]
    elif mode == POSIX_UNICODE:
        return unidata.unicode_binary[
            ('^posix' + value[1:]) if value.startswith('^') else ('posix' + value)
        ]
    else:
        return unidata.unicode_posix_properties[value]


def get_gc_property(value, is_bytes=False):
    """Get `GC` property."""

    obj = unidata.ascii_properties if is_bytes else unidata.unicode_properties

    if value.startswith('^'):
        negate = True
        value = value[1:]
    else:
        negate = False

    value = unidata.unicode_alias['generalcategory'].get(value, value)

    assert 1 <= len(value) <= 2, 'Invalid property!'

    if not negate:
        p1, p2 = (value[0], value[1]) if len(value) > 1 else (value[0], None)
        value = ''.join(
            [v for k, v in obj.get(p1, {}).items() if not k.startswith('^')]
        ) if p2 is None else obj.get(p1, {}).get(p2, '')
    else:
        p1, p2 = (value[0], value[1]) if len(value) > 1 else (value[0], '')
        value = obj.get(p1, {}).get('^' + p2, '')
    assert value, 'Invalid property!'
    return value


def get_binary_property(value, is_bytes=False):
    """Get `BINARY` property."""

    obj = unidata.ascii_binary if is_bytes else unidata.unicode_binary

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['binary'].get(negated, negated)
    else:
        value = unidata.unicode_alias['binary'].get(value, value)

    return obj[value]


def get_canonical_combining_class_property(value, is_bytes=False):
    """Get `CANONICAL COMBINING CLASS` property."""

    obj = unidata.ascii_canonical_combining_class if is_bytes else unidata.unicode_canonical_combining_class

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['canonicalcombiningclass'].get(negated, negated)
    else:
        value = unidata.unicode_alias['canonicalcombiningclass'].get(value, value)

    return obj[value]


def get_east_asian_width_property(value, is_bytes=False):
    """Get `EAST ASIAN WIDTH` property."""

    obj = unidata.ascii_east_asian_width if is_bytes else unidata.unicode_east_asian_width

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['eastasianwidth'].get(negated, negated)
    else:
        value = unidata.unicode_alias['eastasianwidth'].get(value, value)

    return obj[value]


def get_grapheme_cluster_break_property(value, is_bytes=False):
    """Get `GRAPHEME CLUSTER BREAK` property."""

    obj = unidata.ascii_grapheme_cluster_break if is_bytes else unidata.unicode_grapheme_cluster_break

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['graphemeclusterbreak'].get(negated, negated)
    else:
        value = unidata.unicode_alias['graphemeclusterbreak'].get(value, value)

    return obj[value]


def get_line_break_property(value, is_bytes=False):
    """Get `LINE BREAK` property."""

    obj = unidata.ascii_line_break if is_bytes else unidata.unicode_line_break

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['linebreak'].get(negated, negated)
    else:
        value = unidata.unicode_alias['linebreak'].get(value, value)

    return obj[value]


def get_sentence_break_property(value, is_bytes=False):
    """Get `SENTENCE BREAK` property."""

    obj = unidata.ascii_sentence_break if is_bytes else unidata.unicode_sentence_break

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['sentencebreak'].get(negated, negated)
    else:
        value = unidata.unicode_alias['sentencebreak'].get(value, value)

    return obj[value]


def get_word_break_property(value, is_bytes=False):
    """Get `WORD BREAK` property."""

    obj = unidata.ascii_word_break if is_bytes else unidata.unicode_word_break

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['wordbreak'].get(negated, negated)
    else:
        value = unidata.unicode_alias['wordbreak'].get(value, value)

    return obj[value]


def get_hangul_syllable_type_property(value, is_bytes=False):
    """Get `HANGUL SYLLABLE TYPE` property."""

    obj = unidata.ascii_hangul_syllable_type if is_bytes else unidata.unicode_hangul_syllable_type

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['hangulsyllabletype'].get(negated, negated)
    else:
        value = unidata.unicode_alias['hangulsyllabletype'].get(value, value)

    return obj[value]


def get_indic_positional_category_property(value, is_bytes=False):
    """Get `INDIC POSITIONAL/MATRA CATEGORY` property."""

    if PY35:
        obj = unidata.ascii_indic_positional_category if is_bytes else unidata.unicode_indic_positional_category
        alias_key = 'indicpositionalcategory'
    else:
        obj = unidata.ascii_indic_matra_category if is_bytes else unidata.unicode_indic_matra_category
        alias_key = 'indicmatracategory'

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias[alias_key].get(negated, negated)
    else:
        value = unidata.unicode_alias[alias_key].get(value, value)

    return obj[value]


def get_indic_syllabic_category_property(value, is_bytes=False):
    """Get `INDIC SYLLABIC CATEGORY` property."""

    obj = unidata.ascii_indic_syllabic_category if is_bytes else unidata.unicode_indic_syllabic_category

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['indicsyllabiccategory'].get(negated, negated)
    else:
        value = unidata.unicode_alias['indicsyllabiccategory'].get(value, value)

    return obj[value]


def get_decomposition_type_property(value, is_bytes=False):
    """Get `DECOMPOSITION TYPE` property."""

    obj = unidata.ascii_decomposition_type if is_bytes else unidata.unicode_decomposition_type

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['decompositiontype'].get(negated, negated)
    else:
        value = unidata.unicode_alias['decompositiontype'].get(value, value)

    return obj[value]


def get_nfc_quick_check_property(value, is_bytes=False):
    """Get `NFC QUICK CHECK` property."""

    obj = unidata.ascii_nfc_quick_check if is_bytes else unidata.unicode_nfc_quick_check

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['nfcquickcheck'].get(negated, negated)
    else:
        value = unidata.unicode_alias['nfcquickcheck'].get(value, value)

    return obj[value]


def get_nfd_quick_check_property(value, is_bytes=False):
    """Get `NFD QUICK CHECK` property."""

    obj = unidata.ascii_nfd_quick_check if is_bytes else unidata.unicode_nfd_quick_check

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['nfdquickcheck'].get(negated, negated)
    else:
        value = unidata.unicode_alias['nfdquickcheck'].get(value, value)

    return obj[value]


def get_nfkc_quick_check_property(value, is_bytes=False):
    """Get `NFKC QUICK CHECK` property."""

    obj = unidata.ascii_nfkc_quick_check if is_bytes else unidata.unicode_nfkc_quick_check

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['nfkcquickcheck'].get(negated, negated)
    else:
        value = unidata.unicode_alias['nfkcquickcheck'].get(value, value)

    return obj[value]


def get_nfkd_quick_check_property(value, is_bytes=False):
    """Get `NFKD QUICK CHECK` property."""

    obj = unidata.ascii_nfkd_quick_check if is_bytes else unidata.unicode_nfkd_quick_check

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['nfkdquickcheck'].get(negated, negated)
    else:
        value = unidata.unicode_alias['nfkdquickcheck'].get(value, value)

    return obj[value]


def get_numeric_type_property(value, is_bytes=False):
    """Get `NUMERIC TYPE` property."""

    obj = unidata.ascii_numeric_type if is_bytes else unidata.unicode_numeric_type

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['numerictype'].get(negated, negated)
    else:
        value = unidata.unicode_alias['numerictype'].get(value, value)

    return obj[value]


def get_numeric_value_property(value, is_bytes=False):
    """Get `NUMERIC VALUE` property."""

    obj = unidata.ascii_numeric_values if is_bytes else unidata.unicode_numeric_values

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['numericvalue'].get(negated, negated)
    else:
        value = unidata.unicode_alias['numericvalue'].get(value, value)

    return obj[value]


def get_age_property(value, is_bytes=False):
    """Get `AGE` property."""

    obj = unidata.ascii_age if is_bytes else unidata.unicode_age

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['age'].get(negated, negated)
    else:
        value = unidata.unicode_alias['age'].get(value, value)

    return obj[value]


def get_joining_type_property(value, is_bytes=False):
    """Get `JOINING TYPE` property."""

    obj = unidata.ascii_joining_type if is_bytes else unidata.unicode_joining_type

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['joiningtype'].get(negated, negated)
    else:
        value = unidata.unicode_alias['joiningtype'].get(value, value)

    return obj[value]


def get_joining_group_property(value, is_bytes=False):
    """Get `JOINING GROUP` property."""

    obj = unidata.ascii_joining_group if is_bytes else unidata.unicode_joining_group

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['joininggroup'].get(negated, negated)
    else:
        value = unidata.unicode_alias['joininggroup'].get(value, value)

    return obj[value]


def get_script_property(value, is_bytes=False):
    """Get `SC` property."""

    obj = unidata.ascii_scripts if is_bytes else unidata.unicode_scripts

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['script'].get(negated, negated)
    else:
        value = unidata.unicode_alias['script'].get(value, value)

    return obj[value]


def get_script_extension_property(value, is_bytes=False):
    """Get `SCX` property."""

    obj = unidata.ascii_script_extensions if is_bytes else unidata.unicode_script_extensions

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['script'].get(negated, negated)
    else:
        value = unidata.unicode_alias['script'].get(value, value)

    return obj[value]


def get_block_property(value, is_bytes=False):
    """Get `BLK` property."""

    obj = unidata.ascii_blocks if is_bytes else unidata.unicode_blocks

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['block'].get(negated, negated)
    else:
        value = unidata.unicode_alias['block'].get(value, value)

    return obj[value]


def get_bidi_property(value, is_bytes=False):
    """Get `BC` property."""

    obj = unidata.ascii_bidi_classes if is_bytes else unidata.unicode_bidi_classes

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['bidiclass'].get(negated, negated)
    else:
        value = unidata.unicode_alias['bidiclass'].get(value, value)

    return obj[value]


def get_bidi_paired_bracket_type_property(value, is_bytes=False):
    """Get `BPT` property."""

    obj = unidata.ascii_bidi_paired_bracket_type if is_bytes else unidata.unicode_bidi_paired_bracket_type

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['bidipairedbrackettype'].get(negated, negated)
    else:
        value = unidata.unicode_alias['bidipairedbrackettype'].get(value, value)

    return obj[value]


def get_vertical_orientation_property(value, is_bytes=False):
    """Get `VO` property."""

    obj = unidata.ascii_vertical_orientation if is_bytes else unidata.unicode_vertical_orientation

    if value.startswith('^'):
        negated = value[1:]
        value = '^' + unidata.unicode_alias['verticalorientation'].get(negated, negated)
    else:
        value = unidata.unicode_alias['verticalorientation'].get(value, value)

    return obj[value]


def get_is_property(value, is_bytes=False):
    """Get shortcut for `SC` or `Binary` property."""

    if value.startswith('^'):
        prefix = value[1:3]
        temp = value[3:]
        negate = '^'
    else:
        prefix = value[:2]
        temp = value[2:]
        negate = ''

    if prefix != 'is':
        raise ValueError("Does not start with 'is'!")

    script_obj = unidata.ascii_script_extensions if is_bytes else unidata.unicode_script_extensions
    bin_obj = unidata.ascii_binary if is_bytes else unidata.unicode_binary

    value = negate + unidata.unicode_alias['script'].get(temp, temp)

    if value not in script_obj:
        value = negate + unidata.unicode_alias['binary'].get(temp, temp)
        obj = bin_obj
    else:
        obj = script_obj

    return obj[value]


def get_in_property(value, is_bytes=False):
    """Get shortcut for `Block` property."""

    if value.startswith('^'):
        prefix = value[1:3]
        temp = value[3:]
        negate = '^'
    else:
        prefix = value[:2]
        temp = value[2:]
        negate = ''

    if prefix != 'in':
        raise ValueError("Does not start with 'in'!")

    value = negate + unidata.unicode_alias['block'].get(temp, temp)
    obj = unidata.ascii_blocks if is_bytes else unidata.unicode_blocks

    return obj[value]


def is_enum(name):
    """Check if name is an enum (not a binary) property."""

    return name in unidata.enum_names


def get_unicode_property(value, prop=None, is_bytes=False):
    """Retrieve the Unicode category from the table."""

    if prop is not None:
        prop = unidata.unicode_alias['_'].get(prop, prop)
        try:
            if prop == 'generalcategory':
                return get_gc_property(value, is_bytes)
            elif prop == 'script':
                return get_script_property(value, is_bytes)
            elif prop == 'scriptextensions':
                return get_script_extension_property(value, is_bytes)
            elif prop == 'block':
                return get_block_property(value, is_bytes)
            elif prop == 'binary':
                return get_binary_property(value, is_bytes)
            elif prop == 'bidiclass':
                return get_bidi_property(value, is_bytes)
            elif prop == 'bidipairedbrackettype':
                return get_bidi_paired_bracket_type_property(value, is_bytes)
            elif prop == 'age':
                return get_age_property(value, is_bytes)
            elif prop == 'eastasianwidth':
                return get_east_asian_width_property(value, is_bytes)
            elif PY35 and prop == 'indicpositionalcategory':
                return get_indic_positional_category_property(value, is_bytes)
            elif not PY35 and prop == 'indicmatracategory':
                return get_indic_positional_category_property(value, is_bytes)
            elif prop == 'indicsyllabiccategory':
                return get_indic_syllabic_category_property(value, is_bytes)
            elif prop == 'hangulsyllabletype':
                return get_hangul_syllable_type_property(value, is_bytes)
            elif prop == 'decompositiontype':
                return get_decomposition_type_property(value, is_bytes)
            elif prop == 'canonicalcombiningclass':
                return get_canonical_combining_class_property(value, is_bytes)
            elif prop == 'numerictype':
                return get_numeric_type_property(value, is_bytes)
            elif prop == 'numericvalue':
                return get_numeric_value_property(value, is_bytes)
            elif prop == 'joiningtype':
                return get_joining_type_property(value, is_bytes)
            elif prop == 'joininggroup':
                return get_joining_group_property(value, is_bytes)
            elif prop == 'graphemeclusterbreak':
                return get_grapheme_cluster_break_property(value, is_bytes)
            elif prop == 'linebreak':
                return get_line_break_property(value, is_bytes)
            elif prop == 'sentencebreak':
                return get_sentence_break_property(value, is_bytes)
            elif prop == 'wordbreak':
                return get_word_break_property(value, is_bytes)
            elif prop == 'nfcquickcheck':
                return get_nfc_quick_check_property(value, is_bytes)
            elif prop == 'nfdquickcheck':
                return get_nfd_quick_check_property(value, is_bytes)
            elif prop == 'nfkcquickcheck':
                return get_nfkc_quick_check_property(value, is_bytes)
            elif prop == 'nfkdquickcheck':
                return get_nfkd_quick_check_property(value, is_bytes)
            elif PY37 and prop == 'verticalorientation':
                return get_vertical_orientation_property(value, is_bytes)
            else:
                raise ValueError('Invalid Unicode property!')
        except Exception:
            raise ValueError('Invalid Unicode property!')

    try:
        return get_gc_property(value, is_bytes)
    except Exception:
        pass

    try:
        return get_script_extension_property(value, is_bytes)
    except Exception:
        pass

    try:
        return get_block_property(value, is_bytes)
    except Exception:
        pass

    try:
        return get_binary_property(value, is_bytes)
    except Exception:
        pass

    try:
        return get_is_property(value, is_bytes)
    except Exception:
        pass

    try:
        return get_in_property(value, is_bytes)
    except Exception:
        pass

    raise ValueError('Invalid Unicode property!')
