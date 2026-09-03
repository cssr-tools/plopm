.. _example-hello-world:

Hello world
===========

Create spatial maps, summary plots, and cell time series from an SPE11B model.

Run the default command
-----------------------

Run the following command from the ``examples`` directory:

.. code-block:: console

   plopm -i SPE11B

.. figure:: ../figs/spe11b_satnum_*,1,*_t5.png
   :alt: Default SPE11B SATNUM plot on the middle xz slice
   :align: center
   :width: 90%

   The default command plots the standard static variables. This figure shows
   ``satnum`` on the default ``,1,`` slice at the final restart step.

When :option:`plopm -v` is omitted, **plopm** plots its default variable set.
The default spatial selection is ``,1,``, which displays the first xz slice.

Plot gas saturation
-------------------

Select gas saturation at restart step 4 and customize the colorbar:

.. code-block:: console

   plopm -i SPE11B -v sgas -r 4 -cbn 3 -c cubehelix -cbt '[0, middle, 0.9]'

.. figure:: ../figs/spe11b_sgas_i,1,k_t4.png
   :alt: SPE11B gas saturation at restart step 4
   :align: center
   :width: 90%

   Gas saturation on the default xz slice at restart step 4.

The command uses:

* :option:`plopm -v` to select ``sgas``.
* :option:`plopm -r` to select restart step 4.
* :option:`plopm -c` to select the ``cubehelix`` colormap.
* :option:`plopm -cbn` to use three colorbar ticks.
* :option:`plopm -cbt` to replace the numeric tick labels with custom text.

Plot field gas in place
-----------------------

Summary quantities are plotted over time rather than on a spatial slice. Plot
field gas in place with dates on the x-axis:

.. code-block:: console

   plopm -i SPE11B -v fgip -c b -ls dotted -fz 12 -fs 5,5 -lw 4 -tu dates

.. figure:: ../figs/fgip.png
   :alt: SPE11B field gas in place over time
   :align: center
   :width: 90%

   Field gas in place plotted against simulation dates.

Here, :option:`plopm -tu` selects dates, while :option:`plopm -c`,
:option:`plopm -ls`, and :option:`plopm -lw` control the line appearance.

Plot cell values over time
--------------------------

Select three cells and plot pressure increase relative to the initial pressure:

.. code-block:: console

   plopm -i 'SPE11B SPE11B SPE11B' -v 'pressure - 0pressure' -s '1,1,1 41,1,29 83,1,58' -llb 'Top left corner  Middle  Right lower corner' -yl 'Pressure increase at the sensor locations [bar]' -yf .0f -xnt 11 -tu dates

.. figure:: ../figs/spe11b_pressure-0pressure.png
   :alt: Pressure increase at three SPE11B cells over time
   :align: center
   :width: 90%

   Pressure increase at cells near the top-left corner, middle, and lower-right
   corner of the model.

Three indices in :option:`plopm -s` select one cell over time. The three input
entries correspond to the three cell selections. The expression
``pressure - 0pressure`` subtracts the initial pressure from each time step.

The legend labels are separated by two spaces. :option:`plopm -yf` displays
pressure values without decimal places, and :option:`plopm -xnt` sets eleven
x-axis ticks.

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_hello_world.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_hello_world.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_hello_world.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
