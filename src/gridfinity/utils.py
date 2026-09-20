from build123d import (
    Align,
    Axis,
    BuildPart,
    Face,
    Location,
    Locations,
    Plane,
    Vector,
    to_align_offset,
)

from .types import Grid


def faces_xy(p: BuildPart) -> list[Face]:
    return p.faces().filter_by(Plane.XY).sort_by(Axis.Z)


class IrregularGridLocations(Locations):
    def __init__(
        self,
        grid: Grid,
        align: Align | tuple[Align, Align] = (Align.CENTER, Align.CENTER),
    ):
        indices = [
            (i, j)
            for i, row in enumerate(grid.cells)
            for j, val in enumerate(row)
            if val
        ]

        n_rows = max(i for i, j in indices) + 1
        n_cols = max(j for i, j in indices) + 1

        size = [grid.cell_size[0] * (n_cols - 1), grid.cell_size[1] * (n_rows - 1)]
        align_offset = to_align_offset((0, 0), size, align)

        locations = [
            Location(
                align_offset
                + Vector(j * grid.cell_size[0], (n_rows - i - 1) * grid.cell_size[1])
            )
            for i, j in indices
        ]

        super().__init__(*locations)
