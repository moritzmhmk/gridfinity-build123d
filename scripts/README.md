# Scripts

Command-line scripts to generate customizable Gridfinity bins and baseplates.

## Bin

Generate bins with configurable dimensions, compartments, wall cutouts, labels, and scoops.

```bash
uv run -m scripts.bin --grid 3x1 --height 3 --div 4x1 --scoops front --label
```

Run `uv run -m scripts.bin --help` for all available options.

## Baseplate

Generate baseplates with configurable dimensions, edge padding, and corner rounding.

```bash
uv run -m scripts.baseplate --grid 2x3 --padding-left 4.2 --rounded-corners front-left back-left
```

Run `uv run -m scripts.baseplate --help` for all available options.

## Screw holes

Generate an STL negative volume for creating screw holes in the bottom of Gridfinity bins using a slicer's negative-volume feature. Optional bridging support adds stepped geometry to improve printability.

```bash
uv run -m scripts.screw_holes --grid 2x3 --bridging-support
```

Run `uv run -m scripts.screw_holes --help` for all available options.
