"""Tests for ped2studio.

The MPED files in tests/data were written by studio2ped 0.2.0 from fictional
families (four from the Hearn lab's pedigree practical, and one with every
kind of symbol Pedigree Studio draws). simple.ped and two-families.ped are
made up for these tests.
"""
import contextlib
import io
import json
import os

import pytest

import ped2studio
from ped2studio.cli import main
from ped2studio.converter import PHENOTYPE_PALETTE

DATA = os.path.join(os.path.dirname(__file__), "data")
MPED = ["okafor", "price", "lynch", "cf-cousins", "features"]


def read(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return fh.read()


def rows(text):
    out = []
    for line in text.splitlines():
        if line.strip() and not line.startswith("#"):
            out.append(line.split("\t") if "\t" in line else line.split())
    return out


def parents_in(session):
    """{child's text: (father's text, mother's text)} from a session's lines."""
    text = {p["id"]: p["text"] for p in session["persons"]}
    couples = {pr["id"]: (text[pr["fromId"]], text[pr["toId"]]) for pr in session["partnerships"]}
    return {text[cl["childId"]]: couples[cl["partnershipId"]] for cl in session["childLinks"]}


def person(session, label):
    return next(p for p in session["persons"] if p["text"] == label)


def test_a_standard_ped_file():
    session = ped2studio.convert(read("simple.ped"))
    assert session["version"] == 4
    assert [p["text"] for p in session["persons"]] == ["I-1", "I-2", "II-1", "II-2", "II-3", "III-1", "III-2"]
    assert [p["shape"] for p in session["persons"]] == ["male", "female", "male", "female", "male", "female", "unknown"]
    assert parents_in(session) == {"II-1": ("I-1", "I-2"), "II-2": ("I-1", "I-2"),
                                   "III-1": ("II-3", "II-2"), "III-2": ("II-3", "II-2")}
    affected = {p["text"] for p in session["persons"] if p["fillMode"] == "solid"}
    assert affected == {"I-2", "II-1", "III-1"}                    # -9 is unknown, not affected
    assert session["legendLabels"] == {"#1a2332": "Affected"}
    rows_by_gen = sorted({p["y"] for p in session["persons"]})
    assert len(rows_by_gen) == 3                                   # one row per generation
    json.dumps(session)


def test_mped_files_keep_their_families_and_conditions():
    for name in MPED:
        text = read(name + ".mped")
        table = rows(text)
        header = text.splitlines()[0].split("\t")[1:]
        session = ped2studio.convert(text)
        assert len(session["persons"]) == len(table), name
        expected = {r[1]: (r[2], r[3]) for r in table if r[2] != "0" and r[3] != "0"}
        assert parents_in(session) == expected, name
        conditions = [c for c in header if c.lower() != "carrier"]
        if len(conditions) > 1:
            # each condition with someone affected or a carrier gets a colour in the key
            shown = [c for c in conditions
                     if any(int(r[5 + header.index(c)]) >= 2 for r in table)]
            assert sorted(session["legendLabels"].values()) == sorted(shown), name
            assert set(session["legendLabels"]) <= set(PHENOTYPE_PALETTE), name


def test_carriers_and_consanguinity_in_the_cousins_family():
    session = ped2studio.convert(read("cf-cousins.mped"))
    assert person(session, "III-1")["centerText"] == "dot"            # Carrier column 3
    assert person(session, "IV-3")["fillMode"] == "solid"              # affected
    text = {p["id"]: p["text"] for p in session["persons"]}
    kinds = {(text[pr["fromId"]], text[pr["toId"]]): pr["type"] for pr in session["partnerships"]}
    assert kinds[("IV-2", "IV-1")] == "consanguineous"                 # second cousins
    assert kinds[("I-1", "I-2")] == "normal"


def test_several_conditions_give_a_quartered_symbol():
    session = ped2studio.convert(read("features.mped"))
    ii2 = person(session, "II-2")                                    # affected by Condition X and Condition Y
    assert ii2["fillMode"] == "quartered" and len([q for q in ii2["quarters"] if q]) == 2


def test_the_same_id_in_two_families_is_two_people():
    notes = []
    session = ped2studio.convert(read("two-families.ped"), notes=notes)
    assert len(session["persons"]) == 7                       # 0.2.1 merged them into 4
    assert [p["text"] for p in session["persons"]] == ["1", "2", "3", "1", "2", "3", "4"]
    assert len(session["partnerships"]) == 2 and len(session["childLinks"]) == 3
    assert any("1, 2 and 3" in n and "more than one family" in n for n in notes)
    inds, _ = ped2studio.parse_ped(read("two-families.ped"))
    assert inds["F2/3"].father_id == "F2/1" and inds["F2/3"].label == "3"
    # ids used in one family only are left as they are
    inds, _ = ped2studio.parse_ped(read("simple.ped"))
    assert "II-1" in inds and inds["II-1"].father_id == "I-1"


def test_children_who_cannot_be_joined_to_their_parents_are_noted():
    notes = []
    ped = "F 1 0 0 1 1\nF 2 0 0 2 1\nF 3 0 2 2 2\nF 4 1 9 1 1\n"
    session = ped2studio.convert(ped, notes=notes)
    assert not session["childLinks"]
    assert any("3 has only one parent in the file, their mother 2" in n for n in notes)
    assert any("4's mother 9 is not in the file" in n for n in notes)
    assert ped2studio.convert(ped) == session                 # notes change nothing in the drawing


def test_single_condition_styles():
    text = read("simple.ped")
    s = ped2studio.convert(text, affected_color="#c0392b")
    assert person(s, "I-2")["fillColor"] == "#c0392b" and s["legendLabels"] == {"#c0392b": "Affected"}
    s = ped2studio.convert(text, fill_type="half")
    assert person(s, "I-2")["fillMode"] == "half" and person(s, "I-2")["halves"] == ["#1a2332", None]
    s = ped2studio.convert(text, use_shading=True, shading_pattern="dots", fill_type="half")
    p = person(s, "I-2")
    assert (p["fillMode"], p["shadingPattern"], p["shadingCoverage"]) == ("shading", "dots", "half-left")
    assert s["legendLabels"] == {"shading:dots:half-left": "Affected"}


def test_files_are_read_and_written_as_utf8(tmp_path):
    src = tmp_path / "family.ped"
    src.write_bytes("\ufeffFAM1 José 0 0 1 1\nFAM1 Zoë 0 0 2 1\nFAM1 Ana José Zoë 2 2\n".encode("utf-8"))
    out = tmp_path / "family.json"
    ped2studio.convert_file(str(src), str(out))
    session = json.loads(out.read_text(encoding="utf-8"))
    assert [p["text"] for p in session["persons"]] == ["José", "Zoë", "Ana"]
    assert parents_in(session) == {"Ana": ("José", "Zoë")}


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


def test_command_line(tmp_path):
    src = os.path.join(DATA, "two-families.ped")
    code, out, err = run_cli(src, str(tmp_path / "two.json"))
    assert code == 0, err
    assert "Converted: 7 individuals, 2 partnerships, 3 child links" in out
    assert "Note:" in out
    code, out, err = run_cli(src, str(tmp_path / "two.json"), "--shading", "--pattern", "dots", "--fill", "half")
    assert code == 0
    code, out, err = run_cli(os.path.join(DATA, "lynch.mped"), str(tmp_path / "lynch.json"), "--colour", "#c0392b")
    assert code == 0 and json.loads((tmp_path / "lynch.json").read_text(encoding="utf-8"))["persons"]
    code, out, err = run_cli(str(tmp_path / "missing.ped"), str(tmp_path / "x.json"))
    assert code == 1 and "file not found" in err
    code, out, err = run_cli(src, str(tmp_path / "no-such-folder" / "x.json"))
    assert code == 1 and "cannot write" in err and "missing.ped" not in err
    with pytest.raises(SystemExit):
        run_cli("--version")
