---
icon: lucide/hand
---
# Introduction

## Importing

Backrefs comes in two flavors: `bre` (a Re wrapper) and `bregex` (a Regex wrapper). You can import either one simply
by importing it from the `backrefs` library. Regex must be installed if using `bregex`.

```py3
from backrefs import bre
from backrefs import bregex
```

## Searches

Backrefs preprocesses search patterns looking for new syntax that it replaces with compatible regular expressions for
the given regular expression engine. For instance, Backrefs implements the `\R` reference in Re, and when compiled, we
get an Re object with a regular expression pattern that captures various line breaks.

```py play
bre.compile(r'\R')
```

It can be seen that the Backrefs object is simply wrapped around an Re compiled pattern, and we see that `\R` was
replaced with `(?:\\r\\n|(?!\\r\\n)[\\n\\v\\f\\r\\x85\\u2028\\u2029])`.

This basic approach is used to implement all sorts of references from Unicode properties:

```py play
bre.compile(r'test \p{Cs}')
```

To start and end word boundaries:

```py play
bre.compile(r'\mtest\M')
```

A compiled Backrefs object has all the same functions as the regular expression's object, so you can use it in the same
way to perform splits, matches, substitutions, and anything else.

If we wanted to match a line ending, we could call `prefixmatch` (or the legacy alias of `match`) or `search`.

```py play
bre.compile(r'\R').match('\n')
```

Matches can also be preformed without pre-compiling.

```py play
bre.match(r'\R', '\n')
```

## Replacements

Replace templates are a little different than search patterns and require a bit more control to accomplish some of the
replace features which is why a Backrefs object is wrapped around the returned Re object. The wrapper mirrors the
regular expression object's shadows so that it can intercept the calls to `sub`, `subn`, etc. to process replacements
before passing them to the regular expression engine.

Like with searches, Backrefs preprocesses the replace string before passing it to the regular expression engine. Once
Backrefs has parsed and altered the string as needed, it is then passed to the regular expression engine with the
compiled search pattern to extract string literals and the group mapping. With this, Backrefs can assemble the
replacement and inject new functionality on substitution.

For instance, here we use the start and end markers of `\C` and `\E` to specify that the content in between should be
capitalized. Traditionally, `\U` and `\E` is used, but since `\U` is a Unicode escape in Python, we chose to use `\C`.

```py play
pattern = bre.compile(r'(\p{Letter}+)')
pattern.sub(r'\C\1\E', 'sometext')
```

## Format Replacements

Backrefs allows for replacement string templates to use a format string format in both Re and Regex. This feature is a
Regex library specific feature that we mimic in Re, but [enhance in both](#enhancements).

Originally, this feature was developed in Regex to allow accessing specific captures of a group when multiple captures
are made. For Regex, this makes a lot of sense as the library actually tracks all captures for a group. Each capture
can be indexed individually using the format string format.

```py play
regex.subf(r"(?:(\w+) ){2}(\w+)", "{0} => {1[0]} {1[1]} {2}", "foo bar baz")
regex.subf(r"(?:(?P<word1>\w+) ){2}(?P<word2>\w+)", "{0} => {word1[0]} {word1[1]} {word2}", "foo bar baz")
```

The Re engine does not track multiple captures for a single group -- something we cannot change -- and instead only
captures the last capture. Format strings in Re will only provide the last capture in Re. If you were to try and index
into different captures instead of accepting the default, you will only be able to reference the last one. If at some
point in the future, Re begins to track all captures, then this feature will be updated to reflect such changes.

```py play
bre.subf(r"(?:(\w+) ){2}(\w+)", "{0} => {1[0]} {1[-1]} {2}", "foo bar baz")
```

While Re does not really expose multiple captures, this doesn't mean the format string is of no use to Re. For one, the
format string syntax may be generally preferred as a less cumbersome format for specifying groups by index or by name.
By default, Python's Re requires groups to be specified via `\1` or `\g<name>`, while the format syntax simply requires
  `{1}` or `{name}`. Escaping braces is the same as in any format string and requires the user to use two `{{` or `}}`.

When using Backrefs' format replace, it should feel similar to Regex's format replace, except you will generally use raw
strings to allow for back slash references.

```py play
bregex.subf(r"(\w+) (\w+)", r"{0} => {2} {1}", "foo bar")
bregex.subf(r"(?P<word1>\w+) (?P<word2>\w+)", r"{word2} {word1}", "foo bar")
```

You can index into groups that have multiple captures, and while it works for both Re and Regex, it is only useful when
using `bregex`.

```py play
bregex.subf(r"(\w)+ (\w+)", "{0} => {2} {1[0]}", "foo bar")
```

You can also use `{} {}` which is the same as `{0} {1}`.

```py play
bre.subf(r"(\w+) (\w+)", r"{} => \C{} {}\E", "foo bar")
```

Backrefs also provides an `expand` variant for format templates called `expandf`.

```py play
pattern = bre.compile_search(r"(\w+) (\w+)")
m = pattern.match('foo bar')
bre.expandf(m, r"{0} => {2} {1}")
```

### Enhancements

Backrefs' implementation is a little different than Regex's default implementation. Below we cover what is different and
why.

1.  Regex's original implementation is very much like it's non-format style replacement accept for two differences: you
    can access individual captures and you cannot use Python string back references such as specifying Unicode via
    `\u<code>`, etc. In Backrefs, we've enhanced the syntax -- for both Re and Regex -- to allow back references to work
    along side brace replacements. This means you can use string back references and built-in Backrefs features like
    `\C...\E` or `\L...\E`.

    ```py play
    bre.subf(r"(\w+) (\w+)", r"{0} => \C{2} {1}\E", "foo bar")
    bregex.subf(r"(\w+) (\w+)", r"{0} => \C{2} {1}\E", "foo bar")
    ```

2.  The second enhancement that Backrefs adds is the ability to use format string alignment features. In the following
    example, we center the replacement and pad it out to 8 characters using `|` for the padding. We also use casing
    references (`\C...\E`) to capitalize the replacement group.

    ```py play
    bregex.subf(r'(test)', r'\C{0:|^8}\E', 'test')
    ```

    Backrefs implements a subset of the [Format Specification Mini-Language][format-spec] (`format_spec`) that allows
    for these features. As regular expression replacements are only working with string replacements (or byte strings),
    only string features are available with the `format_spec`, and only a subset of those are particularly useful.

    ```
    replacement_field ::=  "{" [field_name] ["!" conversion] [":" format_spec] "}"
    field_name        ::=  arg_name ("." attribute_name | "[" element_index "]")*
    arg_name          ::=  [identifier | integer]
    attribute_name    ::=  identifier
    element_index     ::=  integer | index_string
    index_string      ::=  <any source character except "]"> +
    conversion        ::=  "r" | "s" | "a"
    format_spec       ::=  <described in the next section>
    ```

    ```
    format_spec ::=  [[fill]align][0][width][type]
    fill        ::=  <any character>
    align       ::=  "<" | ">" | "^"
    width       ::=  integer
    type        ::=  "s"
    ```

3.  Lastly, our implementation of the [Format Specification Mini-Language][format-spec] (`format_spec`) allows format
    strings to work for byte strings as well as Unicode strings. This is something that Regex does not allow without
    Backrefs.

    ```py play
    bre.subf(br'(test)', br'\C{0:|^8}\E', b'test')
    ```

    > [!note] Conversion Syntax and Bytes
    > In almost all instances, using conversion types (`{!s}`, etc.) won't make sense in a regular expression replace
    > as the objects will already be strings in the needed format, but if you were to use a conversion using byte
    > strings, when converting from `bytes` to `str`, ASCII will be the assumed encoding, and the object or Unicode
    > string would be encoded using the `backslashreplace` option as well.

## Advanced Usage

As noted, Backrefs wraps the regular expression object on compile with its own object. This is so it can provide
the replace features seamlessly without the user having to do anything extra. But if you only wanted the search
features, the `compile_search` method can be used to compile the pattern and directly return the regular expression
object with no wrapper:

```py play
bre.compile_search(r'(\p{ascii}+)')
```

Conversely, we could only use the replace features by compiling the pattern normally and giving it to the Backrefs API
to create a replace object:

```py play
pattern = re.compile(r'(\w+)')
replace = bre.compile_replace(pattern, r'\C\1\E')
pattern.sub(replace, 'text')
```

You can also compile a replacement object directly from a `backrefs` object:

```py play
pattern = bre.compile(r'(\w+)')
replace = pattern.compile(r'\C\1\E')
pattern.sub(replace, 'text')
```

To pre-compile a format replace template, you can use the Backrefs' `compile_replace` method with the `FORMAT` flag.

```py play
pattern = bre.compile_search(r"(\w+) (\w+)")
replace = bre.compile_replace(pattern, r"{0} => {2} {1}", bre.FORMAT)
m = pattern.match("foo bar")
replace(m)
```

Pre-compiled pattern objects can also create a compiled format replace object using the `FORMAT` flag.

```py play
pattern = bre.compile(r"(?P<word1>\w+) (?P<word2>\w+)")
replace = pattern.compile(r"\c{word2} \c{word1}", bre.FORMAT)
pattern.subf(replace, "foo bar")
```
