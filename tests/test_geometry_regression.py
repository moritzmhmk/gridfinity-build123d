"""Default-spec geometry must stay bit-for-bit what the 42/7 code produced.

The expected values in golden_42_7.json were captured from the code before
the grid/unit parameterisation. Any change here means the refactor altered
geometry that was supposed to stay identical.
"""

import pytest
from conftest import GRID_1X1, GRID_2X2, GRID_G, size_of

import gridfinity as gf

TOL = 1e-6


def parts():
    return {
        "base_1x1": gf.Base(grid=GRID_1X1),
        "base_2x2": gf.Base(grid=GRID_2X2),
        "stacking_lip_1x1": gf.StackingLip(grid=GRID_1X1),
        "compartment_1x1_h14": gf.Compartment(GRID_1X1, 14),
        "bin_1x1_h21": gf.Bin(grid=GRID_1X1, height=21),
        "bin_2x2_h21": gf.Bin(grid=GRID_2X2, height=21),
        "bin_g_h21": gf.Bin(grid=GRID_G, height=21),
        "bin_1x1_h21_no_lip": gf.Bin(
            grid=GRID_1X1, height=21, stacking_lip=None
        ),
        "bin_1x1_h21_filled": gf.Bin(
            grid=GRID_1X1, height=21, compartment=None
        ),
        "subdivided_1x1_h14": gf.extra.SubdividedCompartment(
            GRID_1X1,
            height=14,
            div_x=1,
            div_y=2,
            with_label=True,
            scoops=["back"],
        ),
    }


@pytest.fixture(scope="module")
def built():
    return parts()


@pytest.mark.parametrize(
    "name",
    [
        "base_1x1",
        "base_2x2",
        "stacking_lip_1x1",
        "compartment_1x1_h14",
        "bin_1x1_h21",
        "bin_2x2_h21",
        "bin_g_h21",
        "bin_1x1_h21_no_lip",
        "bin_1x1_h21_filled",
        "subdivided_1x1_h14",
    ],
)
def test_part_matches_golden(built, golden, name):
    expected = golden[name]
    x, y, z = size_of(built[name])
    assert x == pytest.approx(expected["x"], abs=TOL)
    assert y == pytest.approx(expected["y"], abs=TOL)
    assert z == pytest.approx(expected["z"], abs=TOL)
    assert built[name].volume == pytest.approx(expected["volume"], abs=1e-3)


@pytest.mark.parametrize(
    "name,sketch_args",
    [
        ("grid_sketch_1x1_inset025", (GRID_1X1, 0.25)),
        ("grid_sketch_2x2_inset025", (GRID_2X2, 0.25)),
        ("grid_sketch_g_inset0", (GRID_G, 0)),
    ],
)
def test_grid_sketch_matches_golden(golden, name, sketch_args):
    grid, inset = sketch_args
    sketch = gf.GridSketch(grid, inset=inset)
    expected = golden[name]
    x, y, _ = size_of(sketch)
    assert x == pytest.approx(expected["x"], abs=TOL)
    assert y == pytest.approx(expected["y"], abs=TOL)
    assert sketch.area == pytest.approx(expected["area"], abs=1e-3)
