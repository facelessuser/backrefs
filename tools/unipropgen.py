"""Generate a Unicode prop table for Python builds."""
import sys
import unicodedata
import os
import re

__version__ = '5.0.0'

UNIVERSION = None
UNIVERSION_INFO = None
HOME = os.path.dirname(os.path.abspath(__file__))
MAXUNICODE = sys.maxunicode
MAXASCII = 0xFF
MAXVALIDASCII = 0x7F
GROUP_ESCAPES = frozenset([ord(x) for x in '-&[\\]^|~'])

UNICODE_RANGE = (0x0000, 0x10FFFF)
ASCII_RANGE = (0x00, 0xFF)
ASCII_LIMIT = (0x00, 0x7F)

ALL_CHARS = frozenset(list(range(UNICODE_RANGE[0], UNICODE_RANGE[1] + 1)))
ASCII_UNUSED = frozenset(list(range(0x80, UNICODE_RANGE[1] + 1)))
ALL_ASCII = frozenset(list(range(ASCII_RANGE[0], ASCII_RANGE[1] + 1)))
HEADER = '''\
"""Unicode Properties from Unicode version {} (autogen)."""
{}'''
TYPING = 'from __future__ import annotations\n\n'


def uniformat(value):
    """Convert a Unicode char."""

    if value in GROUP_ESCAPES:
        # Escape characters that are (or will be in the future) problematic
        c = "\\x%02x\\x%02x" % (0x5c, value)
    elif value <= 0xFF:
        c = "\\x%02x" % value
    elif value <= 0xFFFF:
        c = "\\u%04x" % value
    else:
        c = "\\U%08x" % value
    return c


def format_name(text):
    """Format the name."""
    return text.strip().lower().replace(' ', '').replace('-', '').replace('_', '')


def create_span(unirange, is_bytes=False):
    """Clamp the Unicode range."""

    if len(unirange) < 2:
        unirange.append(unirange[0])
    if is_bytes:
        if unirange[0] > MAXVALIDASCII:
            return []
        if unirange[1] > MAXVALIDASCII:
            unirange[1] = MAXVALIDASCII
    return list(range(unirange[0], unirange[1] + 1))


def not_explicitly_defined(table, name, is_bytes=False):
    """Compose a table with the specified entry name of values not explicitly defined."""

    name = name.lower()
    all_chars = ALL_CHARS
    s = set()
    for v in table.values():
        s.update(v)
    if name in table:
        table[name] = list(set(table[name]) | (all_chars - s))
    else:
        table[name] = list(all_chars - s)


def char2range(d, is_bytes=False, invert=True):
    """Convert the characters in the dict to a range in string form."""

    fmt = uniformat
    maxrange = MAXUNICODE

    for k1 in sorted(d.keys()):
        v1 = d[k1]
        if not isinstance(v1, list):
            char2range(v1, is_bytes=is_bytes, invert=invert)
        else:
            inverted = k1.startswith('^')
            v1.sort()
            last = None
            first = None
            ilast = None
            ifirst = None
            v2 = []
            iv2 = []
            if v1 and v1[0] != 0:
                ifirst = 0
            for i in v1:
                if first is None:
                    first = i
                    last = i
                elif i == last + 1:
                    last = i
                elif first is not None:
                    if first == last:
                        v2.append(fmt(first))
                    else:
                        v2.append("%s-%s" % (fmt(first), fmt(last)))
                    if invert and ifirst is not None:
                        ilast = first - 1
                        if ifirst == ilast:
                            iv2.append(fmt(ifirst))
                        else:
                            iv2.append("%s-%s" % (fmt(ifirst), fmt(ilast)))
                    ifirst = last + 1
                    first = i
                    last = i

            if not v1:
                iv2 = ["%s-%s" % (fmt(0), fmt(maxrange))]
            elif first is not None:
                if first == last:
                    v2.append(fmt(first))
                else:
                    v2.append("%s-%s" % (fmt(first), fmt(last)))
                if invert and ifirst is not None:
                    ilast = first - 1
                    if ifirst == ilast:
                        iv2.append(fmt(ifirst))
                    else:
                        iv2.append("%s-%s" % (fmt(ifirst), fmt(ilast)))
                ifirst = last + 1
                if invert and ifirst <= maxrange:
                    ilast = maxrange
                    if ifirst == ilast:
                        iv2.append(fmt(ifirst))
                    else:
                        iv2.append("%s-%s" % (fmt(ifirst), fmt(ilast)))
            d[k1] = ''.join(v2)
            if invert:
                d[k1[1:] if inverted else '^' + k1] = ''.join(iv2)


def get_files(output):
    """Get files."""

    files = {
        'gc': os.path.join(output, 'generalcategory.py'),
        'blk': os.path.join(output, 'block.py'),
        'sc': os.path.join(output, 'script.py'),
        'bc': os.path.join(output, 'bidiclass.py'),
        'binary': os.path.join(output, 'binary.py'),
        'age': os.path.join(output, 'age.py'),
        'ea': os.path.join(output, 'eastasianwidth.py'),
        'gcb': os.path.join(output, 'graphemeclusterbreak.py'),
        'lb': os.path.join(output, 'linebreak.py'),
        'sb': os.path.join(output, 'sentencebreak.py'),
        'wb': os.path.join(output, 'wordbreak.py'),
        'hst': os.path.join(output, 'hangulsyllabletype.py'),
        'dt': os.path.join(output, 'decompositiontype.py'),
        'jt': os.path.join(output, 'joiningtype.py'),
        'jg': os.path.join(output, 'joininggroup.py'),
        'nt': os.path.join(output, 'numerictype.py'),
        'nv': os.path.join(output, 'numericvalue.py'),
        'ccc': os.path.join(output, 'canonicalcombiningclass.py'),
        'qc': os.path.join(output, 'quickcheck.py'),
        'alias': os.path.join(output, 'alias.py'),
        'scx': os.path.join(output, 'scriptextensions.py'),
        'insc': os.path.join(output, 'indicsyllabiccategory.py'),
        'bpt': os.path.join(output, 'bidipairedbrackettype.py'),
        'inpc': os.path.join(output, 'indicpositionalcategory.py')
    }

    if UNIVERSION_INFO >= (11, 0, 0):
        files['vo'] = os.path.join(output, 'verticalorientation.py')

    return files


def discover_categories():
    """Discover the categories we need."""

    categories = [
        'generalcategory', 'script', 'block',
        'bidiclass', 'eastasianwidth', 'linebreak',
        'hangulsyllabletype', 'wordbreak', 'sentencebreak',
        'graphemeclusterbreak', 'decompositiontype', 'joiningtype',
        'joininggroup', 'numerictype', 'numericvalue',
        'canonicalcombiningclass', 'age'
    ]
    categories.append('scriptextensions')
    categories.append('indicsyllabiccategory')
    categories.append('bidipairedbrackettype')
    categories.append('indicpositionalcategory')

    if UNIVERSION_INFO >= (11, 0, 0):
        categories.append('verticalorientation')

    binary_categories = ['fullcompositionexclusion', 'compositionexclusion', 'bidimirrored']

    # NF Quick Check categories
    file_name = os.path.join(HOME, 'unicodedata', UNIVERSION, 'DerivedNormalizationProps.txt')
    with open(file_name, 'r', encoding='utf-8') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split('#')[0].split(';')
                if len(data) < 2:
                    continue
                if not data[1].strip().lower().endswith('_qc'):
                    continue
                span = create_span([int(i, 16) for i in data[0].strip().split('..')], is_bytes=False)
                if not span:
                    continue
                name = format_name(data[1][:-3] + 'quickcheck')

                if name not in categories:
                    categories.append(name)

    binary_props = [
        ('DerivedCoreProperties.txt', None),
        ('PropList.txt', None),
        ('DerivedNormalizationProps.txt', ('Changes_When_NFKC_Casefolded', 'Full_Composition_Exclusion'))
    ]

    if UNIVERSION_INFO >= (13, 0, 0):
        binary_props.append(('emoji-data.txt', None))

    for filename, include in binary_props:
        with open(os.path.join(HOME, 'unicodedata', UNIVERSION, filename), 'r', encoding='utf-8') as uf:
            for line in uf:
                if not line.startswith('#'):
                    data = line.split('#')[0].split(';')
                    if len(data) < 2:
                        continue
                    if include and data[1].strip() not in include:
                        continue
                    name = format_name(data[1])

                    if name not in binary_categories:
                        binary_categories.append(name)
    return categories, binary_categories


def gen_blocks(output, ascii_props=False, append=False, prefix="", aliases=None):
    """Generate Unicode blocks."""

    with open(output, 'a' if append else 'w', encoding='utf-8') as f:
        if not append:
            f.write(HEADER.format(UNIVERSION, TYPING))
        f.write('%s_blocks: dict[str, str] = {' % prefix)
        no_block = []
        last = -1
        found = {'noblock'}

        max_limit = MAXVALIDASCII if ascii_props else MAXUNICODE
        max_range = MAXUNICODE
        formatter = uniformat

        with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'Blocks.txt'), 'r', encoding='utf-8') as uf:
            for line in uf:
                if not line.startswith('#'):
                    data = line.split(';')
                    if len(data) < 2:
                        continue
                    block = [int(i, 16) for i in data[0].strip().split('..')]
                    if block[0] > last + 1:
                        if (last + 1) <= max_limit:
                            endval = block[0] - 1 if (block[0] - 1) < max_limit else max_limit
                            no_block.append((last + 1, endval))
                    last = block[1]
                    name = format_name(data[1])
                    found.add(name)
                    inverse_range = []
                    if block[0] > max_limit:
                        if ascii_props:
                            f.write('\n    "%s": "",' % name)
                            f.write('\n    "^%s": "%s-%s",' % (name, formatter(0), formatter(max_range)))
                        continue
                    if block[0] > 0:
                        inverse_range.append("%s-%s" % (formatter(0), formatter(block[0] - 1)))
                    if block[1] < max_range:
                        inverse_range.append("%s-%s" % (formatter(block[1] + 1), formatter(max_range)))
                    f.write('\n    "%s": "%s-%s",' % (name, formatter(block[0]), formatter(block[1])))
                    f.write('\n    "^%s": "%s",' % (name, ''.join(inverse_range)))
            # Initialize values found in aliases in case they have no values.
            if aliases:
                for v in aliases.get('block', {}).values():
                    if v not in found:
                        f.write('\n    "%s": "",' % v)
                        f.write('\n    "^%s": "%s-%s",' % (v, formatter(0), formatter(max_range)))
            if last < max_range:
                if (last + 1) <= max_range:
                    no_block.append((last + 1, max_range))
            last = -1
            no_block_inverse = []
            if not no_block:
                no_block_inverse.append((0, max_range))
            else:
                for piece in no_block:
                    if piece[0] > last + 1:
                        no_block_inverse.append((last + 1, piece[0] - 1))
                    last = piece[1]
            for block, name in ((no_block, 'noblock'), (no_block_inverse, '^noblock')):
                f.write('\n    "%s": "' % name)
                for piece in block:
                    if piece[0] == piece[1]:
                        f.write(formatter(piece[0]))
                    else:
                        f.write("%s-%s" % (formatter(piece[0]), formatter(piece[1])))
                f.write('",')
            f.write('\n}\n')


def gen_ccc(output, ascii_props=False, append=False, prefix="", aliases=None):
    """Generate `canonical combining class` property."""

    obj = {}

    if aliases:
        for v in aliases.get('canonicalcombiningclass', {}).values():
            obj[v] = []

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'DerivedCombiningClass.txt'), 'r', encoding='utf-8') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split('#')[0].split(';')
                if len(data) < 2:
                    continue
                span = create_span([int(i, 16) for i in data[0].strip().split('..')], is_bytes=ascii_props)
                if not span:
                    continue
                name = format_name(data[1])

                if name not in obj:
                    obj[name] = []
                obj[name].extend(span)

    for x in range(0, 256):
        key = str(x)
        if key not in obj:
            obj[key] = []

    for name in list(obj.keys()):
        s = set(obj[name])
        obj[name] = sorted(s)

    not_explicitly_defined(obj, '0', is_bytes=ascii_props)

    # Convert characters values to ranges
    char2range(obj, is_bytes=ascii_props)

    with open(output, 'a' if append else 'w', encoding='utf-8') as f:
        if not append:
            f.write(HEADER.format(UNIVERSION, TYPING))
        # Write out the Unicode properties
        f.write('%s_canonical_combining_class: dict[str, str] = {\n' % prefix)
        count = len(obj) - 1
        i = 0
        for k1, v1 in sorted(obj.items()):
            f.write('    "%s": "%s"' % (k1, v1))
            if i == count:
                f.write('\n}\n')
            else:
                f.write(',\n')
            i += 1


def gen_scripts(
    file_name, file_name_ext, obj_name, obj_ext_name, output, output_ext,
    field=1, notexplicit=None, ascii_props=False, append=False, prefix="", aliases=None
):
    """Generate `script` property."""

    obj = {}
    obj2 = {}

    # Initialize values found in aliases in case they have no values.
    if aliases:
        for v in aliases.get('script', {}).values():
            obj[v] = []
            obj2[v] = []

    alias = {}
    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'PropertyValueAliases.txt'), 'r', encoding='utf-8') as uf:
        for line in uf:
            if line.startswith('sc ;'):
                values = line.split(';')
                alias[format_name(values[1].strip())] = format_name(values[2].strip())

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, file_name_ext), 'r', encoding='utf-8') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split('#')[0].split(';')
                if len(data) < 2:
                    continue
                exts = [alias[format_name(n)] for n in data[1].strip().split(' ')]
                span = create_span([int(i, 16) for i in data[0].strip().split('..')], is_bytes=ascii_props)
                for ext in exts:
                    if ext not in obj2:
                        obj2[ext] = []
                    if not span:
                        continue

                    obj2[ext].extend(span)

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, file_name), 'r', encoding='utf-8') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split('#')[0].split(';')
                if len(data) < 2:
                    continue
                span = create_span([int(i, 16) for i in data[0].strip().split('..')], is_bytes=ascii_props)
                name = format_name(data[1])
                if name not in obj:
                    obj[name] = []
                if name not in obj2:
                    obj2[name] = []

                if not span:
                    continue

                obj[name].extend(span)
                obj2[name].extend(span)

    for name in list(obj.keys()):
        s = set(obj[name])
        obj[name] = sorted(s)

    for name in list(obj2.keys()):
        s = set(obj2[name])
        obj2[name] = sorted(s)

    if notexplicit:
        not_explicitly_defined(obj, notexplicit, is_bytes=ascii_props)
        not_explicitly_defined(obj2, notexplicit, is_bytes=ascii_props)

    # Convert characters values to ranges
    char2range(obj, is_bytes=ascii_props)
    char2range(obj2, is_bytes=ascii_props)

    with open(output, 'a' if append else 'w', encoding='utf-8') as f:
        if not append:
            f.write(HEADER.format(UNIVERSION, TYPING))
        # Write out the Unicode properties
        f.write('%s_%s: dict[str, str] = {\n' % (prefix, obj_name))
        count = len(obj) - 1
        i = 0
        for k1, v1 in sorted(obj.items()):
            f.write('    "%s": "%s"' % (k1, v1))
            if i == count:
                f.write('\n}\n')
            else:
                f.write(',\n')
            i += 1

    with open(output_ext, 'a' if append else 'w', encoding='utf-8') as f:
        if not append:
            f.write(HEADER.format(UNIVERSION, TYPING))
        # Write out the Unicode properties
        f.write('%s_%s: dict[str, str] = {\n' % (prefix, obj_ext_name))
        count = len(obj2) - 1
        i = 0
        for k1, v1 in sorted(obj2.items()):
            f.write('    "%s": "%s"' % (k1, v1))
            if i == count:
                f.write('\n}\n')
            else:
                f.write(',\n')
            i += 1


def gen_enum(
    file_name, obj_name, output, field=1, notexplicit=None, ascii_props=False, append=False, prefix="", aliases=None
):
    """Generate generic enum properties, or properties very much like enum properties."""

    obj = {}

    # Initialize values found in aliases in case they have no values.
    if aliases:
        for v in aliases.get(format_name(obj_name), {}).values():
            obj[v] = []

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, file_name), 'r', encoding='utf-8') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split('#')[0].split(';')
                if len(data) < 2:
                    continue
                span = create_span([int(i, 16) for i in data[0].strip().split('..')], is_bytes=ascii_props)
                name = format_name(data[field])
                if name not in obj:
                    obj[name] = []

                if not span:
                    continue

                obj[name].extend(span)

    for name in list(obj.keys()):
        s = set(obj[name])
        obj[name] = sorted(s)

    if notexplicit:
        not_explicitly_defined(obj, notexplicit, is_bytes=ascii_props)

    # Convert characters values to ranges
    char2range(obj, is_bytes=ascii_props)

    with open(output, 'a' if append else 'w', encoding='utf-8') as f:
        if not append:
            f.write(HEADER.format(UNIVERSION, TYPING))
        # Write out the Unicode properties
        f.write('%s_%s: dict[str, str] = {\n' % (prefix, obj_name))
        count = len(obj) - 1
        i = 0
        for k1, v1 in sorted(obj.items()):
            f.write('    "%s": "%s"' % (k1, v1))
            if i == count:
                f.write('\n}\n')
            else:
                f.write(',\n')
            i += 1


def gen_age(output, ascii_props=False, append=False, prefix="", aliases=None):
    """Generate `age` property."""

    obj = {}

    # Initialize values found in aliases in case they have no values.
    if aliases:
        for v in aliases.get('age', {}).values():
            obj[v] = []

    all_chars = (ALL_CHARS - ASCII_UNUSED) if ascii_props else ALL_CHARS
    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'DerivedAge.txt'), 'r', encoding='utf-8') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split('#')[0].split(';')
                if len(data) < 2:
                    continue
                span = create_span([int(i, 16) for i in data[0].strip().split('..')], is_bytes=ascii_props)
                name = format_name(data[1])

                if name not in obj:
                    obj[name] = []

                if not span:
                    continue

                obj[name].extend(span)

    unassigned = set()
    for x in obj.values():
        unassigned |= set(x)
    obj['na'] = list(all_chars - unassigned)

    for name in list(obj.keys()):
        s = set(obj[name])
        obj[name] = sorted(s)

    # Convert characters values to ranges
    char2range(obj, is_bytes=ascii_props)

    with open(output, 'a' if append else 'w', encoding='utf-8') as f:
        if not append:
            f.write(HEADER.format(UNIVERSION, TYPING))
        # Write out the Unicode properties
        f.write('%s_age: dict[str, str] = {\n' % prefix)
        count = len(obj) - 1
        i = 0
        for k1, v1 in sorted(obj.items()):
            f.write('    "%s": "%s"' % (k1, v1))
            if i == count:
                f.write('\n}\n')
            else:
                f.write(',\n')
            i += 1


def gen_nf_quick_check(output, ascii_props=False, append=False, prefix="", aliases=None):
    """Generate quick check properties."""

    nf = {}
    all_chars = (ALL_CHARS - ASCII_UNUSED) if ascii_props else ALL_CHARS
    file_name = os.path.join(HOME, 'unicodedata', UNIVERSION, 'DerivedNormalizationProps.txt')
    with open(file_name, 'r', encoding='utf-8') as uf:
        for line in uf:
            if not line.startswith('#'):
                data = line.split('#')[0].split(';')
                if len(data) < 2:
                    continue
                if not data[1].strip().lower().endswith('_qc'):
                    continue
                span = create_span([int(i, 16) for i in data[0].strip().split('..')], is_bytes=ascii_props)
                name = format_name(data[1][:-3] + 'quickcheck')
                subvalue = format_name(data[2])

                if name not in nf:
                    nf[name] = {}
                    # Initialize values found in aliases in case they have no values.
                    if aliases:
                        for v in aliases.get(name, {}).values():
                            nf[name][v] = []

                if subvalue not in nf[name]:
                    nf[name][subvalue] = []
                if not span:
                    continue

                nf[name][subvalue].extend(span)

    for v1 in nf.values():
        temp = set()
        for k2 in list(v1.keys()):
            temp |= set(v1[k2])
        v1['y'] = list(all_chars - temp)

    for k1, v1 in nf.items():
        for name in list(v1.keys()):
            s = set(nf[k1][name])
            nf[k1][name] = sorted(s)

    # Convert characters values to ranges
    char2range(nf, is_bytes=ascii_props)

    with open(output, 'a' if append else 'w', encoding='utf-8') as f:
        if not append:
            f.write(HEADER.format(UNIVERSION, TYPING))
        for key, value in sorted(nf.items()):
            # Write out the Unicode properties
            f.write('%s_%s: dict[str, str] = {\n' % (prefix, key.replace('quickcheck', '_quick_check')))
            count = len(value) - 1
            i = 0
            for k1, v1 in sorted(value.items()):
                f.write('    "%s": "%s"' % (k1, v1))
                if i == count:
                    f.write('\n}\n')
                else:
                    f.write(',\n')
                i += 1


def gen_binary(table, output, ascii_props=False, append=False, prefix="", aliases=None):
    """Generate binary properties."""

    max_range = MAXVALIDASCII if ascii_props else MAXUNICODE

    binary_props = [
        ('DerivedCoreProperties.txt', None),
        ('PropList.txt', None),
        ('DerivedNormalizationProps.txt', ('Changes_When_NFKC_Casefolded', 'Full_Composition_Exclusion'))
    ]

    if UNIVERSION_INFO >= (13, 0, 0):
        binary_props.append(('emoji-data.txt', None))

    # Custom binary properties
    binary = {
        'horizspace': (
            [0x09, 0x20, 0xA0, 0x1680, 0x180E] +
            create_span([0x2000, 0x200A], is_bytes=ascii_props) +
            [0x202F, 0x205F, 0x3000]
        ),
        'vertspace': create_span([0x0A, 0x0D], is_bytes=ascii_props) + [0x85, 0x2028, 0x2029]
    }
    binary['horizspace'] = [x for x in binary['horizspace'] if x <= max_range]
    binary['vertspace'] = [x for x in binary['vertspace'] if x <= max_range]

    for filename, include in binary_props:
        with open(os.path.join(HOME, 'unicodedata', UNIVERSION, filename), 'r', encoding='utf-8') as uf:
            for line in uf:
                if not line.startswith('#'):
                    data = line.split('#')[0].split(';')
                    if len(data) < 2:
                        continue
                    if include and data[1].strip() not in include:
                        continue
                    span = create_span([int(i, 16) for i in data[0].strip().split('..')], is_bytes=ascii_props)
                    name = format_name(data[1])

                    if name not in binary:
                        binary[name] = []
                    if not span:
                        continue
                    binary[name].extend(span)

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'CompositionExclusions.txt'), 'r', encoding='utf-8') as uf:
        name = 'compositionexclusion'
        for line in uf:
            if not line.startswith('#'):
                data = [x.strip() for x in line.split('#') if x.strip()]
                if not data:
                    continue
                span = create_span([int(data[0], 16)], is_bytes=ascii_props)
                if not span:
                    continue

                if name not in binary:
                    binary[name] = []
                binary[name].extend(span)

    file_name = os.path.join(HOME, 'unicodedata', UNIVERSION, 'DerivedNormalizationProps.txt')
    with open(file_name, 'r', encoding='utf-8') as uf:
        name = "fullcompositionexclusion"
        for line in uf:
            if not line.startswith('#'):
                data = line.split('#')[0].split(';')
                if len(data) < 2:
                    continue
                if not data[1].strip().lower() == 'Full_Composition_Exclusion':
                    continue
                span = create_span([int(i, 16) for i in data[0].strip().split('..')], is_bytes=False)
                if not span:
                    continue

                if name not in binary:
                    binary[name] = []
                binary[name].extend(span)

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'UnicodeData.txt'), 'r', encoding='utf-8') as uf:
        name = 'bidimirrored'
        for line in uf:
            data = line.strip().split(';')
            if data:
                if data[9].strip().lower() != 'y':
                    continue
                span = create_span([int(data[0].strip(), 16)], is_bytes=ascii_props)
                if not span:
                    continue

                if name not in binary:
                    binary[name] = []
                binary[name].extend(span)

    for name in list(binary.keys()):
        s = set(binary[name])
        binary[name] = sorted(s)

    gen_uposix(table, binary, ascii_props)

    if aliases:
        for v in aliases.get('binary', {}).values():
            if v not in binary and '^' + v not in binary:
                binary[v] = []

    # Convert characters values to ranges
    char2range(binary, is_bytes=ascii_props)

    with open(output, 'a' if append else 'w', encoding='utf-8') as f:
        if not append:
            f.write(HEADER.format(UNIVERSION, TYPING))
        # Write out the Unicode properties
        f.write('%s_binary: dict[str, str] = {\n' % prefix)
        count = len(binary) - 1
        i = 0
        for k1, v1 in sorted(binary.items()):
            f.write('    "%s": "%s"' % (k1, v1))
            if i == count:
                f.write('\n}\n')
            else:
                f.write(',\n')
            i += 1


def gen_bidi(output, ascii_props=False, append=False, prefix="", aliases=None):
    """Generate `bidi class` property."""

    bidi_class = {}

    # Initialize values found in aliases in case they have no values.
    if aliases:
        for v in aliases.get('bidiclasses', {}).values():
            bidi_class[v] = []

    max_range = MAXVALIDASCII if ascii_props else MAXUNICODE
    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'UnicodeData.txt'), 'r', encoding='utf-8') as uf:
        for line in uf:
            data = line.strip().split(';')
            if data:
                bidi = data[4].strip().lower()
                if not bidi:
                    continue
                value = int(data[0].strip(), 16)

                if bidi not in bidi_class:
                    bidi_class[bidi] = []

                if value > max_range:
                    continue

                bidi_class[bidi].append(value)

    for name in list(bidi_class.keys()):
        s = set(bidi_class[name])
        bidi_class[name] = sorted(s)

    # Convert characters values to ranges
    char2range(bidi_class, is_bytes=ascii_props)

    with open(output, 'a' if append else 'w', encoding='utf-8') as f:
        if not append:
            f.write(HEADER.format(UNIVERSION, TYPING))
        f.write('%s_bidi_classes: dict[str, str] = {\n' % prefix)
        count = len(bidi_class) - 1
        i = 0
        for k1, v1 in sorted(bidi_class.items()):
            f.write('    "%s": "%s"' % (k1, v1))
            if i == count:
                f.write('\n}\n')
            else:
                f.write(',\n')
            i += 1


def gen_uposix(table, posix_table, ascii_props):
    """Generate the POSIX table and write out to file."""

    # `Punct: [[\p{P}\p{S}]--[\p{Alphabetic}]]`
    s = set()
    for table_name in ('p', 's'):
        for sub_table_name in table[table_name]:
            if not sub_table_name.startswith('^'):
                s |= set(table[table_name][sub_table_name])
    s -= set(posix_table['alphabetic'])
    posix_table["posixpunct"] = list(s)

    # `Digit: [0-9]`
    s = set(range(0x30, 0x39 + 1))
    posix_table["posixdigit"] = list(s)

    # `XDigit: [\p{Nd}\p{HexDigit}]`
    s = set(table['n']['d']) | set(posix_table["hexdigit"])
    posix_table["xdigit"] = list(s)

    # `XDigit: [A-Fa-f0-9]`
    s = set(range(0x30, 0x39 + 1))
    s |= set(range(0x41, 0x46 + 1))
    s |= set(range(0x61, 0x66 + 1))
    posix_table["posixxdigit"] = list(s)

    # `Alnum: [\p{PosixAlpha}\p{PosixDigit}]`
    s = set(posix_table['alphabetic']) | set(posix_table["posixdigit"])
    posix_table["posixalnum"] = list(s)

    # `Alnum: [\p{PosixAlpha}\p{Nd}]`
    s = set(posix_table['alphabetic']) | set(table['n']['d'])
    posix_table["alnum"] = list(s)

    # `Blank: [\p{Zs}\t]`
    s = set(table['z']['s'] + [0x09])
    posix_table["posixblank"] = list(s)

    # `Graph: [^\p{PosixSpace}\p{Cc}\p{Cn}\p{Cs}]`
    s = ((ALL_CHARS - ASCII_UNUSED) if ascii_props else ALL_CHARS) - (
        set(posix_table["whitespace"]) |
        set(table['c']['c']) |
        set(table['c']['n']) |
        set(table['c']['s'])
    )
    posix_table["posixgraph"] = list(s)

    # `Cntrl: [\p{Cc}]`
    s = set(table['c']['c'])
    posix_table["posixcntrl"] = list(s)

    # `Print: [\p{PosixGraph}\p{PosixBlank}--\p{PosixCntrl}]`
    s = set(posix_table["posixgraph"])
    s |= set(posix_table["posixblank"])
    s -= set(posix_table["posixcntrl"])
    posix_table["posixprint"] = list(s)

    # `Word: [\p{alnum}\p{M}\p{Pc}\p{JoinControl}]`
    s = set(posix_table["alnum"])
    for k, v in table['m'].items():
        if not k.startswith('^'):
            s |= set(v)
    s |= set(table["p"]["c"])
    s |= set(posix_table["joincontrol"])
    posix_table['posixword'] = list(s)


def gen_alias(nonbinary, binary, output):
    """Generate alias."""

    prefix = "unicode"
    alias_re = re.compile(r'^#\s+(\w+)\s+\((\w+)\)\s*$')

    categories = nonbinary + binary
    alias = {}
    gather = False
    current_category = None
    line_re = None
    alias_header_re = re.compile(r'^#\s+(\w+)\s+Properties\s*$')
    divider_re = re.compile(r'#\s*=+\s*$')
    posix_props = {
        'binary': {
            'posixalpha': 'alphabetic',
            'posixlower': 'lowercase',
            'posixupper': 'uppercase',
            'posixspace': 'whitespace',
            'blank': 'posixblank',
            'graph': 'posixgraph',
            'print': 'posixprint',
            'word': 'posixword'
        },
        'block': {
            'posixascii': 'basiclatin'
        }
    }
    toplevel = (
        'catalog', 'enumerated', 'numeric', 'miscellaneous'
    )

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'PropertyAliases.txt'), 'r', encoding='utf-8') as uf:
        div = False
        capture = False
        name = None
        for line in uf:
            if div:
                m = alias_header_re.match(line)
                if m:
                    name = format_name(m.group(1))
                    if name in toplevel:
                        capture = True
                        name = '_'
                    elif name in ('binary',):
                        capture = True
                    else:
                        capture = False
                    continue
                div = False
            elif divider_re.match(line):
                div = True
                continue
            elif line.startswith('#') or not line.strip():
                continue
            if capture:
                should_add = False
                data = [format_name(x) for x in line.split('#')[0].split(';')]
                index = 0
                for d in data:
                    if d in categories:
                        should_add = True
                        break
                    index += 1
                if should_add:
                    data[0], data[index] = data[index], data[0]
                    if name not in alias:
                        alias[name] = {}
                    for d in data[1:]:
                        alias[name][d] = data[0]

    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'PropertyValueAliases.txt'), 'r', encoding='utf-8') as uf:
        for line in uf:
            m = alias_re.match(line)
            if m:
                original_name = format_name(m.group(1))
                gather = original_name in categories
                current_category = format_name(m.group(2))
                line_re = re.compile(r'%s\s*;' % m.group(2), re.I)
            if gather and line_re.match(line):
                data = [format_name(x) for x in line.split('#')[0].split(';')]
                if current_category in ('sc', 'blk', 'dt', 'sb', 'wb', 'gcb', 'nt', 'inpc', 'inmc', 'insc'):
                    data[1], data[2] = data[2], data[1]
                elif current_category == 'age' and UNIVERSION_INFO < (6, 1, 0):
                    if data[2] == 'unassigned':
                        data[1] = 'na'
                    else:
                        data[1], data[2] = data[2], 'V' + data[2].replace('.', '_')
                if len(data) == 5 and data[2] in ('yes', 'no') and data[1] in ('n', 'y'):
                    data = ['binary', original_name, data[0]]
                else:
                    data[0] = alias['_'].get(data[0], data[0])
                if data[0] not in alias:
                    alias[data[0]] = {}
                for a in data[2:]:
                    if a == 'n/a':
                        continue
                    if a not in alias[data[0]] and a != data[1]:
                        alias[data[0]][a] = data[1]

    for x in nonbinary:
        if x not in alias:
            alias[x] = {}

    for k, v in posix_props.items():
        for k1, v1 in v.items():
            alias[k][k1] = v1

    alias['binary']['h'] = 'horizspace'
    alias['binary']['v'] = 'vertspace'

    with open(output, 'w', encoding='utf-8') as f:
        f.write(HEADER.format(UNIVERSION, TYPING))
        f.write('%s_alias: dict[str, dict[str, str]] = {\n' % prefix)
        count = len(alias) - 1
        i = 0
        for k1, v1 in sorted(alias.items()):
            f.write('    "%s": {\n' % k1)
            count2 = len(v1) - 1
            j = 0
            for k2, v2 in sorted(v1.items()):
                f.write('        "%s": "%s"' % (k2, v2))
                if j == count2:
                    f.write('\n    }')
                else:
                    f.write(',\n')
                j += 1
            if count2 < 0:
                f.write('    }')
            if i == count:
                f.write('\n}\n')
            else:
                f.write(',\n')
            i += 1

    return alias


def gen_properties(output, files, aliases, ascii_props=False, append=False):
    """Generate the property table and dump it to the provided file."""

    prefix = "ascii" if ascii_props else 'unicode'

    if ascii_props:
        print('=========Ascii Tables=========')
    else:
        print('========Unicode Tables========')
    print('Building: General Category')
    max_range = ASCII_LIMIT if ascii_props else UNICODE_RANGE
    all_chars = ALL_CHARS

    # `L&` or `Lc` won't be found in the table,
    # so initialize 'c' at the start. `&` will have to be converted to 'c'
    # before sending it through.
    table = {'l': {'c': []}}
    itable = {'l': {}}
    with open(os.path.join(HOME, 'unicodedata', UNIVERSION, 'UnicodeData.txt'), 'r', encoding='utf-8') as uf:
        for line in uf:
            data = line.strip().split(';')
            if data:
                i = int(data[0], 16)
                p = data[2].lower()
                if p[0] not in table:
                    table[p[0]] = {}
                    itable[p[0]] = {}
                if p[1] not in table[p[0]]:
                    table[p[0]][p[1]] = []
                if i > max_range[1]:
                    continue
                table[p[0]][p[1]].append(i)
                # Add LC which is a combo of Ll, Lu, and Lt
                if p[0] == 'l' and p[1] in ('l', 'u', 't'):
                    table['l']['c'].append(i)

    s = set()
    for v in table.values():
        for v2 in v.values():
            s.update(v2)
    table['c']['n'] = list(all_chars - s)

    # Create inverse of each category
    for k1, v1 in table.items():
        inverse_category = set()
        for v2 in v1.values():
            s = set(v2)
            inverse_category |= s
        itable[k1]['^'] = list(all_chars - inverse_category)

    # Generate Unicode blocks
    print('Building: Blocks')
    gen_blocks(files['blk'], ascii_props, append, prefix, aliases=aliases)

    # Generate Unicode scripts
    print('Building: Scripts & Script Extensions')
    gen_scripts(
        'Scripts.txt', 'ScriptExtensions.txt', 'scripts', 'script_extensions', files['sc'], files['scx'],
        notexplicit='unknown', ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    # Generate Unicode binary
    print('Building: Binary')
    gen_binary(table, files['binary'], ascii_props, append, prefix, aliases=aliases)

    print('Building: Age')
    gen_age(files['age'], ascii_props, append, prefix, aliases)

    print('Building: East Asian Width')
    gen_enum(
        'EastAsianWidth.txt', 'east_asian_width', files['ea'],
        notexplicit='n', ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    print('Building: Grapheme Cluster Break')
    gen_enum(
        'GraphemeBreakProperty.txt', 'grapheme_cluster_break', files['gcb'], notexplicit='other',
        ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    print('Building: Line Break')
    gen_enum(
        'LineBreak.txt', 'line_break', files['lb'], notexplicit='xx',
        ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    print('Building: Sentence Break')
    gen_enum(
        'SentenceBreakProperty.txt', 'sentence_break', files['sb'], notexplicit='other',
        ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    print('Building: Word Break')
    gen_enum(
        'WordBreakProperty.txt', 'word_break', files['wb'], notexplicit='other',
        ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    print('Building: Indic Positional Category')
    gen_enum(
        'IndicPositionalCategory.txt', 'indic_positional_category', files['inpc'], notexplicit='na',
        ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    print('Building: Indic Syllabic Category')
    gen_enum(
        'IndicSyllabicCategory.txt', 'indic_syllabic_category', files['insc'], notexplicit='other',
        ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    print('Building: Hangul Syllable Type')
    gen_enum(
        'HangulSyllableType.txt', 'hangul_syllable_type', files['hst'], notexplicit='na',
        ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    print('Building: Decomposition Type')
    gen_enum(
        'DerivedDecompositionType.txt', 'decomposition_type', files['dt'], notexplicit='none',
        ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    print('Building: Joining Type')
    gen_enum(
        'DerivedJoiningType.txt', 'joining_type', files['jt'], notexplicit='u',
        ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    print('Building: Joining Group')
    gen_enum(
        'DerivedJoiningGroup.txt', 'joining_group', files['jg'], notexplicit='nonjoining',
        ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    print('Building: Numeric Type')
    gen_enum(
        'DerivedNumericType.txt', 'numeric_type', files['nt'], notexplicit='none',
        ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    print('Building: Numeric Value')
    gen_enum(
        'DerivedNumericValues.txt', 'numeric_values', files['nv'], field=3, notexplicit='nan',
        ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    print('Building: Canonical Combining Class')
    gen_ccc(files['ccc'], ascii_props, append, prefix, aliases=aliases)

    # Generate Quick Check categories
    print('Building: NF* Quick Check')
    gen_nf_quick_check(files['qc'], ascii_props, append, prefix, aliases=aliases)

    # Generate Unicode bidi classes
    print('Building: Bidi Classes')
    gen_bidi(files['bc'], ascii_props, append, prefix)
    print('Building: Bidi Paired Bracket Type')
    gen_enum(
        'BidiBrackets.txt', 'bidi_paired_bracket_type', files['bpt'], notexplicit='n',
        field=2, ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
    )

    if UNIVERSION_INFO >= (11, 0, 0):
        print('Building: Vertical Orientation')
        gen_enum(
            'VerticalOrientation.txt', 'vertical_orientation', files['vo'], notexplicit='r',
            ascii_props=ascii_props, append=append, prefix=prefix, aliases=aliases
        )

    # Convert char values to string ranges.
    char2range(table, is_bytes=ascii_props)
    char2range(itable, is_bytes=ascii_props, invert=False)
    for k1, v1 in itable.items():
        table[k1]['^'] = v1['^']

    with open(files['gc'], 'a' if append else 'w', encoding='utf-8') as f:
        if not append:
            f.write(HEADER.format(UNIVERSION, TYPING))
        # Write out the Unicode properties
        f.write('%s_properties: dict[str, dict[str, str]] = {\n' % prefix)
        count = len(table) - 1
        i = 0
        for k1, v1 in sorted(table.items()):
            f.write('    "%s": {\n' % k1)
            count2 = len(v1) - 1
            j = 0
            for k2, v2 in sorted(v1.items()):
                f.write('        "%s": "%s"' % (k2, v2))
                if j == count2:
                    f.write('\n    }')
                else:
                    f.write(',\n')
                j += 1
            if i == count:
                f.write('\n}\n')
            else:
                f.write(',\n')
            i += 1

    if not append:
        with open(os.path.join(output, '__init__.py'), 'w') as f:
            f.write(HEADER.format(UNIVERSION, ''))
            for x in sorted(files):
                f.write('from .%s import *  # noqa\n' % os.path.basename(files[x])[:-3])


def build_unicode_property_table(output, files, aliases):
    """Build and write out Unicode property table."""

    gen_properties(output, files, aliases)


def build_ascii_property_table(output, files, aliases):
    """Build and write out Unicode property table."""

    gen_properties(output, files, aliases, ascii_props=True, append=True)


def build_tables(output, version=None):
    """Build output tables."""

    set_version(version)

    files = get_files(output)
    nonbinary, binary = discover_categories()

    if not os.path.exists(output):
        os.mkdir(output)

    print('Building: Aliases')
    aliases = gen_alias(nonbinary, binary, files['alias'])

    build_unicode_property_table(output, files, aliases)
    build_ascii_property_table(output, files, aliases)


def set_version(version):
    """Set version."""

    global UNIVERSION
    global UNIVERSION_INFO

    if version is None:
        version = unicodedata.unidata_version

    UNIVERSION = version
    UNIVERSION_INFO = tuple([int(x) for x in UNIVERSION.split('.')])


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='unipropgen', description='Generate a unicode property table.')
    parser.add_argument('--version', action='version', version="%(prog)s " + __version__)
    parser.add_argument('--unicode-version', default=None, help='Force a specific Unicode version.')
    parser.add_argument('output', default=None, help='Output file.')
    args = parser.parse_args()

    build_tables(args.output, args.unicode_version)
