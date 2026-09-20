# Changelog

## v2.0.0 - beta 2
Extend the Grid type to support configurable cell sizes (defaults to 42×42).

Existing grid definitions such as `grid = [[True, ...], ...]` must now be wrapped as `grid = Grid([[True, ...], ...])`. For simple rectangular grids the helper `Grid.filled(width, height)` is available.

Custom cell sizes can be specified with `Grid(cells, cell_size=(21, 21))` or `Grid.filled(width, height, cell_size=(21, 21))` respectively.

## v2.0.0 - beta 1
Change the label and scoop axes to match the Gridfinity convention: left/right now refer to the X axis and front/back to the Y axis. The label is therefore placed at what is now called the "back" instead of the "front".

## v1.1.0 - 2026-05-03
Add option to define scoop radius in `extra.SubdividedCompartment`.

## v1.0.0 - 2025-12-08
Initial **stable** release.

## v0.0.1 - 2025-02-22
Initial release.
