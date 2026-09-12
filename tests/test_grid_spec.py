"""Grid pitch and height unit are settable from application code."""

import dataclasses

import pytest
from conftest import GRID_1X1, GRID_2X2, size_of

import gridfinity as gf

PITCH = 61.5
TOL = 1e-6


def test_default_spec_is_standard_gridfinity():
    spec = gf.GridSpec()
    assert spec.size == 42.0
    assert spec.unit == 7.0


def test_spec_is_immutable():
    spec = gf.GridSpec()
    with pytest.raises(dataclasses.FrozenInstanceError):
        spec.size = 61.5


def test_base_pitch_follows_spec():
    spec = gf.GridSpec(size=PITCH)
    x, y, z = size_of(gf.Base(grid=GRID_1X1, spec=spec))
    assert x == pytest.approx(PITCH - 0.5, abs=TOL)
    assert y == pytest.approx(PITCH - 0.5, abs=TOL)
    assert z == pytest.approx(4.75, abs=TOL), "z profile must not scale"


def test_base_pitch_follows_spec_on_multi_cell_grid():
    spec = gf.GridSpec(size=PITCH)
    x, y, _ = size_of(gf.Base(grid=GRID_2X2, spec=spec))
    assert x == pytest.approx(2 * PITCH - 0.5, abs=TOL)
    assert y == pytest.approx(2 * PITCH - 0.5, abs=TOL)


def test_grid_sketch_pitch_follows_spec():
    sketch = gf.GridSketch(GRID_2X2, inset=0.25, spec=gf.GridSpec(size=PITCH))
    x, y, _ = size_of(sketch)
    assert x == pytest.approx(2 * PITCH - 0.5, abs=TOL)
    assert y == pytest.approx(2 * PITCH - 0.5, abs=TOL)


def test_compartment_pitch_follows_spec():
    part = gf.Compartment(GRID_1X1, 14, spec=gf.GridSpec(size=PITCH))
    x, _, z = size_of(part)
    assert x == pytest.approx(PITCH - 2.5, abs=TOL)
    assert z == pytest.approx(14, abs=TOL)


def test_stacking_lip_pitch_follows_spec():
    part = gf.StackingLip(grid=GRID_1X1, spec=gf.GridSpec(size=PITCH))
    x, _, z = size_of(part)
    assert x == pytest.approx(PITCH - 0.5, abs=TOL)
    assert z == pytest.approx(3.551472, abs=TOL), "lip profile must not scale"


def test_bin_pitch_follows_spec():
    part = gf.Bin(grid=GRID_1X1, height=21, spec=gf.GridSpec(size=PITCH))
    x, y, z = size_of(part)
    assert x == pytest.approx(PITCH - 0.5, abs=TOL)
    assert y == pytest.approx(PITCH - 0.5, abs=TOL)
    assert z == pytest.approx(24.551472, abs=TOL), "z profile must not scale"


def test_subdivided_compartment_pitch_follows_spec():
    part = gf.extra.SubdividedCompartment(
        GRID_1X1,
        height=14,
        div_x=1,
        div_y=2,
        spec=gf.GridSpec(size=PITCH),
    )
    _, y, _ = size_of(part)
    assert y == pytest.approx(PITCH - 2.5, abs=TOL)


def test_bin_default_compartment_depth_follows_unit():
    """Bin's default compartment is inset by one U from the top."""
    unit = 3.5
    explicit = gf.Bin(
        grid=GRID_1X1,
        height=21,
        compartment=gf.Compartment(GRID_1X1, 21 - unit),
    )
    from_spec = gf.Bin(grid=GRID_1X1, height=21, spec=gf.GridSpec(unit=unit))
    assert from_spec.volume == pytest.approx(explicit.volume, abs=1e-3)


def test_fractional_unit_removes_more_material_than_full_unit():
    full = gf.Bin(grid=GRID_1X1, height=21)
    fractional = gf.Bin(
        grid=GRID_1X1, height=21, spec=gf.GridSpec(unit=0.5 * 7)
    )
    assert fractional.volume < full.volume


def test_explicit_default_spec_matches_no_spec():
    assert gf.Bin(
        grid=GRID_1X1, height=21, spec=gf.GridSpec()
    ).volume == pytest.approx(
        gf.Bin(grid=GRID_1X1, height=21).volume, abs=1e-9
    )


def test_bin_passes_spec_to_its_default_parts():
    """A bin built at 61.5 mm must not contain 42 mm sub-parts."""
    part = gf.Bin(grid=GRID_2X2, height=21, spec=gf.GridSpec(size=PITCH))
    x, y, _ = size_of(part)
    assert x == pytest.approx(2 * PITCH - 0.5, abs=TOL)
    assert y == pytest.approx(2 * PITCH - 0.5, abs=TOL)
