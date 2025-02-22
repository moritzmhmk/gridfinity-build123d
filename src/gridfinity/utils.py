from build123d import (
    Align,
    Axis,
    BuildPart,
    Face,
    Location,
    Locations,
    Plane,
    Vector,
    to_align_offset
)

from .types import Grid


def faces_xy(p: BuildPart) -> list[Face]:
    return p.faces().filter_by(Plane.XY).sort_by(Axis.Z)


class IrregularGridLocations(Locations):
    def __init__(
        self,
        x_spacing: float,
        y_spacing: float,
        grid: Grid,
        align: Align | tuple[Align, Align] = (Align.CENTER, Align.CENTER),
    ):
        indices = [(i, j) for i, row in enumerate(grid)
                   for j, val in enumerate(row) if val]

        n_rows = max(i for i, j in indices) + 1
        n_cols = max(j for i, j in indices) + 1

        size = [x_spacing * (n_cols - 1), y_spacing * (n_rows - 1)]
        align_offset = to_align_offset((0, 0), size, align)

        locations = [
            Location(align_offset + Vector(
                j * x_spacing, (n_rows-i-1) * y_spacing
            ))
            for i, j in indices
        ]

        super().__init__(*locations)
