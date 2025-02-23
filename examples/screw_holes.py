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
    extrude
)
import gridfinity as gf


class ScrewHole(BasePartObject):
    def __init__(self, printable=True, **kwargs):

        with BuildPart() as p:
            Cylinder(radius=6.5/2, height=2.4,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
            Cylinder(radius=3/2, height=2.4+2.6,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
            if printable:
                with BuildSketch():
                    Circle(radius=6.5/2)
                    Rectangle(width=6.5, height=3, mode=Mode.INTERSECT)
                extrude(amount=2.4+0.2)

        assert p.part is not None
        super().__init__(part=p.part, **kwargs)


if __name__ == "__main__":
    def parse_size(value: str):
        """Parses a size argument in the format [width]x[height]."""
        try:
            w, h = map(int, value.lower().split('x'))
            return w, h
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"Invalid format: '{value}'."
                "Expected format: WxH (e.g., 2x3)"
            )

    parser = argparse.ArgumentParser()
    parser.add_argument("--grid", type=parse_size, default=(1, 1),
                        help="Grid size in format WxH (e.g., 2x3)")

    args = parser.parse_args()

    grid = [[True]*args.grid[0]]*args.grid[1]

    with BuildPart() as p:
        with gf.utils.IrregularGridLocations(42, 42, grid):
            with GridLocations(26, 26, 2, 2):
                ScrewHole()

    assert p.part is not None

    export_stl(p.part, f"screw-holes_{args.grid[0]}x{args.grid[1]}.stl")

    # from ocp_vscode import show
    # show(p)
