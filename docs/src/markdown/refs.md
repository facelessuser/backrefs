# Supported References

## Search Back References

Re and Regex out of the box have very different feature sets. Backrefs tailors the supported features for each regular
expression engine. For instance, Regex already supports Unicode properties, so Backrefs does not attempt to provide such
support.

### Re

/// info | LOCALE and Character Properties
Backrefs does not consider `LOCALE` when inserting POSIX or Unicode properties. When forced int ASCII mode, either
by  the `ASCII` (or `LOCALE`) flag or when operating on a byte string, Unicode properties are restricted to the
ASCII range.
///

Back\ References      | Description
--------------------- |------------
`\e`                  | **Deprecated: Use `\x1b` instead.** Escape character `\x1b`.
`\Q...\E`             | Quotes (escapes) text for regular expression.  `\E` signifies the end of the quoting. Affects any and all characters no matter where in the regular expression pattern it is placed.
`\p{UnicodeProperty}` | Unicode property character class. Can be used in character classes `[]`. See [Unicode Properties](#unicode-properties) for more info.
`\pX`                 | Unicode property character class where `X` is the uppercase letter that represents the General Category property.  For instance, `\pL` would be equivalent to `\p{L}` or `\p{Letter}`.
`\P{UnicodeProperty}` | Inverse Unicode property character class. Can be used in character classes `[]`. See [Unicode Properties](#unicode-properties) for more info.
`\PX`                 | Inverse Unicode property character class where `X` is the uppercase letter that represents the General Category property. For instance, `\PL` would be equivalent to `\P{L}` or `\P{Letter}`.
`[[:alnum:]]`         | Though not really a back reference, support for POSIX style character classes is available. See [POSIX Style Properties](#posix-style-properties) for more info.
`\N{UnicodeName}`     | Named characters are normally ignored in Re, but Backrefs adds support for them.
`\m`                  | Start word boundary. Translates to `\b(?=\w)`.
`\M`                  | End word boundary. Translates to `\b(?<=\w)`.
`\h`                  | **Deprecated: Use `\p{Horiz_Space}` instead.** Horizontal whitespace. Equivalent to using `[[:blank:]]` or `[\t\p{Zs}]`.
`\R`                  | Generic line breaks. This will use the pattern `(?:\r\n|(?!\r\n)[\n\v\f\r\x85\u2028\u2029])` which is roughly equivalent the to atomic group form that other engines use: `(?>\r\n|[\n\v\f\r\x85\u2028\u2029])`. When applied to byte strings, the pattern `(?:\r\n|(?!\r\n)[\n\v\f\r\x85])` will be used.
`\X`                  | Grapheme clusters. This will use the pattern `(?:\PM\pM*(?!\pM))` which is roughly equivalent to the atomic group form that other engines have used in the past:  `(?>\PM\pM*)`. This does not implement [full, proper grapheme clusters][grapheme-boundaries] like the 3rd party Regex module does as this would require changes to the Re core engine.

/// warning | Deprecated 6.0
`\e` and `\h` have both been deprecated in 6.0. Please migrate to using `\x1b` and `\p{Horiz_Space}` in their places
respectively.
///

### Regex

/// note
Regex already natively supports `\p{...}`, `\P{...}`, `\pX`, `\PX`, `\N{...}`, `\X`, `\h`, `\m`, and `\M` so
Backrefs does not attempt to add this to search patterns.
///

Back\ References | Description
---------------- | -----------
`\e`             | **Deprecated: Use `\x1b` instead.** Escape character `\x1b`.
`\Q...\E`        | Quotes (escapes) text for regular expression.  `\E` signifies the end of the quoting. Affects any and all characters no matter where in the regular expression pattern it is placed.
`\R`             | Generic line breaks. When searching a Unicode string, this will use the pattern `(?>\r\n|[\n\v\f\r\x85\u2028\u2029])`, and when applied to byte strings, the pattern `(?>\r\n|[\n\v\f\r\x85])` will be used.

/// warning | Deprecated 6.0
`\e` has been deprecated in 6.0. Please migrate to using `\x1b` in its place.
///

## Replace Back References

The replace back references below apply to both Re **and** Regex and are essentially non-specific to the regular
expression engine being used.  Casing is applied to both the literal text and the replacement groups within the replace
template.  In most cases you'd only need to wrap the groups, but it may be useful to apply casing to the literal
portions if you are dynamically assembling replacement patterns.

/// info | LOCALE and Casing
`LOCALE` is not considered when applying character casing. Unicode casing is applied in Unicode strings and ASCII
casing is applied to byte strings.
///

Back\ References     | Description
---------------------|-------------
`\c`                 | Uppercase the next character.
`\l`                 | Lowercase the next character.
`\C...\E`            | Apply uppercase to all characters until either the end of the string, the end marker `\E` is found, or another `\C` or `\L` is encountered.
`\L...\E`            | Apply lowercase to all characters until either the end of the string, the end marker `\E` is found, or another `\L` or `\C` is encountered.
`\U`                 | Wide Unicode character `\U00000057`. Re doesn't translate this notation in raw strings (`#!py3 r"..."`), and Regex doesn't in format templates in raw strings (`#!py3 r"{} {}"`).  This adds support for them.
`\u`                 | Narrow Unicode character `\u0057`. Re doesn't translate this notation in raw strings (`#!py3 r"..."`), and Regex doesn't in format templates in raw strings (`#!py3 r"{} {}"`).  This adds support for them.
`\x`                 | Byte character `\x57`. Re doesn't translate this notation in raw strings (`#!py3 r"..."`), and Regex doesn't in format templates in raw strings (`#!py3 r"{} {}"`).  This adds support for them.
`\N{UnicodeName}`    | Named characters are normally ignored in Re, but Backrefs adds support for them.

/// tip
Complex configurations of casing should work fine.

-   `\L\cTEST\E` --> `Test`
-   `\c\LTEST\E` --> `test`
-   `\L\cTEST \cTEST\E` --> `Test Test`
///

## Unicode Properties

/// new | New in 5.0
5.0 brings significant improvements and bug fixes to Unicode property handling. Properties are sensitive to the
`ASCII` flag along with more extensive testing and bug fixes.
///

A number of various Unicode properties are supported in Backrefs, but only for Re as Regex already has its own
implementation of Unicode properties. Some properties may not be available on certain Python versions due to the
included Unicode build.

It is important to note that Backrefs handles Unicode properties by transforming them to character classes with all the
associated characters: `\p{Cs}` --> `[\ud800\udb7f-\udb80\udbff-\udc00\udfff]`.  Because of this, Backrefs can create
really large regular expressions that the underlying engine must walk through.  In short, Re with Backrefs will never be
as efficient or fast as using Regex's Unicode properties, but it is very useful when you need or want to use Re.

Also, keep in mind that there are most likely some differences between Regex's Unicode Properties and Backrefs' Unicode
properties. One notable difference is Regex does not currently implement `script_extensions` while Backrefs' does and
uses them as the default when specifying them in the form `\p{IsScriptValue}`  or `\p{ScriptValue}` just like Perl does.
See [Property Short Names](#property-short-names) for more info.

Supported\ Properties                       | Aliases
------------------------------------------- | -------
`Age`                                       | &nbsp;
`Bidi_Class`                                | `bc`
`Bidi_Paired_Bracket_Type`                  | `bpt`
`Binary`                                    | &nbsp;
`Block`                                     | `blk`
`Canonical_Combining_Class`                 | `ccc`
`Decomposition_Type`                        | `dt`
`East_Asian_Width`                          | `ea`
`General_Category`                          | `gc`
`Grapheme_Cluster_Break`                    | `gcb`
`Hangul_Syllable_Type`                      | `hst`
`Indic_Positional_Category`                 | `inpc`
`Indic_Syllabic_Category`                   | `insc`
`Joining_Group`                             | `jg`
`Joining_Type`                              | `jt`
`Line_Break`                                | `lb`
`NFC_Quick_Check`                           | `nfcqc`
`NFD_Quick_Check`                           | `nfdqc`
`NFKC_Quick_Check`                          | `nfkcqc`
`NFKD_Quick_Check`                          | `nfkdqc`
`Numeric_Type`                              | `nt`
`Numeric_Value`                             | `nv`
`Script`                                    | `sc`
`Script_Extensions`                         | `scx`
`Sentence_Break`                            | `sb`
`Vertical_Orientation`\ (Python\ 3.7+)      | `vt`
`Word_Break`                                | `wb`

/// note
The Binary property is not actually a property, but more a type of Unicode property.  The available binary
properties may differ from Unicode version to Unicode version.
///

/// new | New 4.4.0
Python 3.9 now uses Unicode 13, and with that comes various new binary properties: `emoji`, `emojicomponent`,
`emojimodifier`, `emojimodifierbase`, and `emojipresentation`. Associated aliases are also included: `ecomp`,
`emod`, `ebase`, and `epres`.
///

Exhaustive documentation on all these properties and their values is not currently provided. In general, we'll cover the
syntax rules, and [special short name handling](#property-short-names) to those rules for specific properties.
Though we will outline all the values for General Category, we will not outline all of the valid values for the other
properties. You can look at [Perl's Unicode property documentation][perl-uniprops] to get an idea of what values are
appropriate for a given property, but keep in mind, syntax may vary from Perl's syntax.

Unicode properties are specific to search patterns and can be used to specify a request to match all the characters in a
specific Unicode property. Unicode properties can be used in byte strings, but the patterns will be restricted to the
ASCII range.

Additionally, Unicode properties are sensitive to the `ASCII` flag and will have their range limited to ASCII if used.
The `LOCALE` flag is treated as `ASCII` in relation to Unicode properties.

### Syntax

Unicode properties can be specified with the format: `\p{property=value}`, `\p{property:value}`. You can also do inverse
properties by using the `^` character (`\p{^property=value}`) or by using a capital `P` (`\P{property=value}` or
`\P{property:value}`).

Unicode properties may only have one property specified between the curly braces.  If you want to use multiple
properties to capture a singe character, create a character class: `[\p{UnicodeProperty}\p{OtherUnicodeProperty}]`.

When specifying a property, the property and value matching is case insensitive and characters like `[ -_]` will be
stripped out.  So the following are all equivalent: `\p{Uppercase_Letter}`, `\p{Uppercase-letter}`,
`\p{UPPERCASELETTER}`, `\p{upper case letter}`.

There are a number of binary properties. In general, binary properties are specified by stating the binary property and
a boolean value. True values can be `Yes`, `Y`, `True`, or `T`. False values can be `No`, `N`, `False`, or `F`. For
example, to specify characters that are "alphabetic", we can use `\p{Alphabetic: Y}`. To specify characters that are
**not** "alphabetic": `\p{Alphabetic: N}`.

/// new | New 5.4 Custom Binary properties
In 5.4, the new custom binary properties `Vert_space` and `Horiz_Space` were added.
///

### Property Short Names

General Category, Script Extensions, Blocks, and Binary all can be specified in a short form using just their name or
alias: `\p{value}`, but they will be evaluated in the following order to resolve name conflicts as some the same value
that is used in Script may be used in Blocks etc.

1.  General Category
2.  Script Extensions
4.  Binary
3.  Blocks

Script Extensions and Binary properties can also be defined in the format `IsValue`.  For instance, if we wanted to
match characters in the `Latin` script, we could use the syntax `\p{IsLatin}`, which would be the same as `\p{Latin}` or
`\p{scx: Latin}`.  For Binary properties, `\p{IsAlphabetic}` is the same as `\p{Alphabetic: Y}` or `\p{Alphabetic}`.

Block properties have a similar short form as Script and Binary properties.  For Blocks you can use `InValue` to specify
a block. If we wanted to match characters in the `Basic_Latin` block, we could use the syntax `\p{InBasic_Latin}`. This
would be the same as `\p{Block: Basic_Latin}` or `\p{Basic_Latin}`.

/// warning | Short Name Conflicts
When it comes to short names, each new Unicode version, there is a risk that new properties could cause conflicts
with existing names and/or aliases. Currently, most of the conflicts involve the Block properties. To reduce
friction, they are evaluated last.

Generally, it is discouraged to use short names for Block properties. But the option is still supported, but Block 
properties will be evaluated last. There are currently no known conflicts with `In*` properties, but in future
Unicode versions there could.

As for short names for scripts, Binary, or General Categories, there is always the possibility that these could
break in the future as well. Generally, more explicit is better and probably safer.
///

Lastly, you can specify general category properties in the form `\pX` where `X` is the single letter terse property
form. In this form, you can only use the single character values. So you could specify `Letter`, whose terse form is `L`
with `\pL`, but cannot specify `Cased_Letter` which has a terse form of `Lc`.

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

/// new | New in 5.0
5.0 brings significant improvements and bug fixes to Unicode property handling. Properties are sensitive to the
`ASCII` flag along with more extensive testing and bug fixes. Additionally, POSIX style properties are now just
an extension of normal Unicode properties. All the POSIX names are available and now conform to
the [Unicode specification for POSIX compatibility](https://unicode.org/reports/tr18/#Compatibility_Properties).
Read on to learn more.
///

Backrefs allows for POSIX style properties in the form `[:name:]`. These properties can only be used inside character
classes and are another form for expressing Unicode properties. Any Unicode property that can be expressed via the
`\p{name}` form can also be expressed in the `[:name:]` form. To illustrate, the following are all the same:

-   `[[:upper:]]` == `[\p{upper}]`
-   `[[:^upper:]]` == `[\p{^upper}]`
-   `[[:alpha=yes:]]` == `[\p{alpha=yes}]`

A number of POSIX property names are available via compatibility properties as outlined in the
[Unicode specification for POSIX compatibility](https://unicode.org/reports/tr18/#Compatibility_Properties). These
properties will operate in the Unicode range and the ASCII range depending on the regular expression mode. These
patterns, like all Unicode properties, are sensitive to the `ASCII` flag (or `LOCALE` which will treat them as `ASCII`).

It is important to note that whether used in the form `[[:name:]]` or `\p{name}`, each POSIX name is available both with
and without the `posix` prefix, but it is recommended to use the `posix` prefix to get the POSIX definition of the
pattern as number of patterns have both a POSIX and Unicode definition that differ. The
[Unicode specification for POSIX compatibility](https://unicode.org/reports/tr18/#Compatibility_Properties) outlines all
the POSIX compatible properties and the ones which have dual definitions: `punct`, `alnum`, `digit`, and `xdigit` all
have a Unicode standard and a POSIX compatibility variant and must be accessed with the `posix` prefix to get the POSIX
form.

In the table below, patterns with `--` mean `[[in this] -- [but not this]]`.

\[:posix:] | \\p\{Posix}   | ASCII                                             | Unicode
---------- | ------------- | ------------------------------------------------- | -------
`alpha`    | `Alpha`       | `[a-zA-Z]`                                        | `\p{Alphabetic}`
`alnum`    | `PosixAlnum`  | `[[:alpha:][:digit:]]`                            | `[[:alpha:][:digit:]]`
`blank`    | `Blank`       | `[ \t]`                                           | `[\p{Zs}\t]`
`cntrl`    | `Cntrl`       | `[\x00-\x1F\x7F]`                                 | `\p{Cc}`
`digit`    | `PosixDigit`  | `[0-9]`                                           | `[0-9]`
`graph`    | `Graph`       | `[^ [:cntrl:]]`                                   | `[^[:space:][:cntrl:]\p{Cn}\p{Cs}]`
`lower`    | `Lower`       | `[a-z]`                                           | `[\p{Lowercase}]`
`print`    | `Print`       | `[[:graph:] ]`                                    | `[[\p{P}\p{S}]--[\p{alpha}]]`
`punct`    | `PosixPunct`  | ``[!\"\#$%&'()*+,\-./:;&lt;=&gt;?@\[\\\]^_`{}~]`` | `[[[:graph:][:blank:]]--[[:cntrl:]]]`
`space`    | `Space`       | `[ \t\r\n\v\f]`                                   | `[\p{Whitespace}]`
`upper`    | `Upper`       | `[A-Z]`                                           | `[\p{Uppercase}]`
`xdigit`   | `PosixXDigit` | `[A-Fa-f0-9]`                                     | `[A-Fa-f0-9]`

### Compatibility Properties

/// new | New in 5.0
While many of the properties were available before 5.0, `word` is newly available. And all the properties now
conform to the [Unicode specification for POSIX compatibility](https://unicode.org/reports/tr18/#Compatibility_Properties).
///

[Unicode specification for POSIX compatibility][unicode-posix] defines a number of properties, many of which double as
[Posix properties](#posix-style-properties). These properties can be accessed via `\p{name}` or `[[:name:]]`.

In the table below, patterns with `--` mean `[[in this] -- [but not this]]`.

\\p\{Posix}   | Unicode
------------- | -------
`Alpha`       | `\p{Alphabetic}`
`Alnum`       | `[\p{Alpha}\p{Digit}]`
`Blank`       | `[\p{Zs}\t]`
`Cntrl`       | `\p{Cc}`
`Digit`       | `\p{Nd}`
`Graph`       | `[^\p{Space}\p{Cntrl}\p{Cn}\p{Cs}]`
`Lower`       | `\p{Lowercase}`
`Print`       | `[[\p{P}\p{S}]--[\p{Alpha}]]`
`Punct`       | `\p{P}`
`Space`       | `\p{Whitespace}`
`Upper`       | `\p{Uppercase}`
`Word`        | `[\p{Alnum}\p{M}\p{Pc}\p{JoinControl}]`
`XDigit`      | `[\p{Nd}\p{HexDigit}]`
