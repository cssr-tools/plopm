.. _example-ensembles:

Different inputs and ensembles
==============================

Compare cases and ensembles.

Compare summary quantities from two simulations.

.. code-block:: console

   plopm -i 'spe11b/SPE11B spe11b_larger_inj/SPE11B' -v 'fgmip,fgmip / 1E6,RGMDS:5' -yl '[kg]  [Kt]  [kg]' -tu w -fs 10,5 -c r,b -ls 'solid,dashed' -t 'Field gas mass in place  Converted to kilotonnes  Dissolved CO$_2$ in facies 5' -fz 14 -sg 2,2 -rdl 1 -ll empty,empty,empty,center -fn comparison

.. figure:: ../figs/comparison.png
   :align: center
   :width: 90%

Subtract one case from another.

.. code-block:: console

   plopm -i spe11b_larger_inj/SPE11B -v sgas -r 3 -di spe11b/SPE11B -hide 0,0,0,1

.. figure:: ../figs/sgas_diff.png
   :align: center
   :width: 90%

Format the difference map.

.. code-block:: console

   plopm -i spe11b_larger_inj/SPE11B -v sgas -r 3 -di spe11b/SPE11B -hide 0,0,0,1 -c tab20c_r -cl '[0,0.8]' -cbn 9 -cbf 0.1 -fn formated

.. figure:: ../figs/sgas_diff_edit.png
   :align: center
   :width: 90%

Use :option:`plopm -ens` for ensemble statistics.

.. figure:: ../figs/ensemble.png
   :align: center
   :width: 90%

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_different_files_and_ensembles.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_different_files_and_ensembles.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_different_files_and_ensembles.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
