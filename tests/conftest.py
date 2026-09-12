import json
import pathlib

import pytest

GRID_1X1 = [[True]]
GRID_2X2 = [[True, True], [True, True]]
GRID_G = [
    [True, True, True],
    [True, False, True],
    [True, True, True],
    [False, False, True],
    [True, True, True],
]

GOLDEN_PATH = pathlib.Path(__file__).parent / "golden_42_7.json"


@pytest.fixture(scope="session")
def golden():
    return json.loads(GOLDEN_PATH.read_text())


def size_of(obj):
    s = obj.bounding_box().size
    return (s.X, s.Y, s.Z)
