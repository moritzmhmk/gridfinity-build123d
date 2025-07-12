from build123d import (Align, Axis, Box, BuildPart, BuildSketch, Cone,
                       Cylinder, Location, Locations, Mode, Plane, Polygon,
                       Rectangle, add, export_stl, extrude, fillet, revolve)
from ocp_vscode import show

import gridfinity as gf
from gridfinity.main import GridSketch

grid = [[True]*1]*4
height = 4*7

with BuildPart(Plane.XZ) as ss03:
    align = (Align.CENTER, Align.CENTER, Align.MIN)

    sizes = [
        (18.5, 18.5, 8),
        (5.5, 5.5, 37),
        (20.5, 20.5, 88),
        (20.5, 9.5, 8),
        (9.5, 9.5, 16),
    ]

    position = 0.0
    for size in sizes:
        with Locations((0, 0, position)):
            if size[0] == size[1]:
                Cylinder(size[0]/2, height=size[2], align=align)
            else:
                Cone(size[0]/2, size[1]/2, height=size[2], align=align)
        position += size[2]

    with BuildSketch() as grip_hole, Locations((0, -7.5-38/2, 0)):
        Rectangle(30, 20)
        fillet(grip_hole.vertices(), 5)
    extrude(amount=21/2, both=True)

    with BuildSketch() as tube_holes:
        y_loc = -7.5-38-88/2
        x_loc = 15
        with Locations((x_loc, y_loc, 0), (-x_loc, y_loc, 0)):
            Rectangle(5, 60)
        with Locations((0, y_loc, 0)):
            Rectangle(30, 15)
        fillet(tube_holes.vertices(), 1)
    extrude(amount=8, both=True)

    fillet(ss03.edges(), 1)

show(ss03)
assert ss03.part

with BuildPart(Plane.XY.offset(-21/2)) as compartment:
    extrude(GridSketch(grid, inset=1.25), -21/2)
    with Locations((0, ss03.part.bounding_box().size.Y/2, 0)):
        add(ss03)
    _es = compartment.faces().filter_by(Plane.XY).sort_by(Axis.Z)[3].edges()
    fillet(_es, 0.8)

show(compartment)

bin = gf.Bin(grid=grid, height=height, compartment=compartment.part)

show(bin)
export_stl(bin, "engineer_ss_03_storage.stl")
