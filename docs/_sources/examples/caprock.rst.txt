.. _example-caprock:

Caprock integrity
=================

Evaluate pressure limits.

``limipres``, ``overpres``, and ``objepres`` support caprock-integrity analysis.

.. code-block:: console

   plopm -i NORNE_ATW2013 -s ',,1:22 ,,1:22' -v limipres,overpres -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -fs 15,10 -c Spectral,spring -sg 1,2 -rdl 1
   plopm -i NORNE_ATW2013 -m csv -v objepres -s ',,1:22'

.. figure:: ../figs/norne_atw2013_overpres_i,j,1:22_t64.png
   :align: center
   :width: 90%

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_caprock_integrity.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_caprock_integrity.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_caprock_integrity.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
