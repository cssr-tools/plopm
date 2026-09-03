.. _example-projections:

Projections and subfigures
==========================

Project several layers onto a two-dimensional map, apply a different
aggregation method to each variable, and combine the results in one figure.

Select the projected layers
---------------------------

Use :option:`plopm -s` with the range ``1:22`` to project the first 22 layers
of the Norne model. Repeat the spatial selection once for each plotted
variable:

.. code-block:: console

   plopm -i NORNE_ATW2013 -v 'index_k,permx,poro' -s ',,1:22 ,,1:22 ,,1:22' -agg 'first,arithmetic,max' -sg 1,3 -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -fs 24,10 -c 'PuOr,vanimo,jet' -cbf '.0f,.0f,.2f' -cbn '2,4,8' -st 0 -t 'Top k values using first  Averaged permx using arithmetic  Values of porosity using max' -fz 18

.. figure:: ../figs/norne_atw2013_poro_i,j,1:22_t64.png
   :alt: Norne layer index, permeability, and porosity projected across layers 1 through 22
   :align: center
   :width: 90%

   Layer index, x-direction permeability, and porosity projected across the
   first 22 layers with three different aggregation methods.

Apply different aggregation methods
-----------------------------------

Use :option:`plopm -agg` to select how values from several cells are combined
at each projected map location. The methods are applied in the same order as
the variables:

``first``
   Selects the first value encountered along the projection direction. Here it
   displays the top ``index_k`` value.

``arithmetic``
   Calculates the arithmetic mean. Here it averages ``permx`` across the
   selected layers.

``max``
   Selects the maximum value. Here it displays the largest ``poro`` value
   across the selected layers.

The command therefore applies:

.. code-block:: text

   index_k -> first
   permx   -> arithmetic
   poro    -> max

If :option:`plopm -agg` is omitted, **plopm** selects an aggregation method
based on the variable type. Providing it explicitly is useful when comparing
projection methods or when the scientific interpretation requires a specific
calculation.

Arrange and format the subfigures
---------------------------------

The remaining options control the combined figure:

* :option:`plopm -sg` arranges the three maps in one row and three columns.
* :option:`plopm -rot` rotates the Norne grid by 65 degrees.
* :option:`plopm -tr` translates the rotated coordinates.
* :option:`plopm -x` and :option:`plopm -y` crop the displayed region.
* :option:`plopm -c` assigns a different colormap to each variable.
* :option:`plopm -cbf` applies separate colorbar number formats.
* :option:`plopm -cbn` uses 2, 4, and 8 colorbar ticks for the three maps.
* :option:`plopm -st` removes the common figure title.
* :option:`plopm -t` assigns one title to each subplot. Two spaces separate
  consecutive titles.

The lists supplied to :option:`plopm -agg`, :option:`plopm -c`,
:option:`plopm -cbf`, and :option:`plopm -cbn` correspond to the variables in
the order supplied through :option:`plopm -v`.

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_projections_subfigures.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_projections_subfigures.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_projections_subfigures.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
