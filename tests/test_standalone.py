"""ped2studio_standalone.py must be the package in one file, and behave exactly as the package does."""
import importlib.util
import json
import os
import subprocess
import sys

import pytest

import ped2studio

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "ped2studio_standalone.py")
DATA = os.path.join(os.path.dirname(__file__), "data")
INPUTS = ["simple.ped", "two-families.ped", "okafor.mped", "cf-cousins.mped", "features.mped"]
OPTIONS = [[], ["--fill", "half", "--colour", "#c0392b"], ["--shading", "--pattern", "dots", "--fill", "half"]]

pytestmark = pytest.mark.skipif(not os.path.exists(SCRIPT), reason="the standalone script is not here")


def test_the_script_is_up_to_date():
    """If this fails, run: python tools/make_standalone.py"""
    spec = importlib.util.spec_from_file_location("make_standalone", os.path.join(ROOT, "tools", "make_standalone.py"))
    maker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(maker)
    with open(SCRIPT, encoding="utf-8") as fh:
        assert fh.read() == maker.build()


@pytest.mark.parametrize("options", OPTIONS, ids=["default", "half", "shading"])
def test_the_script_writes_what_the_package_writes(tmp_path, options):
    keyword = {"--fill": "fill_type", "--colour": "affected_color", "--pattern": "shading_pattern"}
    kwargs = {keyword[k]: v for k, v in zip(options, options[1:]) if k in keyword}
    if "--shading" in options:
        kwargs["use_shading"] = True
    for name in INPUTS:
        src = os.path.join(DATA, name)
        out = tmp_path / (name + ".json")
        done = subprocess.run([sys.executable, SCRIPT, src, str(out)] + options, capture_output=True, text=True)
        assert done.returncode == 0, done.stderr
        with open(src, encoding="utf-8") as fh:
            expected = ped2studio.convert(fh.read(), **kwargs)
        assert json.loads(out.read_text(encoding="utf-8")) == expected, name


def test_the_script_reports_its_version():
    done = subprocess.run([sys.executable, SCRIPT, "--version"], capture_output=True, text=True)
    assert done.stdout.strip() == "ped2studio " + ped2studio.__version__
