"""Examples for the README.md file."""

import math

import build123d as bd
from build123d import RGB, Compound, Edge, ExportSVG, Location, ShapeList, Text

import gridfinity as gf


def render(part: Compound) -> tuple[ShapeList[Edge], ShapeList[Edge]]:
    view_port_origin = (100, -100, 100)
    return part.project_to_viewport(view_port_origin, look_at=(0, 0, 0))


def _export(visible: ShapeList[Edge],
            hidden: ShapeList[Edge],
            text: ShapeList[Text],
            width: int,
            name: str,
            darkmode=False):
    size = Compound(children=visible + hidden + text).bounding_box().size
    exporter = ExportSVG(scale=width / size.X)
    fg_color = RGB(240, 246, 252) if darkmode is True else RGB(31, 35, 40)
    exporter.add_layer(
        "visible",
        line_color=fg_color
    )
    exporter.add_shape(visible, layer="visible")
    exporter.add_layer(
        "text",
        line_color=None,
        fill_color=fg_color
    )
    exporter.add_shape(text, layer="text")
    exporter.write(f"{name}@{"dark" if darkmode is True else "light"}.svg")


def export(
        visible: ShapeList[Edge] | None,
        hidden: ShapeList[Edge] | None,
        text: ShapeList[Text] | None,
        width: int,
        name: str):
    if visible is None:
        visible = ShapeList[Edge]()
    if hidden is None:
        hidden = ShapeList[Edge]()
    if text is None:
        text = ShapeList[Text]()

    _export(visible, hidden, text, width, name, darkmode=False)
    _export(visible, hidden, text, width, name, darkmode=True)


# Example 1
bin = gf.Bin(grid=[[True]], height=3*7)
export(*render(bin), None, 50, "basic-bin")

# Example 2
grid = [[True]]
compartment = gf.extra.SubdividedCompartment(
    grid,  # use same grid
    height=3*7-7,  # usually height of bin minus 1 unit
    div_x=1,
    div_y=2,
    with_label=True,
    scoops=["back"]
)
bin = gf.Bin(
    grid=grid,
    height=3*7,
    compartment=compartment
)

compound = Compound([
    compartment.moved(Location((-42, -42, 2*7))),
    bin,
])
export(*render(compound), None, 100, "subdivided-bin")

# Example 3
grid_g = [
    [True, True, True],
    [True, False, True],
    [True, True, True],
    [False, False, True],
    [True, True, True],
]
grid_f = [
    [True, True, True],
    [True],
    [True, True],
    [True],
    [True],
]
bin_g = gf.Bin(grid=grid_g, height=3*7)
bin_f = gf.Bin(grid=grid_f, height=3*7)

compound = Compound([
    bin_g.moved(Location((-42*4, -42*3, 0))),
    bin_f,
])
export(*render(compound), None, 200, "shaped-bins")


# Example 4.1
grid = [[True]]
height = 3*7
base = gf.Base(grid=grid)
grid_sketch = bd.extrude(gf.GridSketch(grid, inset=0.25), 7)
stacking_lip = gf.StackingLip(grid=grid)

compound = Compound([
    base.moved(Location((-42, -42, 0))),
    grid_sketch,
    stacking_lip.moved(Location((42, 42, 0)))
])
font_path = "/Users/moritz/Library/Fonts/FiraCode-Light.ttf"
text = ShapeList([
    Text("Base", 5, font_path=font_path)
    .moved(Location((-math.sqrt(2*42**2), -22, 0))),
    Text("GridSketch", 5, font_path=font_path)
    .moved(Location((0, -22, 0))),
    Text("StackingLip", 5, font_path=font_path)
    .moved(Location((math.sqrt(2*42**2), -22, 0)))
])
export(*render(compound), text, 200, "gf-parts")

# Example 4.2
grid = [[True], [True, True]]
base = gf.Base(grid=grid)
grid_sketch = bd.extrude(gf.GridSketch(grid, inset=0.25), 7)
stacking_lip = gf.StackingLip(grid=grid)

compound = Compound([
    base.moved(Location((-42-21, -42-21, 0))),
    grid_sketch,
    stacking_lip.moved(Location((42+21, 42+21, 0)))
])
export(*render(compound), None, 200, "gf-parts-2")
