# Changelog

## 3.5.0

- **NEW**: Use a more advanced format string implementation that implements all string features, included those found in `format_spec`.
- **FIX**: Relax validation so not to exclude valid named Unicode values.
- **FIX**: Caching issues where byte string patterns were confused with Unicode patterns.
- **FIX**: More protection against using conflicting string type combinations with search and replace.

## 3.4.0

Mar 8, 2018

- **NEW**: Add support for generic line breaks (`\R`) to Re.
- **NEW**: Add support for an overly simplified form of grapheme clusters (`\X`) to Re. Roughly equivalent to `(?>\PM\pM*)`.
- **NEW**: Add support for `Vertical_Orientation` property for Unicode 10.0.0 on Python 3.7.

## 3.3.0

Feb 27, 2018

- **NEW**: Add support for `Indic_Positional_Category`\\`Indic_Matra_Category` and `Indic_Syllabic_Category` properties.

## 3.2.1

Feb 26, 2018

- **FIX**: `Bidi_Paired_Bracket_type` property's `None` value should be equivalent to all characters that are not `open` or `close` characters.

## 3.2.0

Feb 25, 2018

- **NEW**: Add support for `Script_Extensions` Unicode properties (Python 3 only as Python 2, Unicode 5.2.0 does not define these). Can be accessed via `\p{scripts_extensions: kana}` or `\p{scx: kana}`.
- **NEW**: When defining scripts with just their name `\p{Kana}`, use `Script_Extensions` instead of `Scripts`. To get `Scripts` results, you must specify `\p{scripts: kana}` or `\p{sc: scripts}`.
- **NEW**: Add `Bidi_Paired_Bracket_Type` Unicode property (Python 3.4+ only).
- **NEW**: Add support for `IsBinary` for binary properties: `\p{IsAlphabetic}` == `\p{Alphabetic: Y}`.
- **FIX**: Tweaks/improvements to string iteration.

## 3.1.2

Feb 12, 2018

- **FIX**: Properly escape any problematic characters in Unicode tables.

## 3.1.1

Feb 11, 2018

- **FIX**: `bregex.compile` now supports additional keyword arguments for named lists like `bregex.compile_search` does.

## 3.1.0

Feb 11, 2018

- **NEW**: Start and end word boundary back references are now specified with `\m` and `\M` like Regex does.  `\<` and `\>` have been removed from Regex.
- **FIX**: Escaped `\<` and `\>` are no longer processed as Re is known to escape these in versions less than Python 3.7.

## 3.0.5

Feb 9, 2018

- **FIX**: Process non raw string equivalent escaped Unicode on Python 2.7.
- **FIX**: Compiled objects should return the pattern string, not the pattern object via the property `pattern`.

## 3.0.4

Feb 8, 2018

- **FIX**: Formally enable Python 3.7 support.
- **FIX**: Tweak to Unicode wide character handling.

## 3.0.3

Jan 28, 2018

- **FIX**: Compiled search and replace objects should be hashable.
- **FIX**: Handle cases where a new compiled pattern object is passed back through compile functions.

## 3.0.2

Jan 22, 2018

- **FIX**: Bregex purge was calling Re's purge instead of Regex's purge.

## 3.0.1

Jan 21, 2018

- **FIX**: Do not accidentally `\.` as a group in replace strings (don't use `isdigit` string method).
- **FIX**: Group names can start with `_` in replace strings.
- **FIX**: Do not rely on Re for parsing string.
- **FIX**: Match behavior in `\g<group>` parsing better.
- **FIX**: Raise some exceptions in a few places we weren't.

## 3.0.0

Jan 20, 2018

- **NEW**: Added new `compile` function that returns a pattern object that feels like Re's and Regex's pattern object.
- **NEW**: Add some caching of search and replace patterns.
- **NEW**: Completely refactored algorithm for search and replace pattern augmentation.
- **NEW**: Add support for `\e` for escape character `\x1b` in both Re and Regex.
- **NEW**: Add support for `\R` for generic newlines in the Regex module (Regex only).
- **NEW**: Support Unicode property form `\pP` and `\PP`.
- **NEW**: Add support for properly handling per group, scoped verbose flags in the preprocess step (Regex).
- **NEW**: Handle `(?#comments)` properly in the preprocess step.
- **NEW**: Add support for `\N` in byte strings (characters out of range won't be included).
- **NEW**: Add support for `\p` and `\P` in byte strings (characters out of range won't be included).
- **NEW**: Add support for `\<` and `\>` word boundary escapes.
- **FIX**: Missing block properties on narrow systems when the property starts beyond the narrow limit.
- **FIX**: Fix issue where an invalid general category could sometimes pass and return no characters.
- **FIX**: Fix `\Q...\E` behavior so it is applied first as a separate step. No longer avoids `\Q...\E` in things like character groups or comments.
- **FIX**: Flag related parsing issues in Regex and Re Python 3.6+.

## 2.2.0

Dec 11, 2017

- **NEW**: Proper support for `\N{Unicode Name}`.
- **FIX**: Incomplete escapes will not be passed through, but will instead throw an error. For instance `\p` should only be passed through if it is complete `\p{category}`.  Python 3.7 will error on this if we pass it through, and Python 3.6 will generate warnings.  We should just consistently fail on it for all Python versions.

## 2.1.0

Sep 29, 2017

- **NEW**: Handle Unicode and byte notation in Re replace templates.
- **NEW**: Rework algorithm to handle replace casing back references in Python 3.7 development builds in preparation for Python 3.7 release.
- **NEW**: Add support for case back references when using the Regex module's `subf` and `subfn`.
- **NEW**: Add new convenience method `expandf` to Regex that can take a format string and apply format style replaces.
- **NEW**: Add `FORMAT` flag to `compile_replace` to apply format style replaces when applicable.
- **NEW**: Add the same support that Regex has in relation to format style replacements to Re.
- **NEW**: Compiled replacements are now immutable.
- **NEW**: Various logic checking proper types and values.
- **FIX**: Fix octal/group logic in Regex and Re.
- **FIX**: Fix issue dealing with trailing backslashes in replace templates.

## 2.0.0

- **NEW**: First attempt at bringing Python 3.7 support, fixing back reference logic, and adding new back reference. Released and then removed due to very poor behavior.

## 1.0.2

Aug 06, 2017

- **FIX**: Issues related to downloading Unicode data and Unicode table generation. Include Unicode data in release.

## 1.0.1

Jan 16, 2017

- **FIX**: Fixes for Python 3.6.

## 1.0.0

May 3, 2016

- **NEW**: Initial release.
