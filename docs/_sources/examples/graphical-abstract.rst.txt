.. _example-graphical-abstract:

Graphical abstract
==================

Reproduce the graphical abstract.

The graphical abstract combines an SPE11B summary comparison, a Norne map, and an SPE11C VTK visualization.

.. figure:: ../figs/plopm.png
   :align: center
   :width: 90%

   The plopm graphical abstract.

Generate the SPE11B comparison.

.. code-block:: console

   plopm -i 'spe11b/SPE11B spe11b_higher_rate/SPE11B_HIGHER_RATE' -v 'fgmip * 1e-6' -c 'r,b' -tu y -xf .0f -lw 2 -llb 'Base case  Higher injection rate' -xnt 6 -yl 'Total CO$_2$ mass [Kt]' -fz 18 -t 'Comparing two runs of the SPE11B model'

Generate the Norne map.

.. code-block:: console

   git clone https://github.com/OPM/opm-data.git
   flow opm-data/norne/NORNE_ATW2013.DATA --enable-dry-run=1
   plopm -i opm-data/norne/NORNE_ATW2013 -v permx -clog 1 -rot 65 -s ,,1 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,7600]' -t 'Top view of NORNE' -xu km -yu km -fz 16 -ge 'black,1e-2' -xf .1f -yf .1f -fs 8,8

Generate SPE11C VTK files.

.. code-block:: console

   pip install git+https://github.com/OPM/pyopmspe11.git
   curl -L -O https://raw.githubusercontent.com/OPM/pyopmspe11/refs/heads/main/examples/spe11c.toml
   pyopmspe11 -i spe11c.toml -o spe11c -fz 0
   plopm -i spe11c/SPE11C -v satnum,xco2l -vf UInt16,Float16 -r 0,5 -m vtk

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_graphical_abstract.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_graphical_abstract.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_graphical_abstract.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
