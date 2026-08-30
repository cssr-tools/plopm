.. _options-plot-types:

Plot types and statistical representation
=========================================

Create histograms, ensemble statistics, and step-style summary plots.

.. program:: plopm

-hist/--histogram <SPECIFICATION>
---------------------------------

.. option:: -hist <SPECIFICATION>, --histogram <SPECIFICATION>
   :no-contents-entry:
   :no-typesetting:

Set histogram bins and an optional distribution, for example ``20``, ``20,norm``, or ``20,lognorm``.

Separate specifications for multiple plots with spaces:

.. code-block:: console

   plopm -hist "50,norm 20,lognorm 100"

**Default:** empty, so no histogram is plotted.

-ens/--ensemble <MODE>
----------------------

.. option:: -ens <MODE>, --ensemble <MODE>
   :no-contents-entry:
   :no-typesetting:

Set the ensemble plotting mode:

* ``0`` disables ensemble plotting.
* ``1`` plots the mean and error bands.
* ``2`` plots the minimum, mean, and maximum.
* ``3`` plots both representations.

**Default:** ``0``

-fb/--fill-between-style <STYLE>
--------------------------------

.. option:: -fb <STYLE>, --fill-between-style <STYLE>
   :no-contents-entry:
   :no-typesetting:

Set fill colors and alpha values for ensemble error bands as comma-separated pairs, for example ``r,0.1,g,0.2``.

Use this option with ``-ens 1`` or ``-ens 3``.

**Default:** empty, so the mean color is used with an alpha value of ``0.2``.

-sp/--step-plot <0|1>
---------------------

.. option:: -sp <0|1>, --step-plot <0|1>
   :no-contents-entry:
   :no-typesetting:

Use ``ax.step`` instead of ``ax.plot`` when set to ``1``.

**Default:** ``0``
