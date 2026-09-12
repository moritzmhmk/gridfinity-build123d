# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]

sys.path.insert(0, str((ROOT / "src").resolve()))

project = "gridfinity"
copyright = "2025, moritzmhmk"  # noqa: A001
author = "moritzmhmk"
release = "1.1.0"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = []

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# "both" rather than the more common "init": the class docstrings carry the
# descriptions and the argument lists, and __init__ has none of its own.
autoclass_content = "both"
autodoc_typehints = "description"


# -- Figures -----------------------------------------------------------------
# The SVGs in the repository's top-level images/ directory are the same ones
# README.md uses. Sphinx cannot read image files from outside its source
# directory, so they are copied into source/assets/ at build time rather than
# kept as a second checked-in copy that could drift.


def _copy_images(app):
    destination = Path(app.srcdir) / "assets"
    destination.mkdir(exist_ok=True)
    for svg in sorted((ROOT / "images").glob("*.svg")):
        shutil.copy2(svg, destination / svg.name)


def setup(app):
    app.connect("builder-inited", _copy_images)
