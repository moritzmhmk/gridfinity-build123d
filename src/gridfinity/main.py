from build123d import (
    Axis,
    BasePartObject,
    BaseSketchObject,
    BuildPart,
    BuildSketch,
    Face,
    Kind,
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
from .utils import faces_xy, IrregularGridLocations


class Bin(BasePartObject):
    def __init__(self,
                 grid: Grid,
                 height: float,
                 cut_compartment: Part | None = None,
                 with_stacking_lip=True,
                 **kwargs):

        with BuildPart() as p:
            # Base
            base = Base(grid=grid)
            base_height = base.bounding_box().size.Z

            # Body
            with Locations((0, 0, base_height)):
                extrude(GridSketch(grid), amount=height - base_height)
            if cut_compartment:
                with Locations((0, 0, height)):
                    add(cut_compartment, mode=Mode.SUBTRACT)

            if with_stacking_lip:
                # TODO: Location is applied twice to Lip!? Divide by two...
                with Locations((0, 0, height/2)):
                    StackingLip(grid=grid, with_support=False)

        assert p.part is not None
        super().__init__(part=p.part, **kwargs)


class Base(BasePartObject):
    def __init__(self, grid: Grid, **kwargs):
        d = [2.15, 1.8, 0.8]
        with BuildPart() as base:
            with BuildSketch(Plane.XY.offset(sum(d))):
                r = Rectangle(42-0.5, 42-0.5)
                fillet(r.vertices(), radius=3.75)

            extrude(amount=-d[0], taper=45)
            extrude(faces_xy(base)[0], amount=d[1])
            extrude(faces_xy(base)[0], amount=d[2], taper=45)

        with BuildPart() as p:
            with IrregularGridLocations(42, 42, grid):
                add(base)

        assert p.part is not None
        super().__init__(part=p.part, **kwargs)


class StackingLip(BasePartObject):
    def __init__(self,
                 grid: Grid,
                 with_support=False,
                 **kwargs):
        grid_sketch = GridSketch(grid)
        d0, d1, d2 = 1.9, 1.8, 0.7  # lip dimensions
        d3, d4 = 1.2, d0 + d2  # support dimension

        with BuildPart() as n:
            extrude(grid_sketch, amount=-d0, taper=45)
            extrude(faces_xy(n)[0], amount=d1)
            extrude(faces_xy(n)[0], amount=d2, taper=45)
            extrude(faces_xy(n)[0], amount=d3)
            extrude(faces_xy(n)[0], amount=d4, taper=-45)

        with BuildPart() as p:
            extrude(grid_sketch, amount=d0+d1+d2)
            if with_support:
                extrude(grid_sketch, amount=-d3-d4)
            with Locations((0, 0, d0+d1+d2)):
                add(n, mode=Mode.SUBTRACT)
            fillet(p.edges().group_by(Axis.Z)[-1], radius=0.6)

        assert type(p.part) is Part
        super().__init__(part=p.part, **kwargs)


class GridSketch(BaseSketchObject):
    def __init__(self,
                 grid:  Grid,
                 inset: float = 0.25,
                 with_fillet=True,
                 **kwargs):
        with BuildSketch(Plane.XY) as s:
            with IrregularGridLocations(42, 42, grid):
                Rectangle(42, 42)
            offset(amount=-inset, kind=Kind.INTERSECTION)
            if with_fillet:
                fillet(s.vertices(), radius=4-inset)

        # the fillet operation above always creates a face with a
        # single Wire even when holes are present, let's fix that:
        wires = Wire.combine(s.edges())
        f = Face(outer_wire=wires[0], inner_wires=wires[1:])

        super().__init__(f, **kwargs)
