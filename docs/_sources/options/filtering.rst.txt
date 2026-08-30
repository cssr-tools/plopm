.. _options-filtering:

Filtering, masking, and thresholds
==================================

Filter cells, remove values, and add a static map mask.

.. program:: plopm

-flt/--filters <CONDITIONS>
---------------------------

.. option:: -flt <CONDITIONS>, --filters <CONDITIONS>
   :no-contents-entry:
   :no-typesetting:

Set cell-selection conditions. Join conditions for one input with ``&`` and separate filters for different inputs with commas:

.. code-block:: console

   plopm -flt "fluxnum == 2 & sgas >= 0.2, satnum != 5"

Dynamic variables such as ``sgas`` require ``RPORV`` in ``RPTRST``.

**Default:** empty

-vmin/--min-threshold <VALUE>
-----------------------------

.. option:: -vmin <VALUE>, --min-threshold <VALUE>
   :no-contents-entry:
   :no-typesetting:

Remove variable values below the minimum threshold.

**Default:** empty

-vmax/--max-threshold <VALUE>
-----------------------------

.. option:: -vmax <VALUE>, --max-threshold <VALUE>
   :no-contents-entry:
   :no-typesetting:

Remove variable values above the maximum threshold.

**Default:** empty

-mv/--mask-variable <VARIABLE>
------------------------------

.. option:: -mv <VARIABLE>, --mask-variable <VARIABLE>
   :no-contents-entry:
   :no-typesetting:

Use a static variable as the background of a two-dimensional map.

**Default:** empty

-mt/--mask-threshold <VALUE>
----------------------------

.. option:: -mt <VALUE>, --mask-threshold <VALUE>
   :no-contents-entry:
   :no-typesetting:

Set the threshold applied to the variable supplied through :option:`plopm -mv`.

**Default:** ``1e-3``
