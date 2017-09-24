# Changelog

## 2.0.0

- **NEW**: Add support for case back references when using the Regex module's `subf` and `subfn`.
- **NEW**: Add new convenience method `expandf` to Regex that can take a format string and apply format style replaces.
- **NEW**: Add `FORMAT` flag to `compile_replace` to apply format style replaces when applicable.
- **NEW**: Add the same support that Regex has in relation to format style replacements to Re.
- **NEW**: Compiled replacements are now immutable.
- **NEW**: Various logic checking proper types and values.

## 1.1.1

Sep 19, 2017

- **FIX**: Fix bad regular expression pattern for binary replace in `bre`.
- **FIX**: For `\g<digit>`, ensure you can use group `0` and also allow leading `0` on non-zero digits.

## 1.1.0

Sep 18, 2017

- **NEW**: Rework algorithm to handle replace casing back references in Python 3.7 development builds in preparation for Python 3.7 release.
- **FIX**: Fix issue dealing with trailing backslashes in replace templates.

## 1.0.2

Aug 06, 2017

- **FIX**: Issues related to downloading Unicode data and Unicode table generation. Include Unicode data in release.

## 1.0.1

Jan 16, 2017

- **FIX**: Fixes for Python 3.6.

## 1.0.0

May 3, 2016

- **NEW**: Initial release.
