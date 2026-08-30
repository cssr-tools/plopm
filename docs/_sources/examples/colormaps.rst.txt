.. _example-colormaps:

Colormaps
=========

Use named, RGB, and HEX colormaps.

Use :option:`plopm -c` with Matplotlib or Colorcet names, RGB values, or HEX colors.

.. code-block:: console

   plopm -i SPE11B -v satnum,fipnum,disperc -c '193;147;56 127;148;191 193;127;97 181;73;57 81;124;66 101;64;147 134;133;130',cet_glasbey_bw,'#b6c406 #fffa86' -sg 3,1 -rdl 1 -cbn 3,6,2 -cbf .0f,.0f,.1f -fs 7,4

.. figure:: ../figs/spe11b_disperc_i,1,k_t5.png
   :align: center
   :width: 90%

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_colormaps.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_colormaps.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_colormaps.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
