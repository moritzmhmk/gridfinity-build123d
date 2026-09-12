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
        "--grid-size",
        type=float,
        default=42.0,
        help="Grid pitch in mm (default 42, the Gridfinity standard).",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
    )

    args = parser.parse_args()

    # A rectangle here, but any grid layout works: rows may be ragged and
    # False leaves a hole, e.g.
    # grid = [[True], [True], [True] * 3, [True] * 4]
    grid = [[True] * args.grid[0]] * args.grid[1]

    spec = gf.GridSpec(size=args.grid_size)

    baseplate = gf.Baseplate(grid=grid, spec=spec)

    if args.preview:
        from ocp_vscode import (
            show,
        )

        show(baseplate)
        exit(0)

    export_stl(
        baseplate,
        "baseplate"
        f"_{args.grid[0]}x{args.grid[1]}"
        f"{f'_{args.grid_size:g}mm' if args.grid_size != 42.0 else ''}"
        ".stl",
    )
