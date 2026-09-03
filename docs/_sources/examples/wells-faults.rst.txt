.. _example-wells-faults:

Wells and faults
================

Plot faults and wells declared in the Norne input deck. Apply the same rotation,
translation, and cropping values used for the transformed Norne grid so the
outputs remain spatially consistent.

.. note::

   Faults and wells must be declared directly in the input deck.

Plot faults
-----------

Plot faults intersecting the first layer and use the whole-model value range:

.. code-block:: console

   plopm -i NORNE_ATW2013 -v faults -s ,,1 -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -fz 8 -gr 1

Project faults across layers 1 through 22. Use ``max`` so a map cell is shown
only when the projected fault condition is present across the selected cells:

.. code-block:: console

   plopm -i NORNE_ATW2013 -v faults -s ,,1:22 -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -fz 8 -agg max

.. figure:: ../figs/norne_faults.png
   :alt: Norne faults on one layer and projected across layers 1 through 22
   :align: center
   :width: 90%

   Norne faults on the first layer and projected across the first 22 layers.

The main options are:

* ``faults`` is a special variable selected with :option:`plopm -v`.
* :option:`plopm -gr` uses the whole-model range for the first-layer plot.
* :option:`plopm -agg` controls how faults are combined across a layer range.
* :option:`plopm -rot`, :option:`plopm -tr`, :option:`plopm -x`, and
  :option:`plopm -y` apply the same transformation as the property map.

Plot wells
----------

Plot all wells declared in the model, regardless of whether they intersect the
selected layer:

.. code-block:: console

   plopm -i NORNE_ATW2013 -v wells -s ,,1 -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -fz 8 -gr 1 -fn norne_wells_global

Plot only the wells intersecting the selected layer:

.. code-block:: console

   plopm -i NORNE_ATW2013 -v wells -s ,,1 -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -fz 8 -fn norne_wells

.. figure:: ../figs/norne_wells.png
   :alt: All Norne wells and wells intersecting the selected layer
   :align: center
   :width: 90%

   All declared Norne wells and the subset intersecting the first layer.

For the first command, :option:`plopm -gr` selects the global well view and
:option:`plopm -fn` writes ``norne_wells_global``. Without the global-range
selection, the second command restricts the output to wells associated with the
selected layer and writes ``norne_wells``.

See :doc:`transformations` for the original and transformed Norne grid views.

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_wells-faults.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_wells-faults.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_wells-faults.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
