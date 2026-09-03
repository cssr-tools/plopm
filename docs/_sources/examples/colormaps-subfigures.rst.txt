.. _example-colormaps:

Colormaps and subfigures
========================

Use named colormaps, RGB values, or hexadecimal colors to customize discrete
and continuous variables. Combine several plots in one figure with either
individual or shared colorbars.

Select colors
-------------

Use :option:`plopm -c` with:

* A Matplotlib colormap name, such as ``viridis`` or ``Spectral``.
* A Colorcet colormap name, such as ``cet_glasbey_bw``.
* RGB colors written as ``red;green;blue`` values.
* Hexadecimal colors written as ``#RRGGBB``.

Separate colors belonging to one discrete palette with spaces. Separate the
color specifications for different plots with commas.

Compare three color specifications
----------------------------------

Plot ``satnum``, ``fipnum``, and ``disperc`` with a custom RGB palette, a
Colorcet colormap, and two hexadecimal colors:

.. code-block:: console

   plopm -i SPE11B -v satnum,fipnum,disperc -c '193;147;56 127;148;191 193;127;97 181;73;57 81;124;66 101;64;147 134;133;130',cet_glasbey_bw,'#b6c406 #fffa86' -sg 3,1 -rdl 1 -cbn 3,6,2 -cbf .0f,.0f,.1f -fs 7,4

.. figure:: ../figs/spe11b_disperc_i,1,k_t5.png
   :alt: SPE11B variables displayed with RGB, Colorcet, and hexadecimal colors
   :align: center
   :width: 90%

   ``satnum`` uses a custom RGB palette, ``fipnum`` uses
   ``cet_glasbey_bw``, and ``disperc`` uses two hexadecimal colors.

The custom RGB palette contains seven colors, one for each SPE11 facies:

.. code-block:: text

   193;147;56
   127;148;191
   193;127;97
   181;73;57
   81;124;66
   101;64;147
   134;133;130

The remaining options control the combined figure:

* :option:`plopm -sg` arranges the three plots in three rows and one column.
* :option:`plopm -rdl` removes repeated axis labels.
* :option:`plopm -cbn` sets 3, 6, and 2 colorbar ticks for the three plots.
* :option:`plopm -cbf` sets the corresponding colorbar number formats.
* :option:`plopm -fs` sets the figure size.

.. note::

   Quote color specifications containing spaces, semicolons, or hexadecimal
   values so the shell passes them to **plopm** as one argument.

Subfigures with individual colorbars
------------------------------------

Combine static and dynamic quantities in one figure. When the plotted
quantities use different value ranges or colormaps, each subplot has its own
colorbar:

.. code-block:: console

   plopm -i SPE11B -v poro,sgas,sgas -sg 1,3 -r 0,1,5 -st 0 -fs 25,2 -c terrain,jet,jet -cbn 5 -cbf .1f -fn poro_sgas

.. figure:: ../figs/poro_sgas.png
   :alt: SPE11B porosity and gas saturation shown in three subfigures
   :align: center
   :width: 100%

   Porosity and gas saturation at two restart steps, displayed with individual
   colorbars.

The command applies the values in each comma-separated list in subplot order:

* ``poro`` is plotted at restart step 0 with the ``terrain`` colormap.
* The first ``sgas`` plot uses restart step 1 and the ``jet`` colormap.
* The second ``sgas`` plot uses restart step 5 and the ``jet`` colormap.
* :option:`plopm -sg` arranges the three plots in one row.
* :option:`plopm -st` removes the common figure title.
* :option:`plopm -fn` sets the output filename to ``poro_sgas``.

Subfigures with a shared colorbar
---------------------------------

When subfigures show the same quantity from different inputs or restart steps,
use one shared colorbar. Position and size the shared colorbar with
:option:`plopm -cbp`:

.. code-block:: console

   plopm -i 'SPE11B SPE11C SPE11B SPE11C' -sg 2,2 -v temp -s ',1, ,14, ,1, ,14,' -r 0,0,5,2 -st 0 -fs 10,10 -asp 0 -rdl 1 -c cet_diverging_rainbow_bgymr_45_85_c67_r -cbn 5 -cbp 0.15,0.92,0.7,0.02 -cbl 'Temperature [$^o$C]' -t 'SPE11B (initial temperature)  SPE11C (initial temperature)  SPE11B (end of simulation, 25 y)  SPE11C (end of simulation, 25 y)' -fz 15

.. figure:: ../figs/spe11c_temp_i,14,k_t2.png
   :alt: SPE11B and SPE11C temperature at initial and final restart steps
   :align: center
   :width: 70%

   Initial and final temperatures for SPE11B and SPE11C, displayed with one
   shared colorbar.

The four inputs, slices, restart steps, and titles correspond by position:

.. code-block:: text

   SPE11B -> slice ,1,  -> restart 0 -> initial SPE11B temperature
   SPE11C -> slice ,14, -> restart 0 -> initial SPE11C temperature
   SPE11B -> slice ,1,  -> restart 5 -> SPE11B after 25 years
   SPE11C -> slice ,14, -> restart 2 -> SPE11C after 25 years

The shared-colorbar options are:

* :option:`plopm -cbp` sets ``left,bottom,width,height`` in figure coordinates.
* :option:`plopm -cbn` sets the number of colorbar ticks.
* :option:`plopm -cbl` sets the shared colorbar label.
* :option:`plopm -c` applies one common colormap to all four temperature maps.

:option:`plopm -asp` disables equal axis scaling, while
:option:`plopm -rdl` removes repeated subplot labels. Two spaces separate the
four titles supplied through :option:`plopm -t`.

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_colormaps-subfigures.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_colormaps-subfigures.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_colormaps-subfigures.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
