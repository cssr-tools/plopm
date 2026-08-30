.. _example-projections:

Projections and subfigures
==========================

Combine projection methods in one figure.

Apply a different aggregation to each projected quantity.

.. code-block:: console

   plopm -i NORNE_ATW2013 -v 'index_k,permx,poro' -s ',,1:22 ,,1:22 ,,1:22' -agg 'first,arithmetic,max' -sg 1,3 -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -fs 24,10 -c 'PuOr,vanimo,jet' -cbf '.0f,.0f,.2f' -cbn '2,4,8' -st 0 -t 'Top k values using first  Averaged permx using arithmetic  Values of porosity using max' -fz 18

.. figure:: ../figs/norne_atw2013_poro_i,j,1:22_t64.png
   :align: center
   :width: 90%

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
