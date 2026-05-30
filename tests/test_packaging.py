"""Packaging sanity: the pyproject must stay consistent with the code, so the
`pipx`/`uvx` install keeps working. These are fast and need no build step.
"""

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYPROJECT = os.path.join(ROOT, "pyproject.toml")

tomllib = pytest.importorskip("tomllib") if sys.version_info >= (3, 11) else None
pytestmark = pytest.mark.skipif(tomllib is None, reason="needs tomllib (py3.11+)")


def _load():
    with open(PYPROJECT, "rb") as fh:
        return tomllib.load(fh)


def test_pyproject_exists_and_parses():
    data = _load()
    assert data["project"]["name"] == "hilbertbrane"


def test_console_entry_point_targets_are_callable():
    # `hilbertbrane = hilbert_gen:main`
    import hilbert_gen
    assert callable(hilbert_gen.main)


def test_tuner_entry_point_target_is_callable():
    pytest.importorskip("pyvista")
    import tuner_trame
    assert callable(tuner_trame.main)


def test_scripts_match_module_functions():
    scripts = _load()["project"]["scripts"]
    assert scripts["hilbertbrane"] == "hilbert_gen:main"
    assert scripts["hilbertbrane-tuner"] == "tuner_trame:main"


def test_declared_modules_all_exist():
    mods = _load()["tool"]["setuptools"]["py-modules"]
    for m in mods:
        assert os.path.exists(os.path.join(ROOT, m + ".py")), f"missing module {m}.py"


def test_legacy_scripts_are_not_packaged():
    mods = set(_load()["tool"]["setuptools"]["py-modules"])
    for legacy in ("HilbertGyri", "HilbertGyri2", "interactive_tuner", "brain_box"):
        assert legacy not in mods


def test_version_source_matches_code():
    data = _load()
    # version is dynamic, sourced from provenance.VERSION
    assert "version" in data["project"].get("dynamic", [])
    attr = data["tool"]["setuptools"]["dynamic"]["version"]["attr"]
    assert attr == "provenance.VERSION"
    import provenance
    assert isinstance(provenance.VERSION, str) and provenance.VERSION
