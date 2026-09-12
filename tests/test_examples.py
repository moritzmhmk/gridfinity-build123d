"""Every example script must still build and export.

The scripts are run as `__main__` with the viewer stubbed out and the
working directory redirected, so their STL exports land in a temp dir.
"""

import pathlib
import re
import runpy
import sys

import ocp_vscode
import pytest

EXAMPLES_DIR = pathlib.Path(__file__).parent.parent / "examples"
SCRIPTS = sorted(
    p for p in EXAMPLES_DIR.rglob("*.py") if p.name != "__init__.py"
)


@pytest.fixture(autouse=True)
def no_viewer(monkeypatch):
    monkeypatch.setattr(ocp_vscode, "show", lambda *a, **k: None)


@pytest.mark.parametrize("script", SCRIPTS, ids=[p.stem for p in SCRIPTS])
def test_example_runs(script, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [script.name])
    runpy.run_path(str(script), run_name="__main__")


SOURCE_BLOCK = re.compile(
    r"### Source\n\n`([^`]+)`\n\n```python\n(.*?)\n```", re.DOTALL
)


def test_readme_quotes_every_script_verbatim():
    """README.md embeds each script's source; keep those copies true."""
    readme = EXAMPLES_DIR / "README.md"
    blocks = SOURCE_BLOCK.findall(readme.read_text(encoding="utf-8"))
    assert len(blocks) == len(SCRIPTS), "one source block per example script"
    root = EXAMPLES_DIR.parent
    for path, quoted in blocks:
        actual = (root / path).read_text(encoding="utf-8").rstrip("\n")
        assert quoted == actual, f"{path} has drifted from README.md"
