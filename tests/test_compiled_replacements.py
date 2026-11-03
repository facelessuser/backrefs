"""Compiled replacements must keep their original search pattern."""
import pytest
from backrefs import bre


@pytest.mark.parametrize('engine', ['bre', 'bregex'])
@pytest.mark.parametrize('method', ['sub', 'subn', 'subf', 'subfn'])
@pytest.mark.parametrize('as_bytes', [False, True])
@pytest.mark.parametrize('auto_compile', [False, True])
def test_foreign_compiled_replacement(engine, method, as_bytes, auto_compile):
    """Reject templates whose named captures belong to another pattern."""

    module = bre if engine == 'bre' else pytest.importorskip('backrefs.bregex')
    first = r'(?P<first>a)(?P<second>b)'
    second = r'(?P<second>b)(?P<first>a)'
    text = 'ba'
    template = '{first}' if method in ('subf', 'subfn') else r'\g<first>'
    if as_bytes:
        first, second, text, template = (x.encode() for x in (first, second, text, template))
    source = module.compile(first)
    target = module.compile(second, auto_compile=auto_compile)
    replacement = source.compile(template, module.FORMAT if method in ('subf', 'subfn') else 0)

    with pytest.raises(ValueError, match="Pattern hash doesn't match"):
        getattr(target, method)(replacement, text)


@pytest.mark.parametrize('engine', ['bre', 'bregex'])
@pytest.mark.parametrize('method', ['sub', 'subn', 'subf', 'subfn'])
@pytest.mark.parametrize('as_bytes', [False, True])
@pytest.mark.parametrize('auto_compile', [False, True])
def test_matching_compiled_replacement(engine, method, as_bytes, auto_compile):
    """Matching templates still work without automatic string compilation."""

    module = bre if engine == 'bre' else pytest.importorskip('backrefs.bregex')
    pattern = r'(?P<first>a)(?P<second>b)'
    text, expected = 'ab', 'a'
    template = '{first}' if method in ('subf', 'subfn') else r'\g<first>'
    if as_bytes:
        pattern, text, expected, template = (x.encode() for x in (pattern, text, expected, template))
    target = module.compile(pattern, auto_compile=auto_compile)
    replacement = target.compile(template, module.FORMAT if method in ('subf', 'subfn') else 0)
    if method in ('subn', 'subfn'):
        expected = (expected, 1)
    assert getattr(target, method)(replacement, text) == expected
