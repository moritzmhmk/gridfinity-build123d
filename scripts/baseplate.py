import argparse

from build123d import (
    Axis,
    BuildPart,
    export_stl,
    extrude,
    fillet,
)

import gridfinity as gf

if __name__ == "__main__":

    def parse_size(
        value: str,
    ):
        """Parses a size argument in the format [width]x[height]."""
        try:
            w, h = map(
                int,
                value.lower().split("x"),
            )
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
        help="Baseplate grid size in format WxH (e.g., 2x3)",
    )
    for side in ("left", "right", "front", "back"):
        parser.add_argument(
            f"--padding-{side}",
            type=float,
            help=(f"Add padding to the {side} edge."),
        )
    parser.add_argument(
        "--rounded-corners",
        nargs="+",
        choices=["front-left", "front-right", "back-left", "back-right"],
        default=["front-left", "front-right", "back-left", "back-right"],
        help="Corners to fillet (default: all).",
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

    with BuildPart() as baseplate:
        gf.Baseplate(grid=grid, rounded_corners=False)
        for side in ("left", "right", "front", "back"):
            amount = getattr(args, f"padding_{side}")
            if amount is None or amount == 0:
                continue
            axis = Axis.X if side == "left" or side == "right" else Axis.Y
            index = 0 if side == "front" or side == "left" else -1
            face = baseplate.faces().sort_by(axis)[index]
            extrude(face, amount)

        edges = baseplate.edges().filter_by(Axis.Z)
        bbox = baseplate.part.bounding_box()
        for corner in args.rounded_corners or []:
            x = bbox.min.X if "left" in corner else bbox.max.X
            y = bbox.min.Y if "front" in corner else bbox.max.Y
            edge = min(
                edges,
                key=lambda e: (
                    (e.center().X - x) ** 2 + (e.center().Y - y) ** 2
                ),
            )
            fillet(edge, radius=4)

    baseplate_name = "baseplate"
    if args.grid_cell_size[0] != 42 or args.grid_cell_size[1] != 42:
        baseplate_name = f"custom-{args.grid_cell_size[0]}x{args.grid_cell_size[1]}-baseplate"

    padding_str = ""
    for side in ("left", "right", "front", "back"):
        padding = getattr(args, f"padding_{side}")
        if padding:
            padding_str += f"_pad-{side}-{padding:g}"

    corners_str = ""
    if set(args.rounded_corners) != {
        "front-left",
        "front-right",
        "back-left",
        "back-right",
    }:
        corners = "-".join(
            corner.replace("-", "") for corner in sorted(args.rounded_corners)
        )
        corners_str = f"_corners-{corners}"

    filename = (
        f"{baseplate_name}"
        f"_{args.grid[0]}x{args.grid[1]}"
        f"{padding_str}"
        f"{corners_str}"
    )
    if args.preview:
        from ocp_vscode import (
            show,
        )

        print(
            f"Showing preview for {filename}. Call without --preview to export."
        )
        show(baseplate)
    else:
        export_stl(baseplate.part, f"{filename}.stl")
