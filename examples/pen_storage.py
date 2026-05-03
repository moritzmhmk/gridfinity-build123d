from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    GridLocations,
    Location,
    Locations,
    Mode,
    Plane,
    Rectangle,
    extrude,
    fillet,
)
from ocp_vscode import show

import gridfinity as gf
from gridfinity.main import GridSketch

grid = [[True] * 2] * 3
height = 4 * 7

grid_sketch = GridSketch(grid, inset=1.25)
with BuildPart() as p:
    size = grid_sketch.bounding_box().size
    h = height - 7
    extrude(grid_sketch, amount=-h)

    with BuildSketch(Plane.XZ.move(Location((0, size.Y / 2, -h)))) as s:
        div = 5
        d = size.X / div
        print(d)
        with GridLocations(d, 0, div, 1):
            Circle(radius=d / 2, align=(Align.CENTER, Align.MIN))
        with Locations((0, d / 2)):
            Rectangle(width=size.X, height=h, align=(Align.CENTER, Align.MIN))
        vertices = s.vertices().group_by(Axis.Y)[0].sort_by(Axis.X)[1:-1]
    extrude(amount=size.Y, mode=Mode.INTERSECT)
    fillet(p.edges().filter_by(Axis.Y), 2)
    fillet(p.edges().filter_by(Axis.Y, reverse=True), 1)
bin = gf.Bin(grid=grid, height=height, compartment=p.part)

show(bin)
