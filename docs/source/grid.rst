Grid size and height units
==========================

Gridfinity is defined on a 42 mm grid in x and y, and a 7 mm height unit in z,
written ``U``. Both are defaults here, not constants:
:class:`~gridfinity.spec.GridSpec` carries them, and every object accepts one.

.. code-block:: python

   import gridfinity as gf

   spec = gf.GridSpec(size=61.5, unit=7.0)

   grid = [[True, True], [True, True]]
   bin = gf.Bin(grid=grid, height=3 * spec.unit + 4.75, spec=spec)
   plate = gf.Baseplate(grid=grid, spec=spec)

Omitting ``spec`` gives standard Gridfinity geometry, identical to what the
objects produced before the parameter existed.

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Field
     - Default
     - Meaning
   * - ``size``
     - ``42.0``
     - Grid pitch in x and y, in mm.
   * - ``unit``
     - ``7.0``
     - Height unit ``U`` in z, in mm.

A fractional height unit is expressed by multiplying:

.. code-block:: python

   spec = gf.GridSpec(size=61.5, unit=0.75 * 7)

What scales, and what does not
------------------------------

Only the grid pitch and the height unit scale. Profile geometry is absolute,
because it is fixed by the physical standard and by what a printer can produce,
not by how far apart the cells are:

* wall thickness and the 0.25 mm wall inset
* corner fillet radii, and the pad corner radius
* the base profile heights and the 0.5 mm pad clearance
* the stacking lip profile
* the 4.65 mm height of :class:`~gridfinity.Baseplate` and its socket profile
* scoop radius, label size and divider dimensions in
  :class:`~gridfinity.extra.SubdividedCompartment`

A bin at ``size=61.5`` therefore has the same walls, the same corners and the
same lip as one at 42 mm. Only the footprint changes.

.. note::

   Parts built at a non-standard pitch are consistent with each other and stack
   with each other, but they do not interoperate with standard 42 mm Gridfinity.

Where the unit is used
----------------------

``unit`` has exactly one effect inside the library: the default compartment of a
:class:`~gridfinity.Bin` is inset by one ``U`` from the top of the bin, leaving
that much solid material above the base. Bin height itself is an explicit
argument, so the caller decides how many units tall a part is:

.. code-block:: python

   spec = gf.GridSpec(unit=0.75 * 7)
   bin = gf.Bin(grid=[[True]], height=3 * spec.unit, spec=spec)

Passing a compartment explicitly bypasses that, and the caller controls the
depth directly.
