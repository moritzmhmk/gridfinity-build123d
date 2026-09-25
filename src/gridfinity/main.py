import typing

from build123d import (
    Axis,
    BasePartObject,
    BaseSketchObject,
    BuildPart,
    BuildSketch,
    Compound,
    Face,
    Kind,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    Rectangle,
    Wire,
    add,
    extrude,
    fillet,
    offset,
)

from .types import Grid
from .utils import IrregularGridLocations, faces_xy


class Bin(BasePartObject):
    def __init__(
        self,
        grid: Grid,
        height: float,
        compartment: (typing.Literal["default"] | Part | None) = "default",
        stacking_lip: (typing.Literal["default"] | Part | None) = "default",
        **kwargs,
    ):

        body_sketch = GridSketch(grid, inset=0.25)
        with BuildPart() as p:
            # Base
            base = Base(grid=grid)
            base_height = base.bounding_box().size.Z

            # Body
            extrude(
                body_sketch.moved(Location((0, 0, base_height))),
                amount=height - base_height,
            )

            if compartment is not None:
                if isinstance(compartment, str):
                    compartment = Compartment(grid, height - 7)
                with Locations((0, 0, height)):
                    add(compartment, mode=Mode.SUBTRACT)

            if stacking_lip is not None:
                if isinstance(stacking_lip, str):
                    stacking_lip = StackingLip(grid=grid, with_support=True)
                with Locations((0, 0, height)):
                    add(stacking_lip)

        assert p.part is not None
        super().__init__(part=p.part, **kwargs)


class Base(BasePartObject):
    def __init__(self, grid: Grid, **kwargs):
        d = [2.15, 1.8, 0.8]
        grid_sketch = GridSketch(grid, inset=0.25, separate=True)
        with BuildPart() as p:

            extrude(
                grid_sketch.moved(Location((0, 0, sum(d)))),
                amount=-d[0],
                taper=45,
            )
            extrude(
                p.faces().filter_by(Plane.XY).group_by(Axis.Z)[0],
                amount=d[1],
            )
            extrude(
                p.faces().filter_by(Plane.XY).group_by(Axis.Z)[0],
                amount=d[2],
                taper=45,
            )

        assert p.part is not None
        super().__init__(part=p.part, **kwargs)


class Compartment(BasePartObject):
    def __init__(
        self,
        grid: Grid,
        height: float,
        wall_thickness=1.0,
        mode=Mode.PRIVATE,
        **kwargs,
    ):
        grid_sketch = GridSketch(grid, inset=0.25 + wall_thickness)
        with BuildPart() as p:
            extrude(grid_sketch, amount=-height)
            fillet(faces_xy(p)[0].edges(), radius=1)

        assert p.part is not None
        super().__init__(part=p.part, mode=mode, **kwargs)


class StackingLip(BasePartObject):
    def __init__(
        self, grid: Grid, with_support=False, mode=Mode.PRIVATE, **kwargs
    ):
        grid_sketch = GridSketch(grid, inset=0.25)
        d0, d1, d2 = 1.9, 1.8, 0.7  # lip dimensions
        d3, d4 = 1.2, d0 + d2  # support dimension

        with BuildPart() as n:
            extrude(grid_sketch, amount=-d0, taper=45)
            extrude(faces_xy(n)[0], amount=d1)
            extrude(faces_xy(n)[0], amount=d2, taper=45)
            extrude(faces_xy(n)[0], amount=d3)
            extrude(faces_xy(n)[0], amount=d4, taper=-45)

        with BuildPart() as p:
            extrude(grid_sketch, amount=d0 + d1 + d2)
            if with_support:
                extrude(grid_sketch, amount=-d3 - d4)
            with Locations((0, 0, d0 + d1 + d2)):
                add(n, mode=Mode.SUBTRACT)
            fillet(p.edges().group_by(Axis.Z)[-1], radius=0.6)

        assert type(p.part) is Part
        super().__init__(part=p.part, mode=mode, **kwargs)


class GridSketch(BaseSketchObject):
    def __init__(
        self,
        grid: Grid,
        inset: float = 0,
        with_fillet=True,
        separate=False,
        **kwargs,
    ):
        with BuildSketch(Plane.XY) as s:
            with IrregularGridLocations(grid):
                w,h = grid.cell_size
                if separate:
                    Rectangle(w - inset * 2, h - inset * 2)
                else:
                    Rectangle(w, h)

            if not separate:
                offset(amount=-inset, kind=Kind.INTERSECTION)

            if with_fillet:
                fillet(s.vertices(), radius=4 - inset)

        # the fillet operation above always creates a face with a
        # single Wire even when holes are present, let's fix that:
        faces = []
        for f in s.faces():
            wires = Wire.combine(f.edges())
            faces.append(Face(outer_wire=wires[0], inner_wires=wires[1:]))

        super().__init__(Compound(faces), **kwargs)
