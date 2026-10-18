# Scripts

Command-line scripts to generate customizable Gridfinity bins and baseplates.

## Bin

Generate bins with configurable dimensions, compartments, wall cutouts, labels, and scoops.

```bash
uv run -m scripts.bin --grid 3x1 --height 3 --div 4x1 --scoops front --label
```

Run `uv run -m scripts.bin --help` to see all available options.

## Baseplate

Generate baseplates with configurable dimensions, edge padding, and corner rounding.

```bash
uv run -m scripts.baseplate --grid 2x3 --padding-left 4.2 --rounded-corners front-left back-left
```

Run `uv run -m scripts.baseplate --help` to see all available options.
