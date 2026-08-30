.. _options-computation:

Computation and data transformation
===================================

Aggregate, scale, compare, and transform simulation quantities.

.. program:: plopm

-agg/--aggregation <METHODS>
----------------------------

.. option:: -agg <METHODS>, --aggregation <METHODS>
   :no-contents-entry:
   :no-typesetting:

Set aggregation or selection methods for two-dimensional slices and projections. Supported values are ``min``, ``max``, ``sum``, ``mean``, ``pvmean``, ``harmonic``, ``arithmetic``, ``first``, and ``last``.

Separate methods for multiple variables or plots with commas:

.. code-block:: console

   plopm -agg "first,arithmetic,max"

By default, continuous variables are pore-volume weighted, extensive quantities are summed, indices retain discrete values, and permeabilities use directional harmonic or arithmetic averaging.

For wells and faults, ``min`` shows cells containing at least one occurrence, while ``max`` requires all projected cells to contain one.

**Default:** empty, so **plopm** selects the method automatically.

See :ref:`tutorial-projections` for a guided workflow.

-sf/--scale-factor <FACTORS>
----------------------------

.. option:: -sf <FACTORS>, --scale-factor <FACTORS>
   :no-contents-entry:
   :no-typesetting:

Multiply variable values by a scaling factor, for example ``1e-9`` to display CO2 mass in Mt.

Separate factors for multiple variables or plots with commas, for example ``1e-5,1``.

**Default:** ``1``

-di/--difference-input <INPUT>
------------------------------

.. option:: -di <INPUT>, --difference-input <INPUT>
   :no-contents-entry:
   :no-typesetting:

Set the base name or full path of the input model to subtract from the primary input.

**Default:** empty

-sc/--stress-coefficient <VALUE>
--------------------------------

.. option:: -sc <VALUE>, --stress-coefficient <VALUE>
   :no-contents-entry:
   :no-typesetting:

Set the stress coefficient used to compute pressure limits for ``limipres``, ``overpres``, and ``objepres``.

**Default:** ``0.134``

-dg/--dual-grid <0|1>
---------------------

.. option:: -dg <0|1>, --dual-grid <0|1>
   :no-contents-entry:
   :no-typesetting:

Enable dual-grid processing with ``1`` and disable it with ``0``.

**Default:** ``0``
