#ped2studio
Convert standard PED pedigree files into Pedigree Studio session JSON files.
Installation
```bash
pip install ped2studio
```
Or use the standalone script (`ped2studio_standalone.py`) with no installation required — it needs only Python 3.9+.
Usage
Command line
```bash
# Basic conversion (default: full solid black fill for affected)
ped2studio family.ped family.json

# Use a specific colour for affected individuals
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
Python API
```python
import ped2studio

# From a PED string (default: full solid black)
session = ped2studio.convert(ped_text)

# From file to file
ped2studio.convert_file("family.ped", "family.json")

# With options
session = ped2studio.convert(
    ped_text,
    affected_color="#c0392b",   # colour for affected (when not using shading)
    fill_type="half",           # 'full' or 'half'
    use_shading=True,           # use pattern instead of colour
    shading_pattern="stripes",  # 'stripes' or 'dots'
)
```
Standalone script
```bash
python ped2studio_standalone.py family.ped family.json
python ped2studio_standalone.py family.ped family.json --fill half --colour "#c0392b"
python ped2studio_standalone.py family.ped family.json --shading --pattern dots --fill half
```
PED file format
The tool reads the standard 6-column PED format:
```
FamilyID  IndividualID  FatherID  MotherID  Sex  Phenotype
```
Column	Description
FamilyID	Family identifier (preserved but not used for grouping)
IndividualID	Unique identifier for the individual
FatherID	Father's IndividualID, or `0` if unknown
MotherID	Mother's IndividualID, or `0` if unknown
Sex	`1` = male, `2` = female, `0` = unknown
Phenotype	`2` = affected, `1` = unaffected, `0` or `-9` = unknown
Additional columns beyond column 6 (e.g. genotype data) are ignored. Lines starting with `#` are treated as comments. Both tab and space delimiters are supported.
How it works
Parse the PED file into individuals with parent references
Build mating units (each unique father+mother pair with their children)
Assign generations (founders = generation 0, children = max parent generation + 1)
Layout individuals using Pedigree Studio's default spacing (partner gap = 104px, child height = 130px, sibling spacing = 104px)
Emit a Pedigree Studio v4 session JSON with persons, partnerships, child links, and legend
The output can be imported directly into Pedigree Studio via the Import JSON button. Positions may need manual adjustment for complex pedigrees.
Mapping to Pedigree Studio features
PED field	Pedigree Studio feature
Sex = 1	`male` shape (square)
Sex = 2	`female` shape (circle)
Sex = 0	`unknown` shape (diamond)
Phenotype = 2	Solid colour fill, half colour fill, or shading pattern (configurable via `--fill`, `--color`, `--shading`, `--pattern`)
Phenotype = 1	No fill
Father+Mother pair	Partnership line
Child of a pair	Child link from partnership to individual
License
MIT
