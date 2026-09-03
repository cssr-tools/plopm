.. _example-histograms:

Histograms
==========

Plot distributions of static reservoir properties and optionally fit
probability distributions to the data.

Plot porosity and permeability distributions
---------------------------------------------

Plot porosity and x-direction permeability from the Norne model. Use 20 bins
for each histogram, fit a normal distribution to porosity, and fit a lognormal
distribution to permeability:

.. code-block:: console

   plopm -i NORNE_ATW2013 -v poro,permx -hist '20,norm 20,lognorm' -ag 0 -sg 1,2 -fs 15,5 -ll 'upper center' -y '[0,10000] [0,23000]' -c '#7274b3,#cddb6e'

.. figure:: ../figs/norne_atw2013_permx.png
   :alt: Porosity and permeability histograms for the Norne model
   :align: center
   :width: 90%

   Porosity with a fitted normal distribution and x-direction permeability
   with a fitted lognormal distribution.

Histogram syntax
----------------

Use :option:`plopm -hist` to set the number of bins and an optional fitted
distribution:

``20``
   Creates a histogram with 20 bins and no fitted distribution.

``20,norm``
   Creates a histogram with 20 bins and fits a normal distribution.

``20,lognorm``
   Creates a histogram with 20 bins and fits a lognormal distribution.

Separate specifications for multiple plots with spaces. In this example,
``20,norm 20,lognorm`` applies the normal fit to ``poro`` and the lognormal fit
to ``permx``.

Format the figure
-----------------

The remaining options control the subplot layout and appearance:

* :option:`plopm -ag` disables the axis grid.
* :option:`plopm -sg` places both histograms in one row with two columns.
* :option:`plopm -fs` sets the complete figure size to 15 by 5 inches.
* :option:`plopm -ll` places each legend at the upper center.
* :option:`plopm -y` applies separate y-axis limits to the two plots.
* :option:`plopm -c` assigns a different color to each histogram.

The two y-axis limits are separated by a space and correspond to the variables
in the order supplied through :option:`plopm -v`.

.. note::

   Lognormal fitting is appropriate only for positive values. Review the data
   and selected property before choosing a fitted distribution.

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_histograms.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_histograms.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_histograms.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
