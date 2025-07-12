from build123d import (Align, Axis, Box, BuildPart, BuildSketch, Cone,
                       Cylinder, Location, Locations, Mode, Plane, Polygon,
                       Rectangle, add, export_stl, extrude, fillet, revolve)
from ocp_vscode import show

import gridfinity as gf
from gridfinity.main import GridSketch

grid = [[True]*1]*3
height = 3*7

with BuildPart(Plane.XZ) as tips:
    align = (Align.CENTER, Align.CENTER, Align.MIN)

    d1 = 6
    d2 = 11.75
    space = 0  # (42-1.25-1.5*d1-2.5*d2)/5

    d1_length = 95
    d2_length = 6
    d2_offset = 15
    with Locations([((x-1.5)*(d1+d2+space)/2, 0, 0) for x in range(4)]):
        Cylinder(d1/2, d1_length)
    with Locations([((x-1.5)*(d1+d2+space)/2, 0, (1-2*(x % 2))*d2_offset) for x in range(4)]):
        Cylinder(d2/2+0.05, d2_length)
    with BuildSketch() as grip_hole:
        hole_length = 20
        hole_width = 38
        hole_offset = d1_length/2+hole_length/2-5
        with Locations((0, hole_offset, 0), (0, -hole_offset, 0)):
            Rectangle(hole_width, hole_length)
            fillet(grip_hole.vertices(), 1)
    # extrude(amount=7, both=True)

    fillet(tips.edges(), 1)

show(tips)
assert tips.part

with BuildPart(Plane.XY.offset(-(height-7)/2)) as compartment:
    extrude(GridSketch(grid, inset=1.25), -(height-7))
    Box(42, 90, (height-7)/2, align=(Align.CENTER,
        Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
    fillet(compartment.edges().group_by(Axis.Z)[0:-1], 1)
    add(tips)
    _es = compartment.faces().filter_by(Plane.XY).group_by(Axis.Z)[1].edges()\
        .filter_by_position(Axis.X, -15, 15)\
        .filter_by_position(Axis.Y, -20, 20)
    fillet(_es, 0.39)

show(compartment, _es)

bin = gf.Bin(grid=grid, height=height, compartment=compartment.part)

show(bin)
export_stl(bin, "pinecil_tip_storage.stl")
