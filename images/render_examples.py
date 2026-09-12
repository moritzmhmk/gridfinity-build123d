"""Renders one SVG per example script, plus the library figures docs/ needs.

Each example is executed as ``__main__`` with the viewer stubbed out and the
working directory redirected, then the part it built is pulled out of the
script's own namespace and projected to an SVG. Rendering the object the
example actually builds keeps the pictures honest: they cannot drift from the
code they illustrate.

Run from the repository root::

    uv run images/render_examples.py
"""

from __future__ import annotations

import runpy
import sys
import tempfile
from pathlib import Path

from build123d import RGB, Compound, Edge, ExportSVG, Location, ShapeList

ROOT = Path(__file__).parents[1]
EXAMPLES = ROOT / "examples"
VIEWPORT = (100, -100, 100)


def _stub_viewer():
    import ocp_vscode

    ocp_vscode.show = lambda *a, **k: None
    ocp_vscode.show_object = lambda *a, **k: None
    ocp_vscode.show_all = lambda *a, **k: None


def run_example(script: Path, argv: list[str] | None = None) -> dict:
    """Executes an example and returns the globals it left behind."""
    saved_argv = sys.argv
    saved_cwd = Path.cwd()
    sys.argv = [script.name, *(argv or [])]
    with tempfile.TemporaryDirectory() as tmp:
        import os

        os.chdir(tmp)
        try:
            return runpy.run_path(str(script), run_name="__main__")
        finally:
            os.chdir(saved_cwd)
            sys.argv = saved_argv


def as_shape(obj):
    """Accepts a BuildPart, a BasePartObject or a Compound."""
    return getattr(obj, "part", obj)


def export(part, name: str, width: int = 400) -> None:
    part = as_shape(part)
    visible, _hidden = part.project_to_viewport(VIEWPORT, look_at=(0, 0, 0))
    size = Compound(children=list(visible)).bounding_box().size
    for darkmode in (False, True):
        exporter = ExportSVG(scale=width / size.X)
        color = RGB(240, 246, 252) if darkmode else RGB(31, 35, 40)
        exporter.add_layer("visible", line_color=color)
        exporter.add_shape(ShapeList[Edge](visible), layer="visible")
        suffix = "dark" if darkmode else "light"
        exporter.write(str(ROOT / "images" / f"{name}@{suffix}.svg"))
    print(f"  wrote {name}@light.svg / @dark.svg")


def side_by_side(parts: list, gap: float) -> Compound:
    """Lays parts out along x, separated by their own widths plus a gap."""
    placed = []
    x = 0.0
    for part in parts:
        shape = as_shape(part)
        width = shape.bounding_box().size.X
        placed.append(shape.moved(Location((x + width / 2, 0, 0))))
        x += width + gap
    return Compound(children=placed)


def main() -> None:
    _stub_viewer()
    # The project has no [build-system], so uv never installs it into .venv.
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT))  # solder-fume-fan imports examples.*

    print("overview.py")
    g = run_example(EXAMPLES / "overview.py")
    export(
        side_by_side(
            [
                g["bin_1x1"],
                g["bin_1x1_thick_walls"],
                g["bin_1x1_div2x2_scoop_label"],
            ],
            gap=10,
        ),
        "example-overview",
        width=600,
    )

    print("bin.py")
    g = run_example(
        EXAMPLES / "bin.py",
        [
            "--grid",
            "2x3",
            "--height",
            "4",
            "--div",
            "2x2",
            "--label",
            "--scoops",
            "back",
        ],
    )
    export(g["bin"], "example-bin")

    print("baseplate.py")
    g = run_example(EXAMPLES / "baseplate.py", ["--grid", "3x2"])
    export(g["baseplate"], "example-baseplate")

    print("screw_holes.py")
    g = run_example(EXAMPLES / "screw_holes.py", ["--grid", "2x2"])
    export(g["p"], "example-screw-holes")

    print("sliding_lid_bin.py")
    g = run_example(EXAMPLES / "sliding_lid_bin.py", ["--grid", "2x1"])
    bin_part = as_shape(g["bin"])
    lid = as_shape(g["lid"])
    height = bin_part.bounding_box().size.Z
    export(
        Compound(
            children=[bin_part, lid.moved(Location((0, 0, height + 10)))]
        ),
        "example-sliding-lid-bin",
    )

    print("pen_storage.py")
    g = run_example(EXAMPLES / "pen_storage.py")
    export(g["bin"], "example-pen-storage")

    print("pinecil_tip_storage.py")
    g = run_example(EXAMPLES / "pinecil_tip_storage.py")
    export(g["bin"], "example-pinecil-tip-storage")

    print("pinecil_soldering_iron_storage.py")
    g = run_example(EXAMPLES / "pinecil_soldering_iron_storage.py")
    export(g["bin"], "example-pinecil-soldering-iron-storage")

    print("engineer_ss_03_storage.py")
    g = run_example(EXAMPLES / "engineer_ss_03_storage.py")
    export(g["bin"], "example-engineer-ss-03-storage")

    print("solder-fume-fan.py")
    g = run_example(EXAMPLES / "solder-fume-fan.py")
    bin_part = as_shape(g["bin"])
    lid = as_shape(g["lid"])
    export(
        Compound(children=[bin_part, lid.moved(Location((0, 0, 6 * 7 + 10)))]),
        "example-solder-fume-fan",
    )

    print("PA-09_storage.py")
    g = run_example(EXAMPLES / "PA-09_storage" / "PA-09_storage.py")
    export(g["bin"], "example-pa-09-storage")

    # Library figures, built here rather than run from a script.
    print("baseplate")
    import gridfinity as gf

    export(
        gf.Baseplate(
            grid=[
                [True],
                [True],
                [True, True, True],
                [True, True, True, True],
            ]
        ),
        "baseplate",
    )


if __name__ == "__main__":
    main()
