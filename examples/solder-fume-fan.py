# Note: Run as "python -m examples.solder-fume-fan"
from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    Cylinder,
    GridLocations,
    Location,
    Locations,
    Mode,
    Plane,
    Rectangle,
    add,
    export_stl,
    extrude,
    fillet,
)
from ocp_vscode import show

from examples.sliding_lid_bin import BinSubstraction, Lid
from gridfinity import Bin
from gridfinity.main import GridSketch

with BuildPart() as funnel:
    with BuildSketch():
        Circle(radius=39 / 2)
    extrude(amount=-14)
    extrude(funnel.faces().sort_by(Axis.Z)[0], amount=2.5, taper=45)
    extrude(funnel.faces().sort_by(Axis.Z)[0], amount=2.5)


with BuildPart() as usb_pd:
    with BuildSketch(Plane.ZY) as port:
        Rectangle(9.3, 3.6, align=(Align.CENTER, Align.CENTER))
        fillet(port.vertices(), 1)
    extrude(amount=7.5)
    with BuildSketch(Plane.ZY.offset(1)) as pcb:
        Rectangle(11.5, 8, align=(Align.CENTER, Align.CENTER))
    extrude(amount=20)

show(usb_pd)

with BuildPart() as compartment:
    grid_sketch = GridSketch([[True]], inset=0.25 + 1.0)
    extrude(grid_sketch, -12)

    with BuildSketch(Plane.XY.offset(-12)) as grill_sketch:
        # Center hole
        Circle(39 / 2)
        Circle(10 / 2, mode=Mode.SUBTRACT)
        Rectangle(1, 39, rotation=0, mode=Mode.SUBTRACT)
        Rectangle(1, 39, rotation=60, mode=Mode.SUBTRACT)
        Rectangle(1, 39, rotation=120, mode=Mode.SUBTRACT)
        fillet(grill_sketch.vertices(), 1)

        # Mounting holes
        with GridLocations(32, 32, 2, 2):
            Circle(3.5 / 2)
    extrude(amount=-1)

    with Locations((0, 0, -13)):
        grid_sketch = GridSketch([[True]])
        extrude(grid_sketch, -10)

    with Locations((0, 0, -23)):
        # Self tap holes for M3
        align = (Align.CENTER, Align.CENTER, Align.MAX)
        with GridLocations(32, 32, 2, 2):
            Cylinder(2.7 / 2, 14, align=align)

    # Bottom funnel
    with Locations((0, 0, -23)):
        add(funnel)

    with Locations((42 / 2, -42 / 2 + 8, -6 * 7 + 10.75)):
        add(usb_pd)

show(compartment)

lid_thickness = 0.6 + 0.1 * 2
with BuildPart() as bin:
    grid = [[True]]
    height = 6 * 7
    Bin(grid, height=height, compartment=compartment.part)
    BinSubstraction(grid, bin_height=height, thickness=lid_thickness)

show(bin)

with BuildPart() as lid:
    Lid(grid, lid_thickness)
    with GridLocations(5, 5, 7, 7):
        Cylinder(1.5, 20, mode=Mode.SUBTRACT)
    with GridLocations(5, 5, 6, 6):
        Cylinder(1.5, 20, mode=Mode.SUBTRACT)

show(lid)

show(bin.part, lid.part.moved(Location((0, 0, height))))

export_stl(lid.part, "solder-fume-lid.stl")
export_stl(bin.part, "solder-fume-fan_bin.stl")
