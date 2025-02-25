from ocp_vscode import show
import gridfinity as gf

# A basic 1x1 bin
grid_1x1 = [[True]]
bin_1x1 = gf.Bin(grid=grid_1x1, height=3*7)
show(bin_1x1)

# A 1x1 bin without stacking lip
bin_1x1_wo_lip = gf.Bin(grid=grid_1x1, height=3*7, stacking_lip=None)
show(bin_1x1_wo_lip)

# A 1x1 bin without compartment (i.e. filled)
bin_1x1_filled = gf.Bin(grid=grid_1x1, height=3*7, compartment=None)
show(bin_1x1_filled)

# A 1x1 bin without stacking lip and compartment
bin_1x1_filled_wo_lip = gf.Bin(grid=grid_1x1, height=3*7,
                               stacking_lip=None, compartment=None)
show(bin_1x1_filled_wo_lip)

# A container with a compartment with thick walls
bin_1x1_thick_walls = gf.Bin(
    grid=grid_1x1,
    height=3*7,
    compartment=gf.Compartment(
        grid_1x1,  # use same grid
        2*7,  # height of bin minus 1 unit (i.e. 7 mm)
        wall_thickness=2.6
    )
)
show(bin_1x1_thick_walls)

# A 1x1 bin with a subdivided compartment
bin_1x1_div2x2 = gf.Bin(
    grid=grid_1x1,
    height=3*7,
    compartment=gf.extra.SubdividedCompartment(
        grid_1x1,  # use same grid
        height=3*7-7,  # height of bin minus 1 unit (i.e. 7 mm)
        div_x=1,
        div_y=2
    ))
show(bin_1x1_div2x2)

# A 1x1 bin with a subdivided compartment with scoop & label
bin_1x1_div2x2_scoop_label = gf.Bin(
    grid=grid_1x1,
    height=3*7,
    compartment=gf.extra.SubdividedCompartment(
        grid_1x1,  # use same grid
        height=3*7-7,  # usually height of bin minus 1 unit (i.e. 7 mm)
        div_x=1,
        div_y=2,
        with_label=True,
        scoops=["back"]
    ))
show(bin_1x1_div2x2_scoop_label)


# A simple 3x5 bin
grid_3x5 = [
    [True, True, True],
    [True, True, True],
    [True, True, True],
    [True, True, True],
    [True, True, True]
]
# alternative notation: grid_3x5 = [[True]*3] * 5
bin_3x5 = gf.Bin(grid=grid_3x5, height=3*7)
show(bin_3x5)

# An irregularly shaped bin
grid_g_shaped = [
    [True, True, True],
    [True, False, True],
    [True, True, True],
    [False, False, True],
    [True, True, True],
]
bin_g_shaped = gf.Bin(grid=grid_g_shaped, height=3*7)
show(bin_g_shaped)

# Compartments in an irregularly shaped container
bin_g_shaped_compartment = gf.Bin(
    grid=grid_g_shaped,
    height=3*7,
    compartment=gf.extra.SubdividedCompartment(
        grid_g_shaped,  # same grid
        2*7,  # 1 unit (7 mm) smaller [maximum would be 2.3*7]
        div_x=4,
        div_y=4,
        scoops=["back"],
        with_label=True
    )
)
show(bin_g_shaped_compartment)
