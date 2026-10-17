# Changelog

## 0.2.2

- **People with the same id in different families are no longer merged.**
  PED files often number each family's people from 1 (PLINK's own examples
  do), but 0.2.1 kept individuals by id alone, so a second family's "1", "2"
  and "3" silently replaced the first family's: a file of two such families,
  seven people, came out as four. Each family is now kept apart, everyone is
  still labelled with the id from the file, and a note says which ids were
  shared.
- **Children who can't be joined to their parents are reported.** Pedigree
  Studio draws a child's line from a couple, so a child whose file gives only
  one parent, or names a parent who is not in the file, is drawn without a
  line. That was silent; the command now prints a note for each such child,
  and `convert(..., notes=[])` collects the same notes in Python.
- **A misleading error is fixed.** When the output's folder did not exist,
  the command said that the *input* file could not be found; it now says it
  cannot write the output.
- Files are read as UTF-8 (with or without a byte-order mark) and the session
  written as UTF-8, whatever the computer's own setting, so ids with accents
  no longer fail on Windows.
- `ped2studio_standalone.py` was still version 0.1.0 and could not read MPED
  files, although the README said it could. It is now made from the package
  by `tools/make_standalone.py`, and a test checks that it is up to date and
  writes exactly what the package writes.
- `__version__` now matches the release (0.2.1 reported 0.2.0), and
  `--version` prints it.
- The README's link to Pedigree Studio pointed to a placeholder address.
- Tests run on Python 3.9 to 3.14, and releases are published to PyPI from
  GitHub.

## 0.2.1

Released on PyPI on 27 May 2026: the author and the repository's links in the
package's details. (Its `__version__` still said 0.2.0.)

## 0.2.0

Released on PyPI on 27 May 2026: MPED files. Each condition gets its own
colour and a place in the colour key; someone with two or more conditions is
drawn quartered, in up to four of their colours, a carrier with a half fill,
and a 3 in the Carrier column becomes a centre dot.

## 0.1.1

Released on PyPI on 20 May 2026: each person's id is written under their
symbol (0.1.0 left the text empty).

## 0.1.0

Released on PyPI on 20 May 2026.
