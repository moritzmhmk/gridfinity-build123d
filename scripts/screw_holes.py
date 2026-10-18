import argparse

from build123d import (
    Align,
    BasePartObject,
    BuildPart,
    BuildSketch,
    Circle,
    Cylinder,
    GridLocations,
    Mode,
    Rectangle,
    export_stl,
    extrude,
)

import gridfinity as gf


class ScrewHole(BasePartObject):
    def __init__(self, bridging_support=True, **kwargs):

        with BuildPart() as p:
            Cylinder(
                radius=6.5 / 2,
                height=2.4,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            Cylinder(
                radius=3 / 2,
                height=2.4 + 2.6,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
            if bridging_support:
                with BuildSketch():
                    Circle(radius=6.5 / 2)
                    Rectangle(width=6.5, height=3, mode=Mode.INTERSECT)
                extrude(amount=2.4 + 0.2)

        assert p.part is not None
        super().__init__(part=p.part, **kwargs)


if __name__ == "__main__":

    def parse_size(value: str):
        """Parses a size argument in the format [width]x[height]."""
        try:
            w, h = map(int, value.lower().split("x"))
            return w, h
        except ValueError as e:
            raise argparse.ArgumentTypeError(
                f"Invalid format: '{value}'.Expected format: WxH (e.g., 2x3)"
            ) from e

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--grid",
        type=parse_size,
        default=(1, 1),
        help="Grid size in format WxH (e.g., 2x3)",
    )
    parser.add_argument(
        "--bridging-support",
        action="store_true",
        help="Add stepped support geometry for bridging the screw holes across two layers.",
    )
    parser.add_argument(
        "--grid-cell-size",
        type=parse_size,
        default=(42, 42),
        help="Size of grid cells in format WxH (e.g., 42x42 for standard gridfinity cells)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
    )

    args = parser.parse_args()

    grid = gf.Grid.filled(
        args.grid[0], args.grid[1], cell_size=args.grid_cell_size
    )

    with (
        BuildPart() as p,
        gf.utils.IrregularGridLocations(grid),
        GridLocations(
            args.grid_cell_size[0] - 8 * 2,
            args.grid_cell_size[1] - 8 * 2,
            2,
            2,
        ),
    ):
        ScrewHole(bridging_support=args.bridging_support)

    holes_name = "screw-holes"
    if args.grid_cell_size[0] != 42 or args.grid_cell_size[1] != 42:
        baseplate_name = f"custom-{args.grid_cell_size[0]}x{args.grid_cell_size[1]}-screw-holes"

    filename = f"{holes_name}_{args.grid[0]}x{args.grid[1]}"

    assert p.part is not None

    if args.preview:
        from ocp_vscode import (
            show,
        )

        print(
            f"Showing preview for {filename}. Call without --preview to export."
        )
        show(p)
    else:
        export_stl(p.part, f"{filename}.stl")
