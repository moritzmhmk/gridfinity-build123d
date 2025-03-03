from build123d import (
    Align,
    Axis,
    BasePartObject,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Edge,
    GridLocations,
    Locations,
    Mode,
    Plane,
    Polygon,
    Rectangle,
    extrude,
    fillet,
)


from .main import Grid, GridSketch


class SubdividedCompartment(BasePartObject):
    def __init__(self,
                 grid: Grid,
                 height: float,
                 div_x: int,
                 div_y: int,
                 div_cutout: float = 0,
                 with_label=False,
                 with_scoop=False,
                 wall_thickness=1.0,
                 mode=Mode.PRIVATE,
                 **kwargs):
        grid_sketch = GridSketch(
            grid,
            inset=0.25+wall_thickness,
            with_fillet=False
        )
        size = grid_sketch.bounding_box().size

        with BuildPart() as p:
            extrude(grid_sketch, amount=-height)

            with BuildPart(mode=Mode.SUBTRACT) as p2:
                _align = (Align.CENTER, Align.CENTER, Align.MAX)
                cut_edges: list[Edge] = []
                grid_w = size.X/div_x
                grid_h = size.Y/div_y
                if div_y > 1:
                    with GridLocations(grid_w, grid_h, div_x, div_y-1):
                        Box(grid_w, 1, height, align=_align)
                        cut_size = min(div_cutout, grid_w-10)
                        if cut_size > 0:
                            cut = Box(
                                length=cut_size,
                                width=1,
                                height=height-5,
                                align=_align,
                                mode=Mode.SUBTRACT
                            )
                            cut_edges += cut.edges().filter_by(Axis.Y)
                if div_x > 1:
                    with GridLocations(grid_w, grid_h, div_x-1, div_y):
                        Box(1, grid_h, height, align=_align)
                        cut_size = min(div_cutout, grid_h-10)
                        if cut_size > 0:
                            cut = Box(
                                length=1,
                                width=cut_size,
                                height=height-5,
                                align=_align,
                                mode=Mode.SUBTRACT
                            )
                            cut_edges += cut.edges().filter_by(Axis.X)

                if len(cut_edges):
                    fillet(cut_edges, radius=2)
                if div_x > 1 or div_y > 1:
                    _ez = p2.edges().group_by(Axis.Z)[-1]
                    _ef = [e for e in _ez if e.length > 1]
                    fillet(_ef, radius=0.45)

                if with_label:
                    # Label Cutout
                    with (BuildSketch(Plane.XZ.offset(-size.Y/2)) as s,
                          Locations((size.X/2, 0, 0))):
                        _w = 14
                        # 1:0.7 equals about 55 degrees overhang
                        _h = min(_w*0.7, height-2.2)
                        Polygon((0, 0), (-_w, 0), (0, -_h), align=None)
                        fillet(s.vertices().sort_by(Axis.X)[0], radius=0.6)
                    extrude(amount=size.Y)

                # Scoop Cutout
                if with_scoop:
                    # Shorten by lip_comp to compensate for the stacking lip
                    _l_cmp = 1.8+0.8-wall_thickness
                    with (BuildSketch(Plane.XZ.offset(-size.Y/2)),
                          Locations((-size.X/2+_l_cmp, -height, 0))):
                        Rectangle(_l_cmp, height, align=(Align.MAX, Align.MIN))
                        # Create Scoop with radius r
                        r = 7
                        align = (Align.MIN, Align.MIN)
                        Rectangle(r, r, align=align)
                        Circle(r, align=align, mode=Mode.SUBTRACT)
                    extrude(amount=size.Y)

            # fillet all z edges and all of bottom faces
            z_edges = p.edges().filter_by(Axis.Z)
            btm_faces = p.faces().group_by(Axis.Z)[0]
            btm_edges = [e for btm_face in btm_faces for e in btm_face.edges()]
            fillet(btm_edges + z_edges, radius=4-0.25-wall_thickness)

        assert p.part is not None
        super().__init__(part=p.part, mode=mode, **kwargs)
