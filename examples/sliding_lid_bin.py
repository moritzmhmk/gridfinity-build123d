from build123d import (
    Align,
    Axis,
    BasePartObject,
    Box,
    BuildPart,
    BuildSketch,
    Cylinder,
    Kind,
    Location,
    Locations,
    Mode,
    Plane,
    Rectangle,
    add,
    chamfer,
    export_stl,
    extrude,
    offset
)
from gridfinity import Bin
from gridfinity.main import GridSketch, StackingLip
from gridfinity.extra import SubdividedCompartment
from gridfinity.types import Grid


class InnerLid(BasePartObject):
    def __init__(self,
                 grid: Grid,
                 thickness,
                 inset=1.0,
                 **kwargs):
        lip_d0, lip_d2 = 1.9, 0.7  # stacking lip constants
        working_plane = Plane.XY.offset(lip_d2)
        click_lock = 0.3

        with BuildPart() as p:
            with BuildSketch(working_plane):
                GridSketch(grid, inset=0.25+inset)
            extrude(amount=-lip_d2-thickness)
            top_edges = p.edges().filter_by(Plane.XY).group_by(Axis.Z)[-1]
            chamfer(top_edges, length=lip_d0-inset)

            with BuildPart(working_plane, mode=Mode.SUBTRACT):
                assert p.part is not None
                size = p.part.bounding_box().size
                _x = -size.X/2+7-inset
                _y = size.Y/2
                with Locations((_x,  _y), (_x, -_y)):
                    Cylinder(
                        radius=click_lock,
                        height=lip_d2+thickness,
                        align=(Align.CENTER, Align.CENTER, Align.MAX)
                    )

        assert p.part is not None
        super().__init__(part=p.part, **kwargs)


class Lid(BasePartObject):
    def __init__(self,
                 grid: Grid,
                 thickness,
                 inset=1.0,
                 tolerance=0.1,
                 **kwargs):
        inner_lid = InnerLid(grid, thickness, inset)
        stacking_lip = StackingLip(grid, with_support=True)

        with BuildPart() as p:
            with BuildPart():
                add(stacking_lip)
                with BuildSketch():
                    GridSketch(grid, inset=0.25+inset)
                extrude(amount=-thickness)

                with BuildPart(mode=Mode.SUBTRACT):
                    with BuildSketch(Plane.XY.offset(-thickness)):
                        size = stacking_lip.bounding_box().size
                        with Locations((size.X/2-3.75+tolerance, 0)):
                            Rectangle(size.X, size.Y,
                                      align=(Align.MAX, Align.CENTER))
                    extrude(amount=20)
                    offset(inner_lid, amount=-tolerance,
                           kind=Kind.ARC, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(-thickness+tolerance)):
                GridSketch(grid, inset=0.25)
            extrude(amount=-10, mode=Mode.SUBTRACT)

        assert p.part is not None
        super().__init__(part=p.part, **kwargs)


class BinSubstraction(BasePartObject):
    def __init__(self,
                 grid: Grid,
                 bin_height,
                 thickness,
                 inset=1.0,
                 mode=Mode.SUBTRACT,
                 **kwargs):

        grid_sketch = GridSketch(grid, inset=0.25)
        size = grid_sketch.bounding_box().size
        with BuildPart(Plane.XY.offset(bin_height)) as p:
            with Locations((size.X/2, 0, -thickness)):
                Box(3.75, size.Y, 20,
                    align=(Align.MAX, Align.CENTER, Align.MIN))
            InnerLid(grid, thickness, inset)

        assert p.part is not None
        super().__init__(part=p.part, mode=mode, **kwargs)


if __name__ == "__main__":
    import argparse

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
                        help="Bin grid size in format WxH (e.g., 2x3)")
    parser.add_argument("--height", type=float, default=3,
                        help="Bin height in units (i.e. 2 = 14 mm).")
    parser.add_argument("--div", type=parse_size, default=(1, 1),
                        help="Compartment division in format XxY (e.g., 2x2)")
    parser.add_argument("--scoops", nargs="*",
                        choices=["front", "back", "left", "right"],
                        help=("Specify which sides should have scoops. "
                              "Options: front, back, left, right"))

    args = parser.parse_args()

    lid_thickness = 0.6 + 0.1*2
    with BuildPart() as bin:
        grid = [[True]*args.grid[0]]*args.grid[1]
        height = args.height * 7
        Bin(
            grid,
            height=height,
            compartment=SubdividedCompartment(
                grid,
                height-7-lid_thickness,
                div_x=args.div[0],
                div_y=args.div[1],
                with_label=False,
                scoops=args.scoops
            ).moved(Location((0, 0, -lid_thickness)))
        )

        BinSubstraction(grid, bin_height=height, thickness=lid_thickness)

    assert bin.part is not None
    export_stl(
        bin.part,
        "sliding-lid-bin_"
        f"{args.grid[0]}x{args.grid[1]}-h{args.height}-"
        f"div{args.div[0]}x{args.div[1]}.stl"
    )

    lid = Lid(grid, lid_thickness)
    export_stl(
        lid,
        "sliding-lid-cover_"
        f"{args.grid[0]}x{args.grid[1]}.stl")

    # from ocp_vscode import show
    # show(bin.part, lid.moved(Location((0, 0, height))))
