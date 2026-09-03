.. _example-relative-permeability:

Relative permeability and capillary pressure
============================================

Plot saturation functions stored in an OPM Flow deck, including hysteresis
curves when they are available.

Variable syntax
---------------

Use the saturation-function variable name by itself to read the first SATNUM
table. Append a table number to select another SATNUM region, or append ``h``
to select hysteresis curves.

Examples include:

``krg``
   Gas relative permeability from the first SATNUM table.

``krg2``
   Gas relative permeability from SATNUM table 2.

``krgh``
   Gas relative-permeability hysteresis curve.

``krwh``
   Water relative-permeability hysteresis curve.

``pcwg``
   Gas-water capillary pressure from the first SATNUM table.

Plot hysteresis relative permeability
-------------------------------------

Plot the hydrogen and brine hysteresis curves from the H2HYSTERESIS model:

.. code-block:: console

   plopm -i H2HYSTERESIS -v krgh,krwh -llb 'Hydrogen  Brine' -c r,#0314fc -x '[0,1]' -lw 5 -fz 18 -fs 8,6 -yl 'Relative permeability, $k_r$ [-]' -xl 'Liquid saturation, $s_w$ [-]' -ls solid,solid -xnt 6 -ynt 6

The variables ``krgh`` and ``krwh`` select the gas and water hysteresis curves.
The legend labels are separated by two spaces and correspond to the variables
in the order supplied through :option:`plopm -v`.

Plot capillary pressure
-----------------------

Plot the gas-water capillary-pressure curve on a logarithmic y-axis:

.. code-block:: console

   plopm -i H2HYSTERESIS -v pcwg -c k -x '[0,1]' -lw 5 -ll empty -fz 18 -fs 8,6 -yl 'Capillary pressure, $p_c$ [bar]' -xl 'Liquid saturation, $s_w$ [-]' -xnt 6 -ylog 1

.. figure:: ../figs/saturation_functions.png
   :alt: Hydrogen and brine relative permeability and gas-water capillary pressure
   :align: center
   :width: 90%

   Relative-permeability hysteresis curves for hydrogen and brine, together
   with gas-water capillary pressure.

Format the curves
-----------------

The plotting options control both saturation-function figures:

* :option:`plopm -x` limits liquid saturation to the interval from 0 to 1.
* :option:`plopm -lw` sets the line width.
* :option:`plopm -fs` sets the figure size.
* :option:`plopm -xl` and :option:`plopm -yl` set the axis labels.
* :option:`plopm -xnt` and :option:`plopm -ynt` set the axis tick counts.
* :option:`plopm -ll` removes the capillary-pressure legend.
* :option:`plopm -ylog` enables logarithmic scaling for capillary pressure.

.. note::

   The requested SATNUM table or hysteresis data must be present in the OPM
   input deck. If no suffix is supplied, **plopm** reads the first available
   saturation-function table.

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_rel_perms_and_capillary_pressure.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_rel_perms_and_capillary_pressure.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_rel_perms_and_capillary_pressure.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
