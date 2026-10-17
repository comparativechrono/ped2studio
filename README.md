# ped2studio

Convert PED and MPED pedigree files into
[Pedigree Studio](https://github.com/comparativechrono/PedigreeStudio) session
JSON files, so that a family recorded in a table can be drawn, checked and
edited.

## Installation

```bash
pip install ped2studio
```

Or use the standalone script (`ped2studio_standalone.py`) with no installation
required: it needs only Python 3.9+.

## Usage

### Command line

```bash
# Basic conversion (standard PED)
ped2studio family.ped family.json

# MPED file (auto-detected, each phenotype gets its own colour)
ped2studio family.mped family.json

# Use a specific colour for affected individuals (single-phenotype only)
ped2studio family.ped family.json --colour "#c0392b"

# Use left-half fill instead of full shape
ped2studio family.ped family.json --fill half

# Combine half fill with a colour
ped2studio family.ped family.json --fill half --colour "#c0392b"

# Use shading pattern instead of colour
ped2studio family.ped family.json --shading --pattern stripes

# Use half-shape dot shading
ped2studio family.ped family.json --shading --pattern dots --fill half
```

Open the result in Pedigree Studio with **File → Open**. ped2studio lays the
family out simply; press **Tidy** in Pedigree Studio to arrange it properly.

The command says how many people, couples and child lines it drew, and prints
a note about anything the drawing can't show as the file does (see
[What can't be drawn](#what-cant-be-drawn)).

### Python API

```python
import ped2studio

# From a PED string (default: full solid black)
session = ped2studio.convert(ped_text)

# From an MPED string (auto-detected, multi-colour)
session = ped2studio.convert(mped_text)

# From file to file (works with both .ped and .mped)
ped2studio.convert_file("family.mped", "family.json")

# With options (single-phenotype files only)
session = ped2studio.convert(
    ped_text,
    affected_color="#c0392b",   # colour for affected (when not using shading)
    fill_type="half",           # 'full' or 'half'
    use_shading=True,           # use pattern instead of colour
    shading_pattern="stripes",  # 'stripes' or 'dots'
)

# Collect the notes the command prints
notes = []
session = ped2studio.convert(ped_text, notes=notes)
```

### Standalone script

```bash
python ped2studio_standalone.py family.ped family.json
python ped2studio_standalone.py family.ped family.json --fill half --colour "#c0392b"
python ped2studio_standalone.py family.ped family.json --shading --pattern dots --fill half
```

The script is the package in one file, made by `python tools/make_standalone.py`;
a test checks that the two agree.

## MPED support

MPED (multi-phenotype PED) files are detected and handled automatically. When
an MPED file has several phenotype columns, each phenotype is given its own
colour from Pedigree Studio's palette, and the colour key names them.

How each person is drawn when there are several phenotypes:

| Individual's status | Drawn in Pedigree Studio as |
|-------------------|--------------------------|
| Affected for 1 phenotype | Solid fill in that phenotype's colour |
| Affected for 2 or more phenotypes | Quartered fill, in the colours of up to four of them |
| Carrier for 1 phenotype | Half fill (left) in that phenotype's colour |
| Carrier for 2 or more phenotypes | Quartered fill in their colours |
| Carrier column = 3 | Centre dot (●) |
| Unaffected | No fill |

For MPED files with a single phenotype, the `--colour`, `--fill` and
`--shading` options work as they do for PED files.

## PED file format

The tool reads the standard 6-column PED format:

```
FamilyID  IndividualID  FatherID  MotherID  Sex  Phenotype
```

| Column | Description |
|--------|-------------|
| FamilyID | Family identifier: not shown in the drawing, but it keeps families apart (see below) |
| IndividualID | Identifier for the individual, written under their symbol |
| FatherID | Father's IndividualID, or `0` if unknown |
| MotherID | Mother's IndividualID, or `0` if unknown |
| Sex | `1` = male, `2` = female, `0` = unknown |
| Phenotype | `2` = affected, `1` = unaffected, `0` or `-9` = unknown |

Additional columns beyond column 6 (e.g. genotype data) are ignored. Lines
starting with `#` are treated as comments. Both tab and space delimiters are
supported, and the file is read as UTF-8.

A file can hold several families, and they may reuse the same ids (PLINK's
files number each family's people 1, 2, 3 …). People with the same id in
different families are different people: they are drawn separately, each with
the id from the file under their symbol, and a note lists the ids that were
shared.

## How it works

1. **Parse** the PED file into individuals with parent references
2. **Build** mating units (each unique father+mother pair with their children)
3. **Assign** generations (founders = generation 0, children = max parent generation + 1)
4. **Layout** individuals using Pedigree Studio's default spacing (partner gap = 104px, child height = 130px, sibling spacing = 104px)
5. **Emit** a Pedigree Studio v4 session JSON with persons, partnerships, child links, and legend

Positions may need adjusting for complex pedigrees: Pedigree Studio's **Tidy**
does that.

## What can't be drawn

Pedigree Studio draws a child's line from a couple. A child is therefore
joined to their parents only when the file gives both parents and both are in
the file. A child with only one parent given, or whose parent is not in the
file, is drawn without a line, and the command prints a note naming them.

## Mapping to Pedigree Studio features

| PED field | Pedigree Studio feature |
|-----------|------------------------|
| Sex = 1 | `male` shape (square) |
| Sex = 2 | `female` shape (circle) |
| Sex = 0 | `unknown` shape (diamond) |
| Phenotype = 2 | Solid colour fill, half colour fill, or shading pattern (configurable via `--fill`, `--colour`, `--shading`, `--pattern`) |
| Phenotype = 1 | No fill |
| Father+Mother pair | Partnership line (a consanguineous line when the two share an ancestor) |
| Child of a pair | Child link from partnership to individual |

## Development

```bash
pip install -e ".[test]"
pytest
```

## Licence

MIT
