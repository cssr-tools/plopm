.. _example-generic-deck:

Generic deck
============

Use **plopm** with a generic OPM Flow model. This example uses SPE10 MODEL 2
to plot a reservoir property, inspect the grid, and display the wells.

Plot vertical permeability
--------------------------

Plot vertical permeability on the fourth slice in the xz plane:

.. code-block:: console

   plopm -i SPE10_MODEL2 -v permz -s ,4, -clog 1 -xu km -yu km -xnt 6 -yf .2f -t 'K$_z$ at the fourth slice in the xz plane' -cl '[1e-7,1e3]'

.. figure:: ../figs/spe10_model2_permz_*,4,*_t0.png
   :alt: Vertical permeability on the fourth xz slice of SPE10 MODEL 2
   :align: center
   :width: 90%

   Vertical permeability on the fourth xz slice, displayed with a logarithmic
   color scale between ``1e-7`` and ``1e3`` mD.

The main options are:

* :option:`plopm -v` selects vertical permeability, ``permz``.
* :option:`plopm -s` selects the fourth cell in the y direction and leaves the
  x and z entries empty, producing an xz slice.
* :option:`plopm -clog` enables logarithmic color scaling.
* :option:`plopm -cl` sets fixed color-scale limits.
* :option:`plopm -xu` and :option:`plopm -yu` display spatial coordinates in
  kilometres.
* :option:`plopm -xnt` sets the number of x-axis ticks.
* :option:`plopm -yf` formats the y-axis tick labels with two decimal places.

Plot the grid from above
------------------------

Select the first layer and use the special variable ``grid`` to inspect the
model geometry from above:

.. code-block:: console

   plopm -i SPE10_MODEL2 -s ,,1 -fs 3,4 -fz 8 -v grid -hide 0,0,1,0

The four values supplied to :option:`plopm -hide` control the left axis,
bottom axis, colorbar, and title, in that order. Here, the colorbar is hidden
while the axes and title remain visible.

Plot the wells from above
-------------------------

Use the same layer selection with the special variable ``wells``:

.. code-block:: console

   plopm -i SPE10_MODEL2 -s ,,1 -fs 3,4 -fz 8 -v wells -hide 0,0,0,1

.. figure:: ../figs/wells.png
   :alt: SPE10 MODEL 2 grid and wells viewed from above
   :align: center
   :width: 90%

   Top views of the SPE10 MODEL 2 grid and declared wells.

For the wells plot, the final value in :option:`plopm -hide` removes the title.
The well locations must be available in the OPM input deck.

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_generic_deck.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_generic_deck.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_generic_deck.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
