---
title: "Configurable grid, baseplate, tests and documentation"
date: "2026-09-12"
pdf-engine: lualatex
style: |
  .markdown-preview.markdown-preview {
    font-size: 11pt;
    line-height: 1.5;
  }
puppeteer:
  displayHeaderFooter: true
  format: "A4"
  margin:
    top: "1.5cm"
    bottom: "1.5cm"
    left: "1cm"
    right: "1cm"
  headerTemplate: |
    <div style="font-family: Arial, sans-serif; font-size: 9pt; width: 100%; padding: 0 1cm; display: flex; justify-content: space-between; color: #000;">
      <span class="title"></span>
      <span class="date"></span>
    </div>
  footerTemplate: |
    <div style="font-family: Arial, sans-serif; font-size: 9pt; width: 100%; text-align: center; color: #000;">
      <span class="pageNumber"></span>/<span class="totalPages"></span>
    </div>
---

# Configurable grid, baseplate, tests and documentation

Accompanying note for a pull request against
`moritzmhmk/gridfinity-build123d`, describing every change, why it was made,
and how to verify it.

## 1. Summary

Six changes, in dependency order:

1. **Configurable grid pitch and height unit.** The 42 mm grid and the 7 mm
   height unit `U` become parameters carried by a new `GridSpec`, instead of
   literals scattered through `main.py`. Default behaviour is unchanged.
1. **`Baseplate`.** The one Gridfinity primitive the library lacked, built to
   the published specification.
1. **A test suite.** 45 tests, including a golden-geometry regression captured
   from the pre-change code, so the refactor can be shown to have altered
   nothing.
1. **Sphinx documentation** under `docs/`, building warning-free.
1. **Example documentation.** `examples/README.md` describes all eleven
   scripts, each with a rendered figure and its full source, plus a new
   `examples/baseplate.py`.
1. **Repository housekeeping.** pytest and Sphinx dev dependencies, a
   `.readthedocs.yaml`, `.gitignore` entries, removal of the stale
   `dev-requirements.txt`, and a portability fix to `images/render.py`.

Changes 1 and 2 are the substance. The rest exists to make them reviewable.

## 2. Backwards compatibility

No existing call site changes meaning, and no default geometry changes.

- Every new parameter is added **last among the named parameters**, before
  `**kwargs`, so existing positional and keyword calls are unaffected.
- `spec` defaults to a shared `GridSpec()` instance that holds the standard
  42 mm / 7 mm values.
- Nothing in `examples/` was modified to accommodate the change, apart from
  adding a new script.
- The claim is enforced mechanically: `tests/golden_42_7.json` records the
  bounding box and volume of every component **as built by the code before
  this work**, and `tests/test_geometry_regression.py` asserts they still
  match. See section 5.

## 3. Configurable grid pitch and height unit

### 3.1 The new type

`src/gridfinity/spec.py`, twenty lines:

```python
@dataclass(frozen=True)
class GridSpec:
    size: float = 42.0   # x/y grid pitch, mm
    unit: float = 7.0    # z height unit U, mm


DEFAULT = GridSpec()
```

Exported as `gridfinity.GridSpec`, with the module available as
`gridfinity.spec`. A fractional height unit is expressed by multiplying, for
example `GridSpec(size=61.5, unit=0.75 * 7)`; no separate scale field was
added.

### 3.2 Threading

Each component gained `spec: GridSpec = DEFAULT`:

| Component | File | Use |
|---|---|---|
| `Bin` | `main.py` | `spec.unit` for the default compartment depth; forwards `spec` to `Base`, `GridSketch`, `Compartment`, `StackingLip` |
| `Base` | `main.py` | `spec.size` for pad footprint and placement |
| `Compartment` | `main.py` | forwards to `GridSketch` |
| `StackingLip` | `main.py` | forwards to `GridSketch` |
| `GridSketch` | `main.py` | `spec.size` for cell size and placement |
| `extra.SubdividedCompartment` | `extra.py` | forwards to `GridSketch` |

### 3.3 Literal substitutions

All five are in `src/gridfinity/main.py`:

| Was | Now | Meaning |
|---|---|---|
| `Rectangle(42 - 0.5, 42 - 0.5)` | `Rectangle(spec.size - 0.5, spec.size - 0.5)` | base pad footprint |
| `IrregularGridLocations(42, 42, grid)` in `Base` | `IrregularGridLocations(spec.size, spec.size, grid)` | pad placement |
| `IrregularGridLocations(42, 42, grid)` in `GridSketch` | `IrregularGridLocations(spec.size, spec.size, grid)` | cell placement |
| `Rectangle(42, 42)` | `Rectangle(spec.size, spec.size)` | cell footprint |
| `Compartment(grid, height - 7)` | `Compartment(grid, height - spec.unit, spec=spec)` | default compartment inset by one `U` |

### 3.4 Literals deliberately left absolute

These matched a search for `42` or `7` but are not grid pitch or height units.
They are profile geometry fixed by the physical standard and by printing
constraints, and must stay identical at any pitch:

| Location | Value | What it is |
|---|---|---|
| `main.py`, `Base` | `0.5` | pad-to-cell clearance |
| `main.py`, `Base` | `3.75` | pad corner fillet radius |
| `main.py`, `Base` | `[2.15, 1.8, 0.8]` | base profile heights |
| `main.py`, `Compartment` | `0.25`, `1.0` | wall inset, wall thickness |
| `main.py`, `StackingLip` | `1.9, 1.8, 0.7`, `1.2`, `0.6` | lip and support profile |
| `main.py`, `GridSketch` | `4 - inset` | outer corner fillet radius |
| `extra.py` | `scoop_radius = 7.0` | a radius in mm, not a height unit |
| `extra.py` | `0.7` | 1:0.7 label overhang ratio |
| `extra.py` | `14`, `10`, `2`, `0.45` | label width, divider cutout limits, fillets |

A bin at `size=61.5` therefore has the same walls, corners and lip as one at
42 mm; only the footprint changes. Parts on a non-standard pitch are consistent
with each other and do not interoperate with standard Gridfinity, which is
stated wherever the feature is documented.

### 3.5 Usage

```python
import gridfinity as gf

spec = gf.GridSpec(size=61.5, unit=7.0)

grid = [[True, True], [True, True]]
bin = gf.Bin(grid=grid, height=3 * spec.unit + 4.75, spec=spec)
plate = gf.Baseplate(grid=grid, spec=spec)
```

## 4. Baseplate

`gridfinity.Baseplate(grid, spec=DEFAULT)` in `main.py`, built from the
`Baseplate Design` and `Enlarged Baseplate` panels of the Gridfinity
specification at <https://gridfinity.xyz/specification/>.

- **Body**: `GridSketch(grid, inset=0, spec=spec)` extruded 4.65 mm. The 8.0 mm
  outer corner diameter in the drawing falls out of `GridSketch`'s existing
  `4 - inset` fillet, so no new constant was introduced.
- **Socket**, one per occupied cell, subtracted: from a
  `Rectangle(spec.size - 0.5, spec.size - 0.5)` filleted 3.75 mm at the top,
  2.15 mm of 45-degree taper, 1.8 mm of vertical wall, 0.7 mm of 45-degree
  taper. Total 4.65 mm, the `~5mm` on the drawing.
- **Placement**: `IrregularGridLocations`, the same helper `Base` uses, so
  ragged grids and holes work with no additional code.

The socket's 0.7 mm bottom chamfer against the bin foot's 0.8 mm
(`main.py`, `Base`) is the fit clearance, not an inconsistency: the socket is
0.1 to 0.2 mm wider than the foot at every height. That is asserted by a test
rather than by argument, see section 5.2.

The plate height is absolute and does not scale with `GridSpec`; the cell pitch
does, so a 61.5 mm plate accepts 61.5 mm bins.

## 5. Tests

New `tests/` directory, run with pytest. 45 tests, about 50 seconds, dominated
by the example scripts.

| File | Tests | Purpose |
|---|---|---|
| `test_geometry_regression.py` | 13 | Default-spec geometry against `golden_42_7.json` |
| `test_grid_spec.py` | 13 | `GridSpec` behaviour and derived dimensions |
| `test_baseplate.py` | 7 | Baseplate geometry and fit |
| `test_examples.py` | 12 | Every example script runs; README source blocks are accurate |

### 5.1 Golden regression

`tests/golden_42_7.json` was generated from the unmodified 42/7 code **before
any source edit**, recording bounding box and volume for `Base`, `Bin` in five
configurations, `Compartment`, `StackingLip`, `SubdividedCompartment` and three
`GridSketch` cases. The tests assert those values still hold. This is what
substantiates the compatibility claim in section 2; it is a genuine
before/after comparison, not a snapshot of the new behaviour.

The file must never be regenerated from current code. Doing so would silently
destroy the guarantee.

### 5.2 Baseplate fit

Bounding boxes cannot show that a socket has the right profile. The test that
does:

```python
def test_a_bin_foot_fits_into_the_socket():
    plate = gf.Baseplate(grid=GRID_1X1)
    foot = gf.Base(grid=GRID_1X1)
    overlap = plate.intersect(foot)
    assert volume_of(overlap) == pytest.approx(0.0, abs=1e-6)
```

A wrong chamfer, wall height or footprint anywhere along the profile produces a
non-zero intersection. The same assertion runs at `size=61.5`.

### 5.3 Example scripts

`test_examples.py` runs every script under `examples/` as `__main__` with
`ocp_vscode.show` stubbed and the working directory redirected to a temp
directory, so STL exports are captured and discarded. New scripts are picked up
automatically. A twelfth test checks that the source blocks embedded in
`examples/README.md` still match the files they quote.

### 5.4 Development order

The work was done test-first. The `GridSpec` tests were written and watched to
fail with `AttributeError: module 'gridfinity' has no attribute 'GridSpec'`
while the golden tests passed against untouched source; the same for
`Baseplate`. One baseplate test failed after implementation and the test was at
fault, not the code: it assumed a 2x2 plate is four 1x1 plates, but merging
cells removes twelve filleted corners, a 191.6 mm3 difference that matched the
discrepancy exactly. It was rewritten to use each grid's own sketch area.

## 6. Documentation

`docs/`, laid out in the style of `Ruudjhuu/gridfinity_build123d`:

```text
docs/
    Makefile
    make.bat
    requirements.txt
    source/
        conf.py
        index.rst        intro, installation, quickstart
        objects.rst      Bin, Baseplate, compartments, building blocks
        grid.rst         GridSpec: pitch and U, what scales and what does not
        reference.rst    toctree into the API pages
        gridfinity.rst   automodule for main, extra, spec, utils, types
```

Sphinx 9.1.0 with `sphinx-rtd-theme` 3.1.0 and `sphinx-design` 0.7.0, all in
the `dev` dependency group; `docs/requirements.txt` carries the same pins for
Read the Docs.

Two points of note:

- `conf.py` copies the repository's existing `images/*.svg` into
  `source/assets/` on `builder-inited`. Sphinx cannot read images from outside
  its source directory, and a second committed copy would drift; the generated
  directory is gitignored.
- `autoclass_content = "both"`, not the more usual `"init"`. The class
  docstrings carry the descriptions and argument lists and `__init__` has none,
  so `"init"` silently discarded every one of them while still producing a
  clean build.

Google-style docstrings were added to `Bin`, `Base`, `Baseplate`,
`Compartment`, `StackingLip`, `GridSketch` and `SubdividedCompartment`,
documenting every argument.

## 7. Examples

### 7.1 `examples/README.md`

Rewritten from a four-line note into a guide to all eleven scripts, grouped as
learning the API, parametric generators, and one-off designs shaped around a
real object. Each section explains the design and the mechanism, carries a
rendered figure, and ends with the script's complete source quoted verbatim.

The verbatim quoting is enforced by a test (section 5.3), so a script cannot be
edited without the README being updated.

Two observations recorded rather than fixed, since they are pre-existing and
harmless: `pen_storage.py` has a leftover `print(d)`, and the grip-hole sketch
in `pinecil_tip_storage.py` has its `extrude` commented out.

**The file is long** -- 1584 lines, most of it quoted source. If that is
unwelcome, the same content works with each source block inside a `<details>`
element, or with the blocks dropped entirely; both are small changes.

### 7.2 `examples/baseplate.py`

A new script, deliberately the same shape as `bin.py`: the same `parse_size`
for `WxH`, the same `--preview`, the same self-describing output filename. It
adds `--grid-size`, the only place in `examples/` that exercises `GridSpec`. A
non-default pitch appears in the filename, `baseplate_2x2_61.5mm.stl`, so a
non-standard plate cannot later be mistaken for a standard one.

### 7.3 Figures

`images/render_examples.py` renders one SVG per example, plus the library
figures. It executes each script as `__main__` with the viewer stubbed and the
working directory redirected, then takes the object the script itself built out
of its globals and projects it with the same viewport and colours
`images/render.py` already used. Rendering what the script builds, rather than
a hand-written replica, is what keeps the figures from drifting.

24 new SVGs, light and dark variants as elsewhere in the repository, referenced
with the existing `#gh-light-mode-only` / `#gh-dark-mode-only` convention.

`images/specification.png` is the Gridfinity Design Reference v5 sheet, added
at the top of `examples/README.md` with its source URL. **It is licensed
CC BY-NC-SA** (graphic by @willtree8; Gridfinity by Zack Freedman) while this
repository is MIT. Attribution is given, but the mismatch is real: if it is
unwelcome in the tree, hotlinking it or linking to the specification page in
text are the alternatives.

## 8. Repository and tooling

| Change | Detail |
|---|---|
| `pyproject.toml` | `dev` group gains `pytest`, `sphinx`, `sphinx-rtd-theme`, `sphinx-design`; new `[tool.pytest.ini_options]` with `pythonpath = ["src", "."]` and `testpaths = ["tests"]`; new `[tool.uv] package = true` |
| `uv.lock` | Regenerated for the dev dependencies above. No runtime dependency changed |
| `.gitignore` | `.pytest_cache`, `.ruff_cache`, `Thumbs.db`, `docs/build/`, `docs/source/assets/`, and a root-only `/*.stl` |
| `.readthedocs.yaml` | New: ubuntu-24.04, Python 3.12, `docs/requirements.txt`, `fail_on_warning: true` |
| `dev-requirements.txt` | Removed. Nothing referenced it and its pins (`ocp_vscode==2.6.1`) contradicted `uv.lock` |
| `images/render.py` | Portability fix, see below |

`[tool.uv] package = true` makes `uv sync` install the project itself into
`.venv`, editable. Without it, uv treats a project with no `[build-system]` as
non-packaged, so `uv sync` installs the dependencies but not `gridfinity`, and
the examples cannot import it. The setting is namespaced under `[tool.uv]`, so
it changes nothing for pip or for any PEP 517 consumer.

`images/render.py` hardcoded `/Users/moritz/Library/Fonts/FiraCode-Light.ttf`
and could not run on any machine without that file. It now searches a small
list of candidate paths and falls back to the default font, and puts `src` on
`sys.path` the way `render_examples.py` does. Verified by running it with the
working directory set elsewhere, so the committed SVGs were not overwritten.

The `/*.stl` ignore rule is root-only on purpose: the example scripts export
into the working directory, while `examples/PA-09_storage/PA-09_storage.stl` is
tracked and must stay.

## 9. Deliberately not done

- **`requires-python` in `pyproject.toml`.** `uv.lock` requires `>=3.12` but
  `pyproject.toml` says nothing, so a bare `uv sync` picks whatever `python`
  resolves to and fails on 3.14, for which no `cadquery-ocp` wheel exists.
  Adding the field would fix that in one line, but it changes published package
  metadata, so it is left to the maintainer. The `uv sync --python 3.12`
  requirement is documented in `examples/README.md` and
  `docs/source/index.rst` instead.
- **`CHANGELOG.md`.** Untouched; it is the maintainer's document. `GridSpec`
  and `Baseplate` are both unreleased.
- **Reformatting.** `examples/screw_holes.py`, `examples/sliding_lid_bin.py`
  and `images/render.py` do not satisfy `ruff format --check`, which predates
  this work. Only files this work touched were formatted.
- **Print verification.** All geometry here is verified numerically. A 61.5 mm
  part has not yet been printed.

## 10. Verification

```shell
uv sync --python 3.12
uv run pytest -q
uv run ruff check src/gridfinity tests examples images
uv run sphinx-build -W -b html docs/source docs/build/html
```

Expected, as of this writing:

```text
45 passed
All checks passed!
build succeeded.
```

`--python 3.12` is required for the reason in section 9; 3.13 also works. The
`-W` on the documentation build is the point: a clean build, not merely HTML
output, is the success criterion.

## 11. Diffstat

New files:

| Path | Lines |
|---|---|
| `src/gridfinity/spec.py` | 20 |
| `tests/conftest.py`, `test_geometry_regression.py`, `test_grid_spec.py`, `test_baseplate.py`, `test_examples.py`, `golden_42_7.json` | 430 |
| `docs/` | 468 across 11 files |
| `examples/baseplate.py` | 69 |
| `images/render_examples.py` | 188 |
| `.readthedocs.yaml` | 15 |
| `images/*.svg` (24 figures), `images/specification.png` | generated |

Modified:

| Path | Change |
|---|---|
| `src/gridfinity/main.py` | +116 / -14 |
| `src/gridfinity/extra.py` | +28 / -1 |
| `src/gridfinity/__init__.py` | +13 / -2 |
| `README.md` | +59 / -1, `### Baseplate` and `# Non-standard grid sizes` |
| `examples/README.md` | rewritten, +1576 / -3, now 1584 lines |
| `images/render.py` | +36 / -8, portability |
| `pyproject.toml` | +11 |
| `.gitignore` | +12 |
| `uv.lock` | dev dependencies only |

Deleted: `dev-requirements.txt`.
