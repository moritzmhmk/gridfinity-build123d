from ocp_vscode import show
from gridfinity import Bin, compartments

# A simple 1x1 bin
grid_1x1 = [[True]]
bin_1x1 = Bin(grid=grid_1x1, height=3*7)
show(bin_1x1)

# A simple 1x1 bin without stacking lip
grid_1x1 = [[True]]
bin_1x1 = Bin(grid=grid_1x1, height=3*7, with_stacking_lip=False)
show(bin_1x1)

#  A simple 2x3 bin
grid_2x3 = [
    [True, True],
    [True, True],
    [True, True]
]
bin_2x3 = Bin(grid=grid_2x3, height=3*7)
show(bin_2x3)

# A simple 2x3 bin with short grid notation
bin_2x3_short = Bin(grid=[[True]*2] * 3, height=3*7)
show(bin_2x3_short)

# A 3x3 bin with a whole in the middle
grid_3x3_hole = [
    [True, True, True],
    [True, False, True],
    [True, True, True]
]
bin_3x3_hole = Bin(grid=grid_3x3_hole, height=3*7)
show(bin_3x3_hole)

# A "g" shaped bin
grid_g_shaped = [
    [True, True, True],
    [True, False, True],
    [True, True, True],
    [False, False, True],
    [True, True, True],
]
bin_g_shaped = Bin(grid=grid_g_shaped, height=3*7)
show(bin_g_shaped)


# A container with a simple compartment
bin_1x1_compartment = Bin(
    grid=grid_1x1,
    height=3*7,
    cut_compartment=compartments.Compartment(
        grid_1x1,  # same grid
        2*7  # 1 unit (7 mm) smaller [maximum would be 2.3*7]
    )
)
show(bin_1x1_compartment)

# A container with a simple compartment and thick walls
bin_1x1_compartment = Bin(
    grid=grid_1x1,
    height=3*7,
    cut_compartment=compartments.Compartment(
        grid_1x1,  # same grid
        2*7,  # 1 unit (7 mm) smaller [maximum would be 2.3*7]
        wall_thickness=2.6
    )
)
show(bin_1x1_compartment)

# A container with a subdivided compartment
bin_1x1_compartment_div1x2 = Bin(
    grid=grid_1x1,
    height=3*7,
    cut_compartment=compartments.SubdividedCompartment(
        grid_1x1,  # same grid
        2*7,  # 1 unit (7 mm) smaller [maximum would be 2.3*7]
        div_x=1,
        div_y=2
    )
)
show(bin_1x1_compartment_div1x2)

# A container with more subdivisions without scoop
bin_1x1_compartment_div2x2 = Bin(
    grid=grid_1x1,
    height=3*7,
    cut_compartment=compartments.SubdividedCompartment(
        grid_1x1,  # same grid
        2*7,  # 1 unit (7 mm) smaller [maximum would be 2.3*7]
        div_x=2,
        div_y=2,
        with_scoop=False,
        with_label=False
    )
)
show(bin_1x1_compartment_div2x2)

# Compartments in a "g" shaped container
bin_g_shaped_compartment = Bin(
    grid=grid_g_shaped,
    height=3*7,
    cut_compartment=compartments.SubdividedCompartment(
        grid_g_shaped,  # same grid
        2*7,  # 1 unit (7 mm) smaller [maximum would be 2.3*7]
        div_x=4,
        div_y=4,
        with_scoop=False,
        with_label=False
    )
)
show(bin_g_shaped_compartment)
