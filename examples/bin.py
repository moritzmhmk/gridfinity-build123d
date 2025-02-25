import argparse
from build123d import export_stl
import gridfinity as gf

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
                        help="Bin grid size in format WxH (e.g., 2x3)")
    parser.add_argument("--height", type=int, default=3,
                        help="Bin height in units (i.e. 2 = 14 mm).")
    parser.add_argument("--div", type=parse_size, default=(1, 1),
                        help="Compartment division in format XxY (e.g., 2x2)")
    parser.add_argument("--div-cutout", type=float, default=0,
                        help="Size of cutout in dividing walls (default none)")
    parser.add_argument("--label", action="store_true")
    parser.add_argument("--scoops", nargs="*",
                        choices=["front", "back", "left", "right"],
                        help=("Specify which sides should have scoops. "
                              "Options: front, back, left, right"))

    args = parser.parse_args()

    grid = [[True]*args.grid[0]]*args.grid[1]
    height = args.height * 7

    bin = gf.Bin(
        grid=grid,
        height=height,
        compartment=gf.extra.SubdividedCompartment(
            grid,
            height-7,
            div_x=args.div[0],
            div_y=args.div[1],
            div_cutout=args.div_cutout,
            with_label=args.label,
            scoops=args.scoops
        ))

    scoop_str = "_".join(args.scoops) if args.scoops else None
    export_stl(
        bin,
        "bin"
        f"_{args.grid[0]}x{args.grid[1]}-h{args.height}"
        f"-div{args.div[0]}x{args.div[1]}"
        f"{'_cutout' if args.div_cutout else ''}"
        f"{'-label' if args.label else ''}"
        f"{f'-scoop_{scoop_str}' if scoop_str else ''}"
        ".stl"
    )

    # from ocp_vscode import show
    # show(bin)
