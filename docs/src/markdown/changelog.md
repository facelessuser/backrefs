# Changelog

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
