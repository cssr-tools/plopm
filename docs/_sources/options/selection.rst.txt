.. _options-selection:

Spatial and temporal selection
==============================

Select model locations and summary-plot time units.

.. program:: plopm

-s/--slice <I,J,K>
------------------

.. option:: -s <I,J,K>, --slice <I,J,K>
   :no-contents-entry:
   :no-typesetting:

Set a spatial selection in ``i,j,k`` form. An empty entry selects a plane, for example ``10,,``; a range projects over cells, for example ``,,5:10``; ``:`` selects a line, for example ``:,5,7``; and three indices select a cell over time, for example ``2,4,9``.

Separate multiple selections with spaces:

.. code-block:: console

   plopm -s "1,1,1 41,1,29 83,1,58"

**Default:** ``,1,``

See :ref:`tutorial-model-slices` for a guided workflow.

-tu/--time-units <UNITS>
------------------------

.. option:: -tu <UNITS>, --time-units <UNITS>
   :no-contents-entry:
   :no-typesetting:

Set summary-plot x-axis time units. Accepted values are ``s``, ``m``, ``h``, ``d``, ``w``, ``y``, ``dates``, ``empty``, and ``tstep``.

**Default:** ``d``

-dist/--distance <MODE>
-----------------------

.. option:: -dist <MODE>, --distance <MODE>
   :no-contents-entry:
   :no-typesetting:

Compute the minimum or maximum distance to a sensor or lateral border. Accepted values are ``min,sensor``, ``max,sensor``, ``min,border``, and ``max,border``.

For a sensor, provide its ``i,j,k`` location with :option:`plopm -s`:

.. code-block:: console

   plopm -s 1,2,3 -v "sgas > 1e-2" -dist max,sensor

**Default:** empty, so no distance is computed.
