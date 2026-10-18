import argparse

from build123d import (
    export_stl,
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

    baseplate = gf.Baseplate(grid=grid)

    baseplate_name = "baseplate"
    if args.grid_cell_size[0] != 42 or args.grid_cell_size[1] != 42:
        baseplate_name = f"custom-{args.grid_cell_size[0]}x{args.grid_cell_size[1]}-baseplate"
    filename = f"{baseplate_name}_{args.grid[0]}x{args.grid[1]}"

    if args.preview:
        from ocp_vscode import (
            show,
        )

        print(
            f"Showing preview for {filename}. Call without --preview to export."
        )
        show(baseplate)
    else:
        export_stl(baseplate, f"{filename}.stl")
