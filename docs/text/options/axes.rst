.. _options-axes:

Axes, coordinates, and formatting
=================================

Control limits, units, transformations, logarithmic axes, formats, and ticks.

.. program:: plopm

-x/--xlim <LIMITS>
------------------

.. option:: -x <LIMITS>, --xlim <LIMITS>
   :no-contents-entry:
   :no-typesetting:

Set x-axis limits in the requested display order, for example ``[-100,200]`` or ``[200,-100]``.

Separate limits for multiple plots with spaces:

.. code-block:: console

   plopm -x "[-100,200] [500,0]"

**Default:** empty

-y/--ylim <LIMITS>
------------------

.. option:: -y <LIMITS>, --ylim <LIMITS>
   :no-contents-entry:
   :no-typesetting:

Set y-axis limits in the requested display order, for example ``[0,70]`` or ``[70,0]``.

Separate limits for multiple plots with spaces:

.. code-block:: console

   plopm -y "[0,10000] [0,23000]"

**Default:** empty

-xu/--xunits <UNITS>
--------------------

.. option:: -xu <UNITS>, --xunits <UNITS>
   :no-contents-entry:
   :no-typesetting:

Set spatial-map x-axis units to ``mm``, ``cm``, ``m``, or ``km``.

**Default:** ``m``

-yu/--yunits <UNITS>
--------------------

.. option:: -yu <UNITS>, --yunits <UNITS>
   :no-contents-entry:
   :no-typesetting:

Set spatial-map y-axis units to ``mm``, ``cm``, ``m``, or ``km``.

**Default:** ``m``

-asp/--equal-aspect <0|1>
-------------------------

.. option:: -asp <0|1>, --equal-aspect <0|1>
   :no-contents-entry:
   :no-typesetting:

Scale the axes equally in two-dimensional maps when set to ``1``.

**Default:** ``1``

-rot/--rotation <DEGREES>
-------------------------

.. option:: -rot <DEGREES>, --rotation <DEGREES>
   :no-contents-entry:
   :no-typesetting:

Set the grid rotation angle in degrees for two-dimensional maps.

**Default:** ``0``

-tr/--translation <X,Y>
-----------------------

.. option:: -tr <X,Y>, --translation <X,Y>
   :no-contents-entry:
   :no-typesetting:

Set grid translation in the x and y directions, for example ``[100,-50]``.

**Default:** ``[0,0]``

-xlog/--xlog <0|1>
------------------

.. option:: -xlog <0|1>, --xlog <0|1>
   :no-contents-entry:
   :no-typesetting:

Enable a logarithmic x-axis with ``1``. Comma-separated settings are accepted when plots require different values.

**Default:** ``0``

-ylog/--ylog <0|1>
------------------

.. option:: -ylog <0|1>, --ylog <0|1>
   :no-contents-entry:
   :no-typesetting:

Enable a logarithmic y-axis with ``1``. Comma-separated settings are accepted when plots require different values.

**Default:** ``0``

-xf/--xformat <FORMAT>
----------------------

.. option:: -xf <FORMAT>, --xformat <FORMAT>
   :no-contents-entry:
   :no-typesetting:

Set the x-axis number format, for example ``.2e``.

**Default:** empty, so **plopm** selects the format.

-yf/--yformat <FORMAT>
----------------------

.. option:: -yf <FORMAT>, --yformat <FORMAT>
   :no-contents-entry:
   :no-typesetting:

Set the y-axis number format, for example ``.1f``.

**Default:** empty, so **plopm** selects the format.

-xnt/--xtick-count <COUNT>
--------------------------

.. option:: -xnt <COUNT>, --xtick-count <COUNT>
   :no-contents-entry:
   :no-typesetting:

Set the number of x-axis ticks.

**Default:** ``5``

-ynt/--ytick-count <COUNT>
--------------------------

.. option:: -ynt <COUNT>, --ytick-count <COUNT>
   :no-contents-entry:
   :no-typesetting:

Set the number of y-axis ticks.

**Default:** ``5``
