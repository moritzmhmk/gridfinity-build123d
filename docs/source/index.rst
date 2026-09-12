gridfinity for build123d
========================

Build Gridfinity-compatible parts as `build123d <https://github.com/gumyr/build123d>`_
objects. Bins, baseplates, compartments and stacking lips are assembled from a
grid layout, so arbitrary shapes fall out of the same components that produce a
plain 1x1 bin.

This fork adds :class:`~gridfinity.spec.GridSpec`: the 42 mm grid pitch and the
7 mm height unit are parameters rather than literals, so the same code produces
standard Gridfinity parts or parts on a grid of your own. See :doc:`grid`.

.. image:: assets/basic-bin@light.svg
   :alt: A 1x1 bin
   :align: center

Installation
------------

With uv, from a project of your own:

.. code-block:: shell

   uv add --editable /path/to/gridfinity-build123d
   uv add "ocp-gordon==0.2.0"

The ``ocp-gordon`` pin is required: a fresh resolve of ``build123d==0.10.0``
otherwise selects a version that needs an OCP 8.x API which
``cadquery-ocp 7.8.1.1.post1`` does not provide.

With pip:

.. code-block:: shell

   pip install git+https://github.com/moritzmhmk/gridfinity-build123d

Working on the library itself:

.. code-block:: shell

   uv sync --python 3.12

The interpreter must be named. ``uv.lock`` requires ``>=3.12`` but
``pyproject.toml`` carries no ``requires-python``, so a bare ``uv sync`` takes
whatever ``python`` resolves to; 3.14 has no ``cadquery-ocp`` wheel and fails to
resolve. 3.12 and 3.13 both work. The sync installs the package itself into
``.venv`` as well, because ``pyproject.toml`` sets ``[tool.uv] package = true``.

Quickstart
----------

.. code-block:: python

   import gridfinity as gf

   # A simple 1x1 bin, three units high
   bin = gf.Bin(grid=[[True]], height=3 * 7)

A grid is a list of rows of booleans. Rows need not be the same length, and a
``False`` leaves a hole, so any shape expressible on the grid can be built:

.. code-block:: python

   grid = [
       [True, True, True],
       [True, False, True],
       [True, True, True],
       [False, False, True],
       [True, True, True],
   ]
   bin = gf.Bin(grid=grid, height=3 * 7)

.. image:: assets/shaped-bins@light.svg
   :alt: Bins with irregular shapes
   :align: center

.. toctree::
   :maxdepth: 2
   :caption: Contents

   objects
   grid
   reference

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
