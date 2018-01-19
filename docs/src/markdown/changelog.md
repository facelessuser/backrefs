# Changelog

## 2.3.0

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

- **NEW**: Proper support for `\N{Unicode Name}`.
- **FIX**: Incomplete escapes will not be passed through, but will instead throw an error. For instance `\p` should only be passed through if it is complete `\p{category}`.  Python 3.7 will error on this if we pass it through, and Python 3.6 will generate warnings.  We should just consistently fail on it for all Python versions.

## 2.1.0

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
