.. _tutorial-export:

Export CSV and VTK data
=======================

Export processed values for analysis or three-dimensional visualization.

CSV output
----------

.. code-block:: console

   plopm -i examples/SPE11C -v pressure -s ,1, -r 2 -m csv -fn pressure_end_simulation

Use :option:`plopm -cc` when the input itself is a CSV file.

VTK output
----------

.. code-block:: console

   plopm -i examples/SPE11B -v pressure,sgas -m vtk -fp flow -vn pressure,gas_saturation

Result
------

The first command generates the pressure_end_simulation.csv file, while the second one generates
three files: SPE11B.pvd, SPE11B-GRID.vtu, and SPE11B-0005.vtu, which can be visualized in
`ParaView <https://www.paraview.org>`_.

How it works
------------

:option:`plopm -m`
   Selects CSV or VTK output.

:option:`plopm -fp`
   Selects the Flow executable used for VTK grid generation.

:option:`plopm -vn`
   Sets readable names for exported VTK variables.

Next
----

Browse the :doc:`../examples` for task-oriented recipes, or use the
:doc:`../command-line` for exact syntax and defaults. See
:doc:`../options/vtk` for VTK-specific settings.
