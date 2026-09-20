from collections.abc import Sequence
from typing import NamedTuple


class Grid(NamedTuple):
    cells: Sequence[Sequence[bool]]
    cell_size: tuple[float, float] = (42, 42)

    @classmethod
    def filled(
        cls,
        width: int,
        height: int,
        *,
        cell_size: tuple[float, float] = (42, 42)
    ) -> "Grid":
        return cls(
            cells=[[True] * width] * height,
            cell_size=cell_size
        )
