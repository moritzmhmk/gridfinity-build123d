from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Cylinder,
    Location,
    Mode,
    Plane,
    Polygon,
    add,
    export_stl,
    extrude,
    fillet,
    revolve,
)
from ocp_vscode import show

import gridfinity as gf

grid = [[True] * 1] * 3
height = 3 * 7


with BuildPart() as pencil:
    with BuildSketch() as s:
        Polygon(
            (0, 0),
            (18, 0),
            (18, 12),
            (18 + 1, 13),
            (18 + 1, 64),
            (18, 65),
            (18, 97),
            (18 - 3, 103),
            (18 - 3, 106),
            (18 - 3, 115),
            (0, 115),
        )
        _vs = s.vertices().group_by(Axis.Y)
        fillet(_vs[0], 1)
        fillet(_vs[-1], 1)
    extrude(amount=-15)
    _es = pencil.edges().group_by(Axis.Z)
    fillet(_es[0], 1)

with BuildPart(Plane.XY) as tip:
    with BuildSketch() as s2:
        Polygon(
            (0, 0),
            (6.5 / 2, 0),
            (6.5 / 2, 35),
            (12 / 2, 35),
            (12 / 2, 38),
            (6.5 / 2, 41),
            (6.5 / 2, 90 + 15),
            (0, 90 + 15),
            align=None,
        )
        _es = s2.edges().sort_by(Axis.Y)
        fillet(_es[-1].vertices().sort_by(Axis.X)[1], 1)
    r = revolve(s2.faces(), axis=Axis.Y, revolution_arc=180, mode=Mode.PRIVATE)
    add(r.moved(Location((0, 0, -13 / 2))))
    extrude(tip.faces().sort_by(Axis.Z)[-1], 13 / 2)

    Cylinder(
        radius=17 / 2, height=15, align=(Align.CENTER, Align.CENTER, Align.MAX)
    )

    # fillet bottom of cylinder
    fillet(tip.faces().sort_by(Axis.Z)[0].edges(), 1)
    # fillet connection from cylinder to tip cutout
    fillet(tip.edges().filter_by(Axis.Z).group_by(Axis.Y)[1], 3)


with BuildPart() as compartment:
    add(pencil.part.moved(Location((-7.75, 0, 0))))
    add(tip.part.moved(Location((8.75, 50, 0), 180)))


with BuildPart() as bin:
    gf.Bin(grid=grid, height=height, compartment=compartment.part)

    s_x = 42 * 1 - 8
    s_y = 42 * 3 - 8

    compartment_edges = (
        bin.edges()
        .filter_by_position(Axis.Z, 7, 100)
        .filter_by_position(Axis.X, -s_x / 2, s_x / 2)
        .filter_by_position(Axis.Y, -s_y / 2, s_y / 2)
    )

    fillet(compartment_edges.filter_by(Plane.XY).group_by(Axis.Z)[-1], 0.75)

show(bin)
export_stl(bin.part, "pinecil_soldering_iron_storage.stl")
