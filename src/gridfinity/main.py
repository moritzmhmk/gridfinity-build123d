import typing

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

from .spec import DEFAULT, GridSpec
from .types import Grid
from .utils import IrregularGridLocations, faces_xy


class Bin(BasePartObject):
    """A complete Gridfinity bin: base, body, compartment and stacking lip.

    Args:
        grid: Rows of booleans describing which cells are occupied.
        height: Overall height of the bin in mm, base included.
        compartment: Part to subtract from the body, positioned with its top
            at the top of the bin. ``"default"`` builds a plain
            :class:`Compartment` one ``spec.unit`` below the top, ``None``
            leaves the bin solid.
        stacking_lip: Lip added at the top of the bin. ``"default"`` builds a
            :class:`StackingLip` with support, ``None`` omits it.
        spec: Grid pitch and height unit. Defaults to standard Gridfinity.
    """

    def __init__(
        self,
        grid: Grid,
        height: float,
        compartment: (typing.Literal["default"] | Part | None) = "default",
        stacking_lip: (typing.Literal["default"] | Part | None) = "default",
        spec: GridSpec = DEFAULT,
        **kwargs,
    ):
        with BuildPart() as p:
            # Base
            base = Base(grid=grid, spec=spec)
            base_height = base.bounding_box().size.Z

            # Body
            with Locations((0, 0, base_height)):
                extrude(
                    GridSketch(grid, inset=0.25, spec=spec),
                    amount=height - base_height,
                )

            if compartment is not None:
                if isinstance(compartment, str):
                    compartment = Compartment(
                        grid, height - spec.unit, spec=spec
                    )
                with Locations((0, 0, height)):
                    add(compartment, mode=Mode.SUBTRACT)

            if stacking_lip is not None:
                if isinstance(stacking_lip, str):
                    stacking_lip = StackingLip(
                        grid=grid, with_support=True, spec=spec
                    )
                with Locations((0, 0, height)):
                    add(stacking_lip)

        assert p.part is not None
        super().__init__(part=p.part, **kwargs)


class Base(BasePartObject):
    """The stackable feet of a bin, one per occupied grid cell.

    Args:
        grid: Rows of booleans describing which cells are occupied.
        spec: Grid pitch and height unit. Defaults to standard Gridfinity.
    """

    def __init__(self, grid: Grid, spec: GridSpec = DEFAULT, **kwargs):
        d = [2.15, 1.8, 0.8]
        with BuildPart() as base:
            with BuildSketch(Plane.XY.offset(sum(d))):
                r = Rectangle(spec.size - 0.5, spec.size - 0.5)
                fillet(r.vertices(), radius=3.75)

            extrude(amount=-d[0], taper=45)
            extrude(faces_xy(base)[0], amount=d[1])
            extrude(faces_xy(base)[0], amount=d[2], taper=45)

        with BuildPart() as p:
            with IrregularGridLocations(spec.size, spec.size, grid):
                add(base)

        assert p.part is not None
        super().__init__(part=p.part, **kwargs)


class Baseplate(BasePartObject):
    """A plate of sockets that the feet of a bin drop into.

    The socket profile mirrors the bin foot, with a 0.7 mm bottom chamfer
    against the foot's 0.8 mm, which is what provides the fit clearance. The
    plate is 4.65 mm tall regardless of the grid pitch.

    Args:
        grid: Rows of booleans describing which cells are occupied.
        spec: Grid pitch and height unit. Defaults to standard Gridfinity.
    """

    def __init__(self, grid: Grid, spec: GridSpec = DEFAULT, **kwargs):
        d = [2.15, 1.8, 0.7]  # socket profile, top to bottom
        with BuildPart() as socket:
            with BuildSketch(Plane.XY.offset(sum(d))):
                r = Rectangle(spec.size - 0.5, spec.size - 0.5)
                fillet(r.vertices(), radius=3.75)

            extrude(amount=-d[0], taper=45)
            extrude(faces_xy(socket)[0], amount=d[1])
            extrude(faces_xy(socket)[0], amount=d[2], taper=45)

        with BuildPart() as p:
            extrude(GridSketch(grid, spec=spec), amount=sum(d))
            with IrregularGridLocations(spec.size, spec.size, grid):
                add(socket, mode=Mode.SUBTRACT)

        assert p.part is not None
        super().__init__(part=p.part, **kwargs)


class Compartment(BasePartObject):
    """A plain cavity to subtract from a bin body.

    The part is built downwards from the origin, so it is positioned by its
    top face.

    Args:
        grid: Rows of booleans describing which cells are occupied.
        height: Depth of the cavity in mm.
        wall_thickness: Wall left between the cavity and the outside of the
            bin, in mm.
        mode: build123d combination mode.
        spec: Grid pitch and height unit. Defaults to standard Gridfinity.
    """

    def __init__(
        self,
        grid: Grid,
        height: float,
        wall_thickness=1.0,
        mode=Mode.PRIVATE,
        spec: GridSpec = DEFAULT,
        **kwargs,
    ):
        grid_sketch = GridSketch(grid, inset=0.25 + wall_thickness, spec=spec)
        with BuildPart() as p:
            extrude(grid_sketch, amount=-height)
            fillet(faces_xy(p)[0].edges(), radius=1)

        assert p.part is not None
        super().__init__(part=p.part, mode=mode, **kwargs)


class StackingLip(BasePartObject):
    """The lip around the top edge that a bin stacked above locates into.

    Args:
        grid: Rows of booleans describing which cells are occupied.
        with_support: Add printable support material under the lip.
        mode: build123d combination mode.
        spec: Grid pitch and height unit. Defaults to standard Gridfinity.
    """

    def __init__(
        self,
        grid: Grid,
        with_support=False,
        mode=Mode.PRIVATE,
        spec: GridSpec = DEFAULT,
        **kwargs,
    ):
        grid_sketch = GridSketch(grid, inset=0.25, spec=spec)
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
    """The 2D footprint of a grid layout.

    Args:
        grid: Rows of booleans describing which cells are occupied.
        inset: Amount to shrink the outline by, in mm.
        with_fillet: Round the outline corners.
        spec: Grid pitch and height unit. Defaults to standard Gridfinity.
    """

    def __init__(
        self,
        grid: Grid,
        inset: float = 0,
        with_fillet=True,
        spec: GridSpec = DEFAULT,
        **kwargs,
    ):
        with BuildSketch(Plane.XY) as s:
            with IrregularGridLocations(spec.size, spec.size, grid):
                Rectangle(spec.size, spec.size)
            offset(amount=-inset, kind=Kind.INTERSECTION)
            if with_fillet:
                fillet(s.vertices(), radius=4 - inset)

        # the fillet operation above always creates a face with a
        # single Wire even when holes are present, let's fix that:
        wires = Wire.combine(s.edges())
        f = Face(outer_wire=wires[0], inner_wires=wires[1:])

        super().__init__(f, **kwargs)
