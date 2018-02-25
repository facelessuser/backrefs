# User Guide

## Overview

Backrefs is a wrapper around Python's built-in [Re][re] and the 3rd party [Regex][regex] library.  Backrefs adds various additional back references (and a couple other features) that are known to some regular expression engines, but not to Python's Re and/or Regex.  The supported back references actually vary depending on the regular expression engine being used as the engine may already have support for some, or things that prevent implementation of a feature.

It is important to note that Backrefs doesn't alter the regular expression engine that it wraps around, it is essentially a string processor that looks for certain symbols in a regular expression search or replace string, and alters the pattern before sending it to the regular expression engine.

For instance, if we used `\m` in our regular expression, it would be transformed into `\b(?=\w)`.

```pycon3
>>> bre.compile(r'test \m').pattern
re.compile('test \\b(?=\\w)')
```

Or if we used a Unicode property, it would be transformed into a character group:

```pycon3
>>> bre.compile(r'test \p{Cs}').pattern
re.compile('test [\ud800\udb7f-\udb80\udbff-\udc00\udfff]')
```

Replace templates are a little different than searches and require a bit more control to accomplish some of the replace features. Backrefs, like with searches, processes the string before passing it through the regular expression engine. Once Backrefs has parsed and altered the string as needed, it is then passed the regular expression engine to extract string literals and the group mapping (search groups to replace group placeholders). Backrefs will then return a replace object that should be used to apply the replace. The object will handle applying casing (upper or lower) to the returned captured groups, and assemble the desired string output. For these reasons, Backrefs requires you to compile your replaces and use the returned replace object if you want to take advantage of replace features.

```pycon3
>>> pattern = bre.compile_search(r'(\p{Letter}+)')
>>> replace = bre.compile_replace(pattern, r'\C\1\E')
>>> text = pattern.sub(replace, 'sometext')
'SOMETEXT'
```

## Using Backrefs

Depending on which regular expression engine you are using (Re or Regex), you can import the appropriate module.

```py3
from backrefs import bre
from backrefs import bregex
```

Backrefs can be applied to search patterns and/or replace patterns. You can control whether you want to use search augmentation, replace augmentation, or both.

### Search Patterns

To augment the search pattern of Re or Regex to utilize search back references, you can use Backrefs to compile the search. This will apply a preprocessor to the pattern and replace the back references (or other special syntax) with the appropriate content to construct a valid regular expression for Re or Regex. It will then return a valid compiled pattern for the respective regular expression engine. Since the return is a valid compiled pattern, you can use it as expected.

```py3
>>> pattern = bre.compile_search(r'\p{Letter}+', bre.UNICODE)
>>> pattern.match('whatever') is not None
True
```

### Replace Templates

Backrefs also provides special back references for replace templates as well. In order to utilize these back references, the template string must be run through a compiler as well. The replace compiler will run a preprocessor on the replace template that will strip out the back references and augment the template accordingly creating a valid replace template. Then it will return a replace object that can be used in place of your replace string. When used as your replace, the object will properly apply all the replace back references to your returned string and insert matched groups into the template.  These replace objects can be passed into `sub`, `subn` etc.

Search templates must be run through the compiler with an associated compiled search pattern so that it can properly map to the groups in your search pattern.

```pycon3
>>> pattern = bre.compile_search(r'(\p{Letter}+)')
>>> replace = bre.compile_replace(pattern, r'\C\1\E')
>>> text = pattern.sub(replace, 'sometext')
'SOMETEXT'
```

Since compiled replaces are not template strings, but functions, you wont be able to apply compiled replaces via `#!py m.expand(replace)`. Instead, you can use the compiled replace directly.

```pycon3
>>> pattern = bre.compile_search(r'(\p{Letter}+)')
>>> replace = bre.compile_replace(pattern, r'\C\1\E')
>>> m = pattern.match('sometext')
>>> replace(m)
'SOMETEXT'
```

If you have a one time expand, and don't feel like pre-compiling, you can use Backrefs `expand` method (it can also take pre-compiled patterns as well).

```pycon3
>>> pattern = bre.compile_search(r'(\p{Letter}+)')
>>> m = pattern.match('sometext')
>>> bre.expand(m, r'\C\1\E')
'SOMETEXT'
```

### Search & Replace Together

If you plan on using both the search and replace features, using `compile_search` and `compile_replace` can be a little awkward. If you wish to use something a bit more familiar, you can use the `compile` function to create a pattern object that mimics Re and Regex's pattern object. Once created, it will work very similar to how Re and Regex pattern objects work.  It will also auto compile replace patterns for you:

```pycon3
>>> pattern = bre.compile(r'(\p{Letter}+)')
>>> pattern.sub(r'\C\1\E', 'sometext')
'SOMETEXT'
```

If needed, you can use the object's `compile` function to pre-compile the replace patterns:

```pycon3
>>> pattern = bre.compile(r'(\p{Letter}+)')
>>> replace = pattern.compile(r'\C\1\E')
>>> pattern.sub(replace, 'sometext')
'SOMETEXT'
```

If you want to disable the patterns use of replace back references, you can disable the pre-compile of replace templates:

```pycon3
>>> pattern = bre.compile(r'(\p{Letter}+)', auto_compile=False)
>>> pattern.sub(r'\C\1\E', 'sometext')
'\\Csometext\\E'
```

### Other Functions

Backrefs exposes most of the usual functions which Backrefs is wrapped around.  For instance, Backrefs wraps around `purge` so that it can purge its cache along with the regular expression engine's cache.

Backrefs also wraps around the global matching functions. So if you have a one time `finditer`, `match`, `sub`, `search`, or other operation, Backrefs provides wrappers for these methods too.  The wrappers will compile the search and replace patterns for you on the fly, but they will also accept and pass pre-compiled patterns through as well.  They should take all the flags and options your chosen regular expression engine normally accepts with the same names and positions.

```pycon3
>>> bre.sub(r'(\p{Letter}+)', r'\C\1\E', 'sometext')
SOMETEXT
```

In general, all options and flags for any of the compile, search, or replace wrappers should be the same as your actual regular expression engine.  They are mirrored in the `bre` and `bregex` library to save you from having to import the the original `re` and `regex` respectively, but you could just as easily use the original flags if desired.

In order to escape patterns formulated for Backrefs, you can simply use your regular expressions built-in escape method or the one mirrored in Backrefs; they are the same.

```pycon3
>>> pattern = bre.compile_search(bre.escape(r'(\p{Letter}+)'))
>>> bre.sub(pattern, 'found it!', '(\\p{Letter}+)')
'found it!'
```

### Format Replacements

!!! note "Backrefs' Format Differences"
    Even though this is a Regex specific feature, this replace format is supported by Backrefs for both Regex *and* Re with some slight differences.  These differences apply to both Regex as well as Re as Backrefs must augment the format to allow casing back references.

    1. Backrefs does not use Python's string format directly but mimics the feel for inserting groups into the final output.
    2. Indexing into different captures in Re is limited to `0` or `-1` since Re *only* maintains the last capture.
    3. Raw string (`#!py3 r"..."`) handling for format replace is a bit different for Backrefs compared to Regex. Regex treats format strings as simply strings instead of as a regular replace template. So while in a regular replace template you can use `\n` to represent a new line, in format strings, you'd have use a literal new line or use a normal string (`#!py3 "..."`) with `\n`. Since Backrefs allows for its own special back references in format strings, it will also process standard string and Unicode string back references as well.

The Regex module offers a feature where you can apply replacements via a format string style.

```pycon3
>>> regex.subf(r"(\w+) (\w+)", "{0} => {2} {1}", "foo bar")
'foo bar => bar foo'
>>> regex.subf(r"(?P<word1>\w+) (?P<word2>\w+)", "{word2} {word1}", "foo bar")
'bar foo'
```

You can even index into groups that have multiple captures.

```pycon3
>>> regex.subf(r"(\w)+ (\w+)", "{0} => {2} {1[0]}", "foo bar")
'foo bar => bar f'
```

Backrefs supports this functionality in a similar way, and you can do it with Regex *or* Re. This allows you to use case back references and the format style replacements.


```pycon3
>>> bre.subf(r"(\w+) (\w+)", r"{0} => \C{2} {1}\E", "foo bar")
'foo bar => BAR FOO'
>>> bre.subf(r"(?P<word1>\w+) (?P<word2>\w+)", r"\c{word2} \c{word1}", "foo bar")
'Bar Foo'
```

You can also use `{} {}` which is the same as `{0} {1}`.

```pycon3
>>> bre.subf(r"(\w+) (\w+)", r"{} => \C{} {}\E", "foo bar")
'foo bar => FOO BAR'
```

To pre-compile a format replace template, you can use the Backrefs' `compile_replace` method with the `FORMAT` flag.

```pycon3
>>> pattern = bre.compile_search(r"(\w+) (\w+)")
>>> replace = bre.compile_replace(pattern, r"{0} => {2} {1}", bre.FORMAT)
>>> m = pattern.match("foo bar")
>>> replace(m)
'foo bar => bar foo'
```

Or using Backrefs' pattern object:

```pycon3
>>> pattern = bre.compile(r"(\w+) (\w+)")
>>> pattern.subf(r"{0} => \C{2} {1}\E", "foo bar")
'foo bar => BAR FOO'
```

Pre-compiling a format replace template with Backref's pattern object:

```pycon3
>>> pattern = bre.compile(r"(?P<word1>\w+) (?P<word2>\w+)")
>>> replace = pattern.compile(r"\c{word2} \c{word1}", bre.FORMAT)
>>> pattern.subf(replace, "foo bar")
'Bar Foo'
```

Backrefs also provides an `expand` variant for format templates called `expandf`.

```pycon3
>>> pattern = bre.compile_search(r"(\w+) (\w+)")
>>> m = pattern.match('foo bar')
>>> bre.expandf(m, r"{0} => {2} {1}")
'foo bar => bar foo'
```

## Search Back References

Each supported regular expression engine's supported search features vary, so features are broken up to show what is specifically added for Re and for Regex.

### Re

!!! info "`LOCALE` and Character Properties"
    Backrefs does not consider `LOCALE` when inserting POSIX or Unicode properties. In byte strings, Unicode properties will be truncated to the ASCII range of `\xff`. POSIX properties will use either Unicode categories or POSIX categories depending on whether the `UNICODE` flag is set. If the `LOCALE` flag is set, it is considered **not** Unicode. Keep in mind that Backrefs doesn't stop `LOCALE` from being applied, only that Backrefs inserts its categories as either Unicode or ASCII only.

Back\ References      | Description
--------------------- |------------
'\e'                  | Escape character `\x1b`.
`\c`                  | Shortcut for the uppercase [POSIX character class](#posix-style-properties) `[[:upper:]]`.  ASCII or Unicode when re Unicode flag is used.  Can be used in character classes `[]`.
`\l`                  | Shortcut for the lowercase [POSIX character class](#posix-style-properties) `[[:lower:]]`.  ASCII or Unicode when re Unicode flag is used.  Can be used in character classes `[]`.
`\C`                  | Shortcut for the inverse uppercase [POSIX character class](#posix-style-properties) `[[:^upper:]]`.  ASCII or Unicode when re Unicode flag is used.  Can be used in character classes `[]`.
`\L`                  | Shortcut for the inverse lowercase [POSIX character class](#posix-style-properties) `[[:^lower:]]`.  ASCII or Unicode when re Unicode flag is used.  Can be used in character classes `[]`.
`\Q...\E`             | Quotes (escapes) text for regular expression.  `\E` signifies the end of the quoting. Affects any and all characters no matter where in the regular expression pattern it is placed.
`\p{UnicodeProperty}` | Unicode property character class. Can be used in character classes `[]`. See [Unicode Properties](#unicode-properties) for more info.
`\pX`                 | Unicode property character class where `X` is the uppercase letter that represents the General Category property.  For instance, `\pL` would be equivalent to `\p{L}` or `\p{Letter}`.
`\P{UnicodeProperty}` | Inverse Unicode property character class. Can be used in character classes `[]`. See [Unicode Properties](#unicode-properties) for more info.
`\PX`                 | Inverse Unicode property character class where `X` is the uppercase letter that represents the General Category property. For instance, `\PL` would be equivalent to `\P{L}` or `\P{Letter}`.
`[[:alnum:]]`         | Though not really a back reference, support for POSIX style character classes is available. See [POSIX Style Properties](#posix-style-properties) for more info.
`\N{UnicodeName}`     | Named characters are are normally ignored in Re, but Backrefs adds support for them.
`\m`                  | Start word boundary. Translates to `\b(?=\w)`.
`\M`                  | End word boundary. Translates to `\b(?<=\w)`.

### Regex

!!! note
    Regex already natively supports `\p{...}`, `\P{...}`, `\pX`, `\PX`, and `\N{...}`, so Backrefs does not attempt to add this to search patterns.

    `\m` and `\M` are also features already present in Regex.

    `\c`, `\l`, `L` and `L` are not used as some of these flags are already taken by Regex itself  These references are just shortcuts for the related POSIX properties in Backrefs.

Back\ References | Description
---------------- | -----------
`\e`             | Escape character `\x1b`.
`\Q...\E`        | Quotes (escapes) text for regular expression.  `\E` signifies the end of the quoting. Affects any and all characters no matter where in the regular expression pattern it is placed.
`\R`             | Generic line breaks. When searching a Unicode string, this will use an atomic group and match `(?>\r\n|\n|\x0b|\f|\r|\x85|\u2028|\u2029)`, and when applied to byte strings, this will match `(?>\r\n|\n|\x0b|\f|\r|\x85)`. Because it uses atomic groups, which Re does not support, this feature is only for Regex.

## Replace Back References

The replace back references below apply to both Re **and** Regex and are essentially non-specific to the regular expression engine being used.  Casing is applied to both the literal text and the replacement groups within the replace template.  In most cases you'd only need to wrap the groups, but it may be useful to apply casing to the literal portions if you are dynamically assembling replacement patterns.

!!! info "`LOCALE` and Casing"
    `LOCALE` is not considered when applying character casing. Unicode casing is applied in Unicode strings and ASCII casing is applied to byte strings.

Back\ References     | Description
---------------------|-------------
`\c`                 | Uppercase the next character.
`\l`                 | Lowercase the next character.
`\C...\E`            | Apply uppercase to all characters until either the end of the string or the end marker `\E` is found.
`\L...\E`            | Apply lowercase to all characters until either the end of the string or the end marker `\E` is found.
`\U`                 | Wide Unicode character `\U00000057`. Re doesn't translate this notation in raw strings (`#!py3 r"..."`), and Regex doesn't in format templates in raw strings (`#!py3 r"{} {}"`).  This adds support for them.
`\u`                 | Narrow Unicode character `\u0057`. Re doesn't translate this notation in raw strings (`#!py3 r"..."`), and Regex doesn't in format templates in raw strings (`#!py3 r"{} {}"`).  This adds support for them.
`\x`                 | Byte character `\x57`. Re doesn't translate this notation in raw strings (`#!py3 r"..."`), and Regex doesn't in format templates in raw strings (`#!py3 r"{} {}"`).  This adds support for them.
`\N{UnicodeName}`    | Named characters are are normally ignored in Re, but Backrefs adds support for them.

!!! tip "Tip"
    Complex configurations of casing should work fine.

    - `\L\cTEST\E` --> `Test`
    - `\c\LTEST\E` --> `Test`
    - `\L\cTEST \cTEST\E` --> `Test Test`

## Unicode Properties

A number of various Unicode properties are supported in Backrefs, but only for Re as Regex already has its own implementation of Unicode properties.

Supported\ Properties       | Aliases
--------------------------- | -------
`Age`                       | &nbsp;
`Bidi_class`                | `bc`
`Binary`                    | &nbsp;
`Block`                     | `blk`
`Canonical_Combining_Class` | `ccc`
`Decomposition_Type`        | `dt`
`East_Asian_Width`          | `ea`
`General_Category`          | `gc`
`Grapheme_Cluster_Break`    | `gcb`
`Hangul_Syllable_Type`      | `hst`
`Joining_Group`             | `jg`
`Joining_Type`              | `jt`
`Line_Break`                | `lb`
`NFC_Quick_Check`           | `nfcqc`
`NFD_Quick_Check`           | `nfdqc`
`NFKC_Quick_Check`          | `nfkcqc`
`NFKD_Quick_Check`          | `nfkdqc`
`Numeric_Type`              | `nt`
`Numeric_Value`             | `nv`
`Script`                    | `sc`
`Script_Extensions`         | `scx`
`Sentence_Break`            | `sb`
`Word_Break`                | `wb`

!!! note
    The Binary property is not actually a property, but a group of different properties with binary characteristics.

Exhaustive documentation on all these properties and their values is not currently provided. In general, we'll cover the syntax rules, and [special exceptions](#special-syntax-exceptions) to those rules for specific properties. Though we will outline all the values for General Category, we will not outline all of the valid values for the other properties. You can look at [Perl's Unicode property documentation][perl-uniprops] to get an idea of what values are appropriate for a given property, but keep in mind, syntax may vary from Perl's syntax.

Unicode properties are specific to search patterns and can be used to specify a request to match all the characters in a specific Unicode property. Unicode properties can be used in byte strings, but the patterns will be restricted to the range `\x00-\xff`.

If you are using a narrow python build, your max Unicode value will be `\uffff`.  Unicode blocks above that limit will not be available.  Also Unicode values above the limit will not be available in character classes either. If you are using a wide build, you should have access to all Unicode values.

### Syntax

Unicode properties can be specified with the format: `\p{property=value}`, `\p{property:value}`. You can also do inverse properties by using the `^` character (`\p{^property=value}`) or by using a capital `P` (`\P{property=value}`. `\P{property:value}`).

Unicode properties may only have one property specified between the curly braces.  If you want to use multiple properties to capture a singe character, create a character class: `[\p{UnicodeProperty}\p{OtherUnicodeProperty}]`.

When specifying a property, the property and value matching is case insensitive and characters like `[ -_]` will be stripped out.  So the following are all equivalent: `\p{Uppercase_Letter}`, `\p{Uppercase-letter}`, `\p{UPPERCASELETTER}`, `\p{upper case letter}`.

There are a number of binary properties. In general, binary properties are specified by stating the binary property and a boolean value. True values can be `Yes`, `Y`, `True`, or `T`. False values can be `No`, `N`, `False`, or `F`. For example, to specify characters that are "alphabetic", we can use `\p{Alphabetic: Y}`. To specify characters that are **not** "alphabetic": `\p{Alphabetic: N}`.

### Special Syntax Exceptions

General Category, Script, Blocks, and Binary all can be specified by their value alone: `\p{value}`, but they will be evaluated in the following order to resolve name conflicts as some the same value that is used in Script may be used in Blocks etc.

1. General Category
2. Script
3. Blocks
4. Binary

Script and Binary properties can also be defined in the format `IsValue`.  For instance, if we wanted to match characters in the `Latin` script, we could use the syntax `\p{IsLatin}`, which would be the same as `\p{Latin}` or `\p{scx: Latin}`.  For Binary properties, `\p{IsAlphabetic}` is the same as `\p{Alphabetic: Y}` or `\p{Alphabetic}`.

!!! note
    If you use the form `\p{Latin}` or `\p{IsLatin}` for Script, you will get `Scripts` on Python 2 and `Scripts_Extensions` on Python 3. This is because Python 2 uses Unicode version 5.2.0 which does not define `Scripts_Extensions`.

Block properties have a similar short form as Script and Binary properties.  For Blocks you can use `InValue` to specify a block. If we wanted to match characters in the `Basic_Latin` block, we could use the syntax `\p{InBasic_Latin}`. This would be the same as `\p{Block: Basic_Latin}` or `\p{Basic_Latin}`.

Lastly, you can specify general category properties in the form `\pX` where `X` is the single letter terse property form. In this form, you can only use the single character values. So you could specify `Letter`, whose terse form is `L` with `\pL`, but cannot specify `Cased_Letter` which has a terse form of `Lc`.

See the table below to see all the Unicode General Category values and their terse forms.

Verbose\ Property\ Form            | Terse\ Property\ Form
---------------------------------- | ------------------------------
 `Other`                           | `C`
 `Control`                         | `Cc`
 `Format`                          | `Cf`
 `Surrogate`                       | `Cs`
 `Private_Use`                     | `Co`
 `Unassigned`                      | `Cn`
 `Letter`                          | `L`
 `Cased_Letter`                    | `L&` or `Lc`
 `Uppercase_Letter`                | `Lu`
 `Lowercase_Letter`                | `Ll`
 `Titlecase_Letter`                | `Lt`
 `Modifier_Letter`                 | `Lm`
 `Other_Letter`                    | `Lo`
 `Mark`                            | `M`
 `Nonspacing_Mark`                 | `Mc`
 `Spacing_Mark`                    | `Me`
 `Enclosing_Mark`                  | `Md`
 `Number`                          | `N`
 `Decimal_Number`                  | `Nd`
 `Letter_Number`                   | `Nl`
 `Other_Number`                    | `No`
 `Punctuation`                     | `P`
 `Connector_Punctuation`           | `Pc`
 `Dash_Punctuation`                | `Pd`
 `Open_Punctuation`                | `Ps`
 `Close_Punctuation`               | `Pe`
 `Initial_Punctuation`             | `Pi`
 `Final_Punctuation`               | `Pf`
 `Other_Punctuation`               | `Po`
 `Symbol`                          | `S`
 `Math_Symbol`                     | `Sm`
 `Currency_Symbol`                 | `Sc`
 `Modifier_Symbol`                 | `Sk`
 `Other_Symbol`                    | `So`
 `Separator`                       | `Z`
 `Space_Separator`                 | `Zs`
 `Line_Separator`                  | `Zl`
 `Paragraph_Separator`             | `Z`

### POSIX Style Properties

A number of POSIX property names are also available in the form `[:posix:]`. Inverse properties are also available in the form `[:^posix:]`. These properties must only be included in a character class: `[[:upper:]a-z]`. There are two definitions for a given POSIX property: ASCII and Unicode. The Unicode definitions leverage Unicode properties and are only used if the pattern is a Unicode string **and** the regular expression's `UNICODE` flag is set.  In Python 3, the default is Unicode unless the `ASCII` flag is set (the `LOCALE` flag is the equivalent of not having `UNICODE` set).

The Unicode variants of the POSIX properties are also available via the `\p{...}` form.  There are some name collisions with existing Unicode properties like `punct` which exists as both a name for a Unicode property and a slightly different POSIX property. To access the POSIX property, you should prefix the name with `posix`: `\p{PosixPunct}`. It should be noted that you can use the `posix` prefix to access any of the POSIX properties, even if there is no name collision. The POSIX properties are treated as [binary Unicode properties](#binary).


\[:posix:] | \\p\{Posix} | ASCII                                             | Unicode
---------- | ----------- | ------------------------------------------------- | -------
`alnum`    | `Alnum`     | `[a-zA-Z0-9]`                                     | `[\p{L&}\p{Nd}]`
`alpha`    | `Alpha`     | `[a-zA-Z]`                                        | `[\p{L&}]`
`ascii`    | `ASCII`     | `[\x00-\x7F]`                                     | `[\x00-\x7F]`
`blank`    | `Blank`     | `[ \t]`                                           | `[\p{Zs}\t]`
`cntrl`    | `Cntrl`     | `[\x00-\x1F\x7F]`                                 | `[\p{Cc}]`
`digit`    | `Digit`     | `[0-9]`                                           | `[\p{Nd}]`
`graph`    | `Graph`     | `[\x21-\x7E]`                                     | `[^\p{Z}\p{C}]`
`lower`    | `Lower`     | `[a-z]`                                           | `[\p{Ll}]`
`print`    | `Print`     | `[\x20-\x7E]`                                     | `[\P{C}]`
`punct`    | `Punct`     | ``[!\"\#$%&'()*+,\-./:;&lt;=&gt;?@\[\\\]^_`{}~]`` | `[\p{P}\p{S}]`
`space`    | `Space`     | `[ \t\r\n\v\f]`                                   | `[\p{Z}\t\r\n\v\f]`
`upper`    | `Upper`     | `[A-Z]`                                           | `[\p{Lu}]`
`xdigit`   | `XDigit`    | `[A-Fa-f0-9]`                                     | `[A-Fa-f0-9]`

--8<-- "links.md"
