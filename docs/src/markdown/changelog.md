# Changelog

## 2.0.2

Sep 26, 2017

- **FIX**: Don't apply case to template Unicode and binary notation: `\u00cf`, `\x57` etc. Also don't apply case to standard special references like `\n` etc.
- **FIX**: For Regex only (because it is Regex's default behavior), translate syntax for Unicode characters and binary to there actual character form and then apply case if specified. Afterwards, convert back to back slash notation and insert back into the replace template.
- **FIX**: Since Backrefs' format replace is a simulation of Regex's format, it uses Regex's non-format API to pull of the format replace; therefore, respect Unicode and binary char replacements the same way as non-format replace.

## 2.0.1

Sep 24, 2017

- **FIX**: Make sure that back slash group formats don't not get applied to format templates.
- **FIX**: Make sure format curly brackets don't get escaped by back slash.

## 2.0.0

Sep 24, 2017

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
