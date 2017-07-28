# User Guide

## Overview

Backrefs is a wrapper around Python's built-in [Re][re] and the 3rd party [Regex][regex] library.  Backrefs adds various additional back references that are known to some regular expression engines, but not to Python's Re or Regex.  The supported back references actually vary depending on the regular expression engine being used as the engine may already have support for some.

## Using Backrefs

Depending on which regular expression engine you are using (Re or Regex), you can import the appropriate module.

```python
from backrefs import bre
from backrefs import bregex
```

Backrefs provides a wrapper for all of Re's and Regex's normal functions such as `match`, `sub`, etc., but is recommended to pre-compile your search patterns **and** your replace patterns for the best performance; especially if you plan on reusing the same pattern multiple times.  As Re and Regex does cache a certain amount of the non-compiled calls you will be spared from some of the performance hit, but Backrefs does not cache the preprocessing of search and replace patterns.

To use pre-compiled functions, you compile the search pattern with `compile_search`.  If you want to take advantage of replace Backrefs, you need to compile the replace pattern as well.  Notice the compiled pattern is fed into the replace pattern; you can feed the replace compiler the string representation of the search pattern as well, but the compiled pattern will be faster and is the recommended way.

For the sake of demonstration, the library for Re will be used.

To compile search **and** replace patterns, you can use the `compile_search` and `compile_replace` functions.

```python
pattern = bre.compile_search(r'somepattern', flags)
replace = bre.compile_replace(pattern, r'\1 some replace pattern')
```

Then you can use the complied search and replace patterns!

```python
text = pattern.sub(replace, r'sometext')
```

or

```python
m = pattern.match(r'sometext')
if m:
    text = replace(m)  # similar to m.expand(template)
```

To use the non-compiled search/replace functions, you call them just as you would in Re; the names are the same.  Methods like `sub` and `subn` will compile the replace pattern on the fly if given a string.

```python
for m in bre.finditer(r'somepattern', 'some text', bre.UNICODE | bre.DOTALL):
    # do something
```

If you want to replace without compiling, you can use the `expand` method.

```python
m = bre.match(r'sometext')
if m:
    text = bre.expand(m, r'replace pattern')
```

## Search Back References

Added features available for search patterns. Features are broken up to show what is specifically added for Re and for Regex.

### Re

Back\ References      | Description
--------------------- |------------
`\c`                  | Uppercase character class.  ASCII or Unicode when re Unicode flag is used.  Can be used in character classes `[]`.
`\l`                  | Lowercase character class.  ASCII or Unicode when re Unicode flag is used.  Can be used in character classes `[]`.
`\C`                  | Inverse uppercase character class.  ASCII or Unicode when re Unicode flag is used.  Can be used in character classes `[]`.
`\L`                  | Inverse lowercase character class.  ASCII or Unicode when re Unicode flag is used.  Can be used in character classes `[]`.
`\Q...\E`             | Quotes (escapes) text for regular expression.  `\E` signifies the end of the quoting. Will be ignored in character classes `[]`.
`\p{UnicodeProperty}` | Unicode property character class. Search string must be a Unicode string. Can be used in character classes `[]`. See [Unicode Properties](#unicode-properties) for more info.
`\P{UnicodeProperty}` | Inverse Unicode property character class. Search string must be a Unicode string. Can be used in character classes `[]`. See [Unicode Properties](#unicode-properties) for more info.
`[[:alnum:]]`         | Though not really a back reference, support for Posix style character classes is available. See [Posix Style Properties](#posix-style-properties) for more info.

### Regex

Back\ References | Description 
---------------- | -----------
`\Q...\E`        | Quotes (escapes) text for regular expression.  `\E` signifies the end of the quoting. Will be ignored in character classes `[]`. 

## Replace Back References

Added features available for replace patterns. None of the replace back references can be used in character classes `[]`.  The references below apply to both Re **and** Regex.

Back&nbsp;References | Description 
---------------------|-------------
`\c`                 | Uppercase the next character. 
`\l`                 | Lowercase the next character. 
`\C...\E`            | Apply uppercase to all characters until either the end of the string or the end marker `\E` is found. 
`\L...\E`            | Apply lowercase to all characters until either the end of the string or the end marker `\E` is found. 

!!! tip "Tip"
    Complex configurations of casing should work fine.

    - `\L\cTEST\E` --> `Test`
    - `\c\LTEST\E` --> `Test`
    - `\L\cTEST \cTEST\E` --> `Test Test`

## Unicode Properties

!!! note "Note"
    Unicode Properties are only added to Re as Regex already has **full** Unicode properties built in (on both wide and narrow builds).

There are quite a few properties that are also supported and an exhaustive list is not currently provided. This documentation will only briefly touch on `General_Category`, `Block`, `Script`, and binary properties.

Unicode properties can be used with the format: `\p{property=value}`, `\p{property:value}`, `\p{value}`, `\p{^property=value}`, `\p{^value}`.  Though you don't have to specify the `UNICODE` flag, the search pattern must be a Unicode string and the search buffer must also be Unicode.

The inverse of properties can also be used to specify everything not in a Unicode property: `\P{value}` or `\p{^value}` etc.  They are only used in the search patterns. Only one property may specified between the curly braces.  If you want to use multiple properties, you can place them in a character class: `[\p{UnicodeProperty}\p{OtherUnicodeProperty}]`.

When specifying a property, the value matching is case insensitive and characters like `[ -_]` will be ignored.  So the following are all equivalent: `\p{Uppercase_Letter}`, `\p{Uppercase-letter}`, `\p{UPPERCASELETTER}`, `\p{upper case letter}`.

When evaluating a property in the form `\p{value}`, they are evaluated in this order:

1. General Category
2. Script
3. Blocks
4. Binary

All other properties are namespaced.  Example: `\p{Bidi_Class: White_Space}`.

When installed, the Unicode version that comes with the Python it is installed under will be used to generate all the Unicode tables.  For instance, Python 2.7 is currently using Unicode 5.2.0.  And Python 3.5 is using 8.0.0.

!!! caution "Narrow Python Builds"
    If you are using a narrow python build, your max Unicode value will be `\uffff`.  Unicode blocks above that limit will not be available.  Also Unicode values above the limit will not be available in character classes either.

    If you are using a wide build, you should have access to all Unicode values. If you are on a narrow build and need full Unicode ranges, you should consider using the Regex module.

### General Category

General categories can be specified in one of three ways: `\p{gc: value}`, `\p{General_Category: value}`, `\p{value}` etc.  Again, case is not important.  See the table below to see all the Unicode category properties that can be used.

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

### Blocks

There are a number of Unicode blocks and also aliases for blocks (they won't be listed here), but they can be specified in two ways: `\p{Block: Basic_Latin}` or `\p{InBasic_Latin}`.

### Scripts

There are a number of Unicode scripts and also aliases for scripts (they won't be listed here), but they can be specified in two ways: `\p{Script: Latin}` or `\p{IsLatin}`.

### Binary

There are a number of binary properties and even aliases for some of the binary properties.  Comprehensive lists are available on the web, but they are specified in the following way: `\p{Alphabetic}`.  Normal just specifying inverse via `\P{value}` or `\p{^value}` should be enough, but for completeness the form `\p{Alphabetic: Y}` and `\p{Alphabetic: N}` along with all the variants (Yes|No|T|F|True|False).

### Posix

A number of Posix property names are also available.  In general, when used in the `\p{}` form, they are aliases for existing Unicode properties with the same name. There are some Posix names that aren't used in the current Unicode properties such as `alnum`, `xdigit`, etc.  If you want to force the Posix form inside `\p{}` you can use their name prefixed with `posix`: `\p{Punct}` --> `\p{PosixPunct}` (these `posix` prefixed properties are treated as binary properties)  Currently when using Posix values in `\p{}` they will be forced into their Unicode form (see [Posix Style Properties](#posix-style-properties) for more info).

## Posix Style Properties

Posix properties in the form of `[:posix:]` and the inverse `[:^posix:]` are available.  These character classes are only available inside a character group `[]`.  If needed, you can use the alternate form of `\p{Posix}` to use inside and outside a character group.

!!! caution "Posix Values in `p{}`"
    If using the `\p{Posix}` form, the return will always be Unicode and properties like `punct` will revert to the Unicode property form opposed the Posix unless `posix` is prefixed to the name.  Example: the Unicode property `punct` = `[\p{P}]`, but the Posix `posixpunct` = `[\p{P}\p{S}]`.

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
