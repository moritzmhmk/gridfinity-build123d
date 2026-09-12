"""The baseplate is a plate of sockets that bin feet drop into."""

import pytest
from conftest import GRID_1X1, GRID_2X2, size_of

import gridfinity as gf

PITCH = 61.5
TOL = 1e-6
HEIGHT = 4.65  # 0.7 + 1.8 + 2.15, per the Gridfinity specification


def volume_of(shape):
    """An empty intersection comes back as None rather than a null solid."""
    return 0.0 if shape is None else shape.volume


RAGGED = [
    [True],
    [True],
    [True, True, True],
    [True, True, True, True],
]


def test_baseplate_is_one_cell_wide_and_spec_high():
    x, y, z = size_of(gf.Baseplate(grid=GRID_1X1))
    assert x == pytest.approx(42.0, abs=TOL)
    assert y == pytest.approx(42.0, abs=TOL)
    assert z == pytest.approx(HEIGHT, abs=TOL)


def test_baseplate_spans_the_whole_grid():
    x, y, _ = size_of(gf.Baseplate(grid=GRID_2X2))
    assert x == pytest.approx(84.0, abs=TOL)
    assert y == pytest.approx(84.0, abs=TOL)


def test_ragged_grid_is_bounded_by_its_widest_row():
    x, y, _ = size_of(gf.Baseplate(grid=RAGGED))
    assert x == pytest.approx(4 * 42.0, abs=TOL)
    assert y == pytest.approx(4 * 42.0, abs=TOL)


def test_each_occupied_cell_gets_one_socket():
    """Volume removed must scale with the number of occupied cells.

    Each grid's own sketch area is used as the uncut solid: a 2x2 plate is not
    four 1x1 plates, because merging the cells removes twelve filleted corners.
    """

    def removed(grid):
        solid = gf.GridSketch(grid, spec=gf.GridSpec()).area * HEIGHT
        return solid - gf.Baseplate(grid=grid).volume

    assert removed(GRID_2X2) == pytest.approx(4 * removed(GRID_1X1), rel=1e-9)


def test_a_bin_foot_fits_into_the_socket():
    """The socket must clear the bin foot at every height."""
    plate = gf.Baseplate(grid=GRID_1X1)
    foot = gf.Base(grid=GRID_1X1)
    overlap = plate.intersect(foot)
    assert volume_of(overlap) == pytest.approx(0.0, abs=1e-6)


def test_socket_follows_the_spec_pitch():
    plate = gf.Baseplate(grid=GRID_2X2, spec=gf.GridSpec(size=PITCH))
    x, y, z = size_of(plate)
    assert x == pytest.approx(2 * PITCH, abs=TOL)
    assert y == pytest.approx(2 * PITCH, abs=TOL)
    assert z == pytest.approx(HEIGHT, abs=TOL), "profile must not scale"


def test_a_bin_foot_fits_a_baseplate_of_the_same_spec():
    spec = gf.GridSpec(size=PITCH)
    plate = gf.Baseplate(grid=GRID_1X1, spec=spec)
    foot = gf.Base(grid=GRID_1X1, spec=spec)
    overlap = plate.intersect(foot)
    assert volume_of(overlap) == pytest.approx(0.0, abs=1e-6)
