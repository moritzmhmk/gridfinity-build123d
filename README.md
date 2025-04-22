# Gridfinity for build123d

This project provides a Python package to create Gridfinity compatible parts with build123d.

# Installation

```shell
pip install git+https://github.com/moritzmhmk/gridfinity-build123d
```
# Usage

## Basic usage
For simple designs the `Bin` component can be used.

### Basic bin

```python
import gridfinity as gf

# A simple 1x1 bin with a height of 3 units
bin = gf.Bin(grid=[[True]], height=3*7)
```

![1x1 Bin](./images/basic-bin@light.svg#gh-light-mode-only)
![1x1 Bin](./images/basic-bin@dark.svg#gh-dark-mode-only)

### Compartment

A negative volume can be provided to create a more complex compartment. For some common use cases the `SubdividedCompartment` from the `extra` module can be used.

```python
import gridfinity as gf

# A 1x1 bin with a subdivided compartment with scoop and label
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
```

![Negative volume and bin with compartment](./images/subdivided-bin@light.svg#gh-light-mode-only)
![Negative volume and bin with compartment](./images/subdivided-bin@dark.svg#gh-dark-mode-only)


### Bin shape

The library allows for the definition of arbitrary shapes via the grid layout.

```python
import gridfinity as gf

# Two odly shaped bins
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
```

![Bins with irregular shape](./images/shaped-bins@light.svg#gh-light-mode-only)
![Bins with irregular shape](./images/shaped-bins@dark.svg#gh-dark-mode-only)


## Advanced usage

For more complex use cases creating a custom component from the building blocks might be necessary.

```python
import build123d as bd
import gridfinity as gf

grid = [[True]]
height = 3*7
base = gf.Base(grid=grid)
grid_sketch = bd.extrude(gf.GridSketch(grid, inset=0.25), 7)
stacking_lip = gf.StackingLip(grid=grid)
```

![Gridfinity Parts](./images/gf-parts@light.svg#gh-light-mode-only)
![Gridfinity Parts](./images/gf-parts@dark.svg#gh-dark-mode-only)

Every building block has a `grid` argument to define its shape.

```python
...
grid = [[True], [True, True]]
...
```

![Gridfinity Parts](./images/gf-parts-2@light.svg#gh-light-mode-only)
![Gridfinity Parts](./images/gf-parts-2@dark.svg#gh-dark-mode-only)

## Example scripts
Scripts for the creation of some parametric designs can be found in the [examples](./examples/) folder.

## Screw holes

Each design must be published in many variations when holes for screws, magnets or other modifications are added into the design. It makes more sense to publish each design as it is (while ensuring that the lower 7mm are not used for the inner compartment). 

Possible modifications, e.g. for screws, can then be added in the slicer as a negative volume. Only one such negative volume is required for each grid layout and can be reused for all designs. 

An example of how to create negative volumes for screws can be found in the [examples](./examples/) folder.

Of course, it is still possible to add screw holes directly to the design with this library, but it is not recommended and therefore not actively supported.