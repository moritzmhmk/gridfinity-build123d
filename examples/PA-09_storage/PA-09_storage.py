import os

from build123d import (Align, Axis, Box, BuildPart, Face, Location, Locations,
                       Mode, Plane, export_stl, extrude, fillet, import_svg)
from ocp_vscode import show

import gridfinity as gf

grid = [[True]*2]*5
height = 3*7

outline_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "PA-09_outline.svg"
)

outline = Face(import_svg(outline_file)[0])

with BuildPart() as compartment:
    extrude(
        outline.moved(Location(-outline.bounding_box().center())),
        amount=14
    )
    with Locations((0, 53, -14)):
        box = Box(
            80, 35, 4.5,
            align=(Align.CENTER, Align.MIN, Align.MIN),
            mode=Mode.SUBTRACT
        )

with BuildPart() as bin:
    gf.Bin(grid=grid, height=height, compartment=compartment.part)

    s_x = 42*2-8
    s_y = 42*5-8

    compartment_edges = bin.edges()\
        .filter_by_position(Axis.Z, 7, 100)\
        .filter_by_position(Axis.X, -s_x/2, s_x/2)\
        .filter_by_position(Axis.Y, -s_y/2, s_y/2)

    fillet(compartment_edges.filter_by(Plane.XY), 1)

show(bin)
export_stl(bin.part, "PA-09_storage.stl")
