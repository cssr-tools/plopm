.. _example-animations:

GIFs and masks
==============

Animate results and apply masks.

Create a masked GIF comparing two cases.

.. code-block:: console

   plopm -v xco2l -sg 1,2 -i 'spe11b/SPE11B spe11b_larger_inj/SPE11B_LARGER_INJ' -fs 16,2.5 -mv satnum -r 0,1,2,3,4,5 -m gif -dpi 1000 -t 'spe11b  spe11b larger injection' -fz 16 -gi 1000 -gl 1 -cbf .2f -cbp 0.30,0.01,0.4,0.02

.. figure:: ../figs/xco2l.gif
   :align: center
   :width: 90%

Create an unmasked gas-saturation GIF with grid edges.

.. code-block:: console

   plopm -i spe11b/SPE11B -v sgas -tu y -c cet_cwr -ge 'black,5e-3' -fs 16,5 -m gif -dpi 1000 -fz 20 -gi 1000 -gl 1 -cbf .2f -asp 0 -xu km -yu km -xf .1f -yf .1f -cbn 5 -cbl 'Gas saturation [-]'

.. figure:: ../figs/spe11b_sgas.gif
   :align: center
   :width: 90%

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_gif_mask.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_gif_mask.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_gif_mask.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
