# Changelog

## 5.9

-   **NEW**: Add support for Python 3.14.
-   **ENHANCE**: Switch to deploying with PyPI's "Trusted Publisher".

## 5.8

-   **NEW**: Drop Python 3.8.
-   **FIX**: Deprecation warnings.

## 5.7

-   **NEW**: Add support for Python 3.13 beta.

## 5.6.post1

-   **Fix**: Update project metadata to indicate Python 3.12 support.

## 5.6

-   **NEW**: Officially support Python 3.12.

## 5.5.1

-   **FIX**: Fix some flag issues in `bregex`.

## 5.5

-   **NEW**: `\e` and `\h` have both been deprecated in 6.0. Please migrate to using `\x1b` and `\p{Horiz_Space}` in
    their respective place.
-   **FIX**: Fix flag issue with `sub` functions.

## 5.4

-   **NEW**: Officially support Python 3.11.
-   **NEW**: Add to Bre compatible custom Unicode properties `\p{Vert_Space}` and `\p{Horiz_Space}` that match Regex's
    new custom properties. This helps to expose vertical space shorthand that was not previously present.

## 5.3

-   **NEW**: Drop Python 3.6 support.
-   **NEW**: Update build backend to use Hatch.

## 5.2

-   **NEW**: Add type annotations.
-   **FIX**: Re format replacement captures behave more like Regex in that you can technically index into the captures
    of a given group in Re, but in Re there is only ever one or zero captures. Documentation was never really explicit
    on what one should expect if indexing a group in Re occurred. The documentation seemed to vaguely insinuate that it
    would behave like a Regex capture list, just with one or zero values in the list. In reality, the value was a simple
    string or `None`. This caused a bug in some cases where you'd have `None` inserted for a group if a group was
    optional, but referenced in the replacement template. Now the implementation matches the description in the
    documentation with the documentation now being more explicit about behavior.
-   **FIX**: Match Re and Regex handling when doing a non-format replacement that references a group that is present in
    the search pattern but has no actual captures. Such a case should not fail, but simply return an empty string for
    the group.
-   **FIX**: Format replacements that have groups with no captures will yield an empty string as the only capture as
    long as the user does not try to index into any captures as there are no actual captures. This behavior was a bug in
    Regex that we duplicated and should now be fixed in the latest Regex (mrabarnett/mrab-regex#439) as well as in
    Backrefs.

## 5.1

-   **NEW**: Add support for Python 3.10.

## 5.0.1

-   **FIX**: Fix wheel names.

## 5.0

-   **NEW**: Significant improvements to Unicode handling. A lot of testing was implemented to catch existing bugs and
    to improve result.
-   **NEW**: POSIX style properties now handle all existing Unicode properties.
-   **NEW**: POSIX properties now follow the [Unicode specification for POSIX compatibility][unicode-posix].
    Read the [documentation](../refs.md#posix-style-properties) to learn more.
-   **NEW**: Unicode properties are now sensitive to the `ASCII` flag and will properly restrict the range of properties
    to the ASCII range even in Unicode strings.
-   **NEW**: Removed the old deprecated search references: `\l`, `\L`, `\c`, and `\C`. These are available in various
    other forms: `[[:lower:]]`, `\p{lower}`, etc.
-   **NEW**: To reduce conflicts of naming, Binary properties are evaluated before Block properties when using short
    names. Block has conflicts with some other properties of various types, using short names for blocks is discouraged.
-   **FIX**: Numerous fixes to existing Unicode properties: missing values, incorrect values, etc.

## 4.6

- **NEW**: Provide wheels for all officially supported versions of Python.

## 4.5

-   **NEW**: Added new back reference `\h` to Re. To get similar functionality with Regex, users must update to the
    latest Regex release.

## 4.4

-   **NEW**: Added the following binary properties for Unicode 13.0 support (Python 3.9): `emoji`, `emojicomponent`,
    `emojimodifier`, `emojimodifierbase`, and `emojipresentation`. Associated aliases are also included: `ecomp`,
    `emod`, `ebase`, and `epres`.

## 4.3

-   **NEW**: Install Regex library along Backrefs via `pip install backrefs[extras]`.
-   **NEW**: Remove `version` and `__version__` and remove associated deprecation code.

## 4.2.1

-   **FIX**: Fix Python 3.8 installation issue due to Unicode bundle having an incorrect encoding in some files.

## 4.2

-   **NEW**: Deprecate the **search** references `\l`, `\L`, `\c`, and `\C`. The POSIX alternatives (which these were
    shortcuts for) should be used instead: `[[:lower:]]`, `[[:^lower:]]`, `[:upper:]]`, and `[[:^upper:]]` respectively.
-   **NEW**: Formally drop support for Python 3.4.

## 4.1.1

-   **FIX**: Later pre-release versions of Python 3.8 will support Unicode 12.1.0.

## 4.1

-   **NEW**: Add official support for Python 3.8.
-   **NEW**: Vendor the `Pep562` library instead of requiring as a dependency.
-   **NEW**: Input parameters accept `*args` and `**kwargs` instead of specify every parameter in order to allow
    Backrefs to work even when the Re or Regex API changes. Change was made to support new Regex `timeout` parameter.

## 4.0.2

-   **FIX**: Fix compatibility issues with latest Regex versions.

## 4.0.1

-   **FIX**: Ensure that when generating the Unicode property tables, that the property files are read in with `UTF-8`
    encoding.

## 4.0

-   **NEW**: Drop support for new features in Python 2. Python 2 support is limited to the 3.X.X series and will only
    receive bug fixes up to 2020. All new features moving forward will be on the 4.X.X series and will be for Python 3+
    only.

## 3.6

-   **NEW**: Make version available via the new, and more standard, `__version__` attribute and add the
    `__version_info__` attribute as well. Deprecate the old `version` and `version_info` attribute for future removal.

## 3.5.2

-   **FIX**: Include zip for Unicode 11 (Python 3.7) to make installation more reliable.

## 3.5.1

-   **FIX**: POSIX character classes should not be part of a range.
-   **FIX**: Replace string casing logic properly follows other implementations like Boost etc. `\L`, `\C`, and `\E`
    should all terminate `\L`, and `\C`. `\l` and `\c` will be ignored if followed by `\C` or `\L`.

## 3.5

-   **NEW**: Use a more advanced format string implementation that implements all string features, included those found
    in `format_spec`.
-   **FIX**: Relax validation so not to exclude valid named Unicode values.
-   **FIX**: Caching issues where byte string patterns were confused with Unicode patterns.
-   **FIX**: More protection against using conflicting string type combinations with search and replace.

## 3.4

-   **NEW**: Add support for generic line breaks (`\R`) to Re.
-   **NEW**: Add support for an overly simplified form of grapheme clusters (`\X`) to Re. Roughly equivalent to
    `(?>\PM\pM*)`.
-   **NEW**: Add support for `Vertical_Orientation` property for Unicode 10.0.0 on Python 3.7.

## 3.3

-   **NEW**: Add support for `Indic_Positional_Category`\\`Indic_Matra_Category` and `Indic_Syllabic_Category`
    properties.

## 3.2.1

-   **FIX**: `Bidi_Paired_Bracket_type` property's `None` value should be equivalent to all characters that are not
    `open` or `close` characters.

## 3.2

-   **NEW**: Add support for `Script_Extensions` Unicode properties (Python 3 only as Python 2, Unicode 5.2.0 does not
    define these). Can be accessed via `\p{scripts_extensions: kana}` or `\p{scx: kana}`.
-   **NEW**: When defining scripts with just their name `\p{Kana}`, use `Script_Extensions` instead of `Scripts`. To get
    `Scripts` results, you must specify `\p{scripts: kana}` or `\p{sc: scripts}`.
-   **NEW**: Add `Bidi_Paired_Bracket_Type` Unicode property (Python 3.4+ only).
-   **NEW**: Add support for `IsBinary` for binary properties: `\p{IsAlphabetic}` == `\p{Alphabetic: Y}`.
-   **FIX**: Tweaks/improvements to string iteration.

## 3.1.2

-   **FIX**: Properly escape any problematic characters in Unicode tables.

## 3.1.1

-   **FIX**: `bregex.compile` now supports additional keyword arguments for named lists like `bregex.compile_search`
    does.

## 3.1

-   **NEW**: Start and end word boundary back references are now specified with `\m` and `\M` like Regex does.  `\<` and
    `\>` have been removed from Regex.
-   **FIX**: Escaped `\<` and `\>` are no longer processed as Re is known to escape these in versions less than Python
    3.7.

## 3.0.5

-   **FIX**: Process non raw string equivalent escaped Unicode on Python 2.7.
-   **FIX**: Compiled objects should return the pattern string, not the pattern object via the property `pattern`.

## 3.0.4

-   **FIX**: Formally enable Python 3.7 support.
-   **FIX**: Tweak to Unicode wide character handling.

## 3.0.3

-   **FIX**: Compiled search and replace objects should be hashable.
-   **FIX**: Handle cases where a new compiled pattern object is passed back through compile functions.

## 3.0.2

-   **FIX**: Bregex purge was calling Re's purge instead of Regex's purge.

## 3.0.1

-   **FIX**: Do not accidentally `\.` as a group in replace strings (don't use `isdigit` string method).
-   **FIX**: Group names can start with `_` in replace strings.
-   **FIX**: Do not rely on Re for parsing string.
-   **FIX**: Match behavior in `\g<group>` parsing better.
-   **FIX**: Raise some exceptions in a few places we weren't.

## 3.0

-   **NEW**: Added new `compile` function that returns a pattern object that feels like Re's and Regex's pattern object.
-   **NEW**: Add some caching of search and replace patterns.
-   **NEW**: Completely refactored algorithm for search and replace pattern augmentation.
-   **NEW**: Add support for `\e` for escape character `\x1b` in both Re and Regex.
-   **NEW**: Add support for `\R` for generic newlines in the Regex module (Regex only).
-   **NEW**: Support Unicode property form `\pP` and `\PP`.
-   **NEW**: Add support for properly handling per group, scoped verbose flags in the preprocess step (Regex).
-   **NEW**: Handle `(?#comments)` properly in the preprocess step.
-   **NEW**: Add support for `\N` in byte strings (characters out of range won't be included).
-   **NEW**: Add support for `\p` and `\P` in byte strings (characters out of range won't be included).
-   **NEW**: Add support for `\<` and `\>` word boundary escapes.
-   **FIX**: Missing block properties on narrow systems when the property starts beyond the narrow limit.
-   **FIX**: Fix issue where an invalid general category could sometimes pass and return no characters.
-   **FIX**: Fix `\Q...\E` behavior so it is applied first as a separate step. No longer avoids `\Q...\E` in things like
    character groups or comments.
-   **FIX**: Flag related parsing issues in Regex and Re Python 3.6+.

## 2.2

-   **NEW**: Proper support for `\N{Unicode Name}`.
-   **FIX**: Incomplete escapes will not be passed through, but will instead throw an error. For instance `\p` should
    only be passed through if it is complete `\p{category}`.  Python 3.7 will error on this if we pass it through, and
    Python 3.6 will generate warnings.  We should just consistently fail on it for all Python versions.

## 2.1

-   **NEW**: Handle Unicode and byte notation in Re replace templates.
-   **NEW**: Rework algorithm to handle replace casing back references in Python 3.7 development builds in preparation
    for Python 3.7 release.
-   **NEW**: Add support for case back references when using the Regex module's `subf` and `subfn`.
-   **NEW**: Add new convenience method `expandf` to Regex that can take a format string and apply format style replaces.
-   **NEW**: Add `FORMAT` flag to `compile_replace` to apply format style replaces when applicable.
-   **NEW**: Add the same support that Regex has in relation to format style replacements to Re.
-   **NEW**: Compiled replacements are now immutable.
-   **NEW**: Various logic checking proper types and values.
-   **FIX**: Fix octal/group logic in Regex and Re.
-   **FIX**: Fix issue dealing with trailing backslashes in replace templates.

## 2.0

-   **NEW**: First attempt at bringing Python 3.7 support, fixing back reference logic, and adding new back reference.
    Released and then removed due to very poor behavior.

## 1.0.2

-   **FIX**: Issues related to downloading Unicode data and Unicode table generation. Include Unicode data in release.

## 1.0.1

-   **FIX**: Fixes for Python 3.6.

## 1.0

-   **NEW**: Initial release.
