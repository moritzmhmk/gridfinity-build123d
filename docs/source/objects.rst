Objects
=======

Every object takes a ``grid`` and, optionally, a
:class:`~gridfinity.spec.GridSpec`. Higher-level objects are assembled from the
lower-level ones, and each can be used on its own.

Bin
---

:class:`~gridfinity.Bin` is the whole part: base, body, compartment and
stacking lip. Both the compartment and the lip can be replaced with a part of
your own, or switched off with ``None``.

.. code-block:: python

   import gridfinity as gf

   bin = gf.Bin(grid=[[True]], height=3 * 7)
   filled = gf.Bin(grid=[[True]], height=3 * 7, compartment=None)
   no_lip = gf.Bin(grid=[[True]], height=3 * 7, stacking_lip=None)

Baseplate
---------

:class:`~gridfinity.Baseplate` is the tray bins sit in. Sockets mirror the bin
foot, so any bin on the same grid pitch drops into any cell.

.. code-block:: python

   import gridfinity as gf

   baseplate = gf.Baseplate(grid=[
       [True],
       [True],
       [True, True, True],
       [True, True, True, True],
   ])

.. image:: assets/baseplate@light.svg
   :alt: A baseplate on a ragged grid
   :align: center

The plate is 4.65 mm tall: a 2.15 mm chamfer, 1.8 mm of vertical wall and a
0.7 mm bottom chamfer, per the Gridfinity specification. That 0.7 mm against
the bin foot's 0.8 mm is what gives the fit its clearance. The height is fixed
and does not scale with :class:`~gridfinity.spec.GridSpec`, but the cell pitch
does, so a 61.5 mm baseplate accepts 61.5 mm bins.

Compartments
------------

The default compartment is a plain cavity one unit below the top of the bin.
:class:`~gridfinity.extra.SubdividedCompartment` divides that cavity, and adds
labels and scoops.

.. code-block:: python

   import gridfinity as gf

   grid = [[True]]
   compartment = gf.extra.SubdividedCompartment(
       grid,
       height=3 * 7 - 7,  # usually the bin height minus one unit
       div_x=1,
       div_y=2,
       with_label=True,
       scoops=["back"],
   )
   bin = gf.Bin(grid=grid, height=3 * 7, compartment=compartment)

.. image:: assets/subdivided-bin@light.svg
   :alt: A negative volume and the bin it produces
   :align: center

Any part works as a compartment: it is subtracted from the bin body, positioned
with its top at the top of the bin.

Building blocks
---------------

For anything the :class:`~gridfinity.Bin` constructor cannot express, compose
the blocks directly.

.. code-block:: python

   import build123d as bd
   import gridfinity as gf

   grid = [[True]]
   base = gf.Base(grid=grid)
   body = bd.extrude(gf.GridSketch(grid, inset=0.25), 7)
   stacking_lip = gf.StackingLip(grid=grid)

.. image:: assets/gf-parts@light.svg
   :alt: Base, body and stacking lip
   :align: center

The same blocks follow any grid layout:

.. image:: assets/gf-parts-2@light.svg
   :alt: The same parts on a two-cell grid
   :align: center

:class:`~gridfinity.Base`
    The stackable feet and the plate they sit on, one foot per occupied cell.
    The mating half of :class:`~gridfinity.Baseplate`.

:class:`~gridfinity.GridSketch`
    The 2D footprint of the grid, optionally inset and filleted. Extrude it for
    a body, or use it as the profile for a part of your own.

:class:`~gridfinity.StackingLip`
    The lip around the top edge that a bin above locates into.

:class:`~gridfinity.Compartment`
    A plain cavity to subtract from a bin body.

Screw and magnet holes
----------------------

Holes are deliberately not part of the objects above. A design is published as
it is, with the lower 7 mm kept clear of the compartment, and the holes added in
the slicer as a negative volume. One such volume per grid layout is reusable
across every design. See ``examples/screw_holes.py``.
