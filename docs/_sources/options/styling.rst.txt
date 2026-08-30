.. _options-styling:

Color scales and styling
========================

Control colors, colorbars, lines, grids, map appearance, fonts, and resolution.

.. program:: plopm

-c/--colors <COLORS>
--------------------

.. option:: -c <COLORS>, --colors <COLORS>
   :no-contents-entry:
   :no-typesetting:

Set the colormap for spatial plots, for example ``jet``, or summary-plot colors separated by commas, for example ``b,r``.

**Default:** empty, so **plopm** selects the colors.

-cl/--clim <LIMITS>
-------------------

.. option:: -cl <LIMITS>, --clim <LIMITS>
   :no-contents-entry:
   :no-typesetting:

Set color-scale limits in the requested display order, for example ``[-0.1,11]`` or ``[11,-0.1]``. Separate limits for multiple plots with spaces.

**Default:** empty

-clog/--color-log <0|1>
-----------------------

.. option:: -clog <0|1>, --color-log <0|1>
   :no-contents-entry:
   :no-typesetting:

Enable logarithmic color scaling with ``1``. Separate settings for multiple variables with commas:

.. code-block:: console

   plopm -clog "1,1,0"

**Default:** ``0``

-clt/--color-log-ticks <TICKS>
------------------------------

.. option:: -clt <TICKS>, --color-log-ticks <TICKS>
   :no-contents-entry:
   :no-typesetting:

Set logarithmic color-scale ticks in brackets, separated by commas, for example ``[1,10,100]``. At least one corresponding :option:`plopm -clog` setting must be ``1``.

**Default:** empty

-gr/--global-range <0|1>
------------------------

.. option:: -gr <0|1>, --global-range <0|1>
   :no-contents-entry:
   :no-typesetting:

Select the values used for color scaling:

* ``0`` uses the current slice range.
* ``1`` uses the whole-model range.

**Default:** ``0``

-cbf/--colorbar-format <FORMAT>
-------------------------------

.. option:: -cbf <FORMAT>, --colorbar-format <FORMAT>
   :no-contents-entry:
   :no-typesetting:

Set the colorbar number format, for example ``.2f``.

**Default:** empty, so **plopm** selects the format.

-cbn/--colorbar-tick-count <COUNT>
----------------------------------

.. option:: -cbn <COUNT>, --colorbar-tick-count <COUNT>
   :no-contents-entry:
   :no-typesetting:

Set the number of colorbar ticks. Separate values for multiple plots with commas, for example ``3,6,2``.

**Default:** empty, so **plopm** selects the number of ticks.

-cbt/--colorbar-ticks <LABELS>
------------------------------

.. option:: -cbt <LABELS>, --colorbar-ticks <LABELS>
   :no-contents-entry:
   :no-typesetting:

Set custom colorbar tick labels in brackets, separated by commas, for example ``[G,F,E,D,C,ESF]``.

**Default:** empty

-lw/--linewidth <WIDTHS>
------------------------

.. option:: -lw <WIDTHS>, --linewidth <WIDTHS>
   :no-contents-entry:
   :no-typesetting:

Set line widths separated by commas, for example ``1,2,1.5``.

**Default:** empty, so **plopm** selects the widths.

-ls/--linestyle <STYLES>
------------------------

.. option:: -ls <STYLES>, --linestyle <STYLES>
   :no-contents-entry:
   :no-typesetting:

Set line styles separated by commas, for example ``solid,dotted``.

**Default:** empty, so **plopm** selects the styles.

-ag/--axis-grid <0|1>
---------------------

.. option:: -ag <0|1>, --axis-grid <0|1>
   :no-contents-entry:
   :no-typesetting:

Display the summary-plot axis grid when set to ``1``.

**Default:** ``1``

-fc/--facecolor <COLOR>
-----------------------

.. option:: -fc <COLOR>, --facecolor <COLOR>
   :no-contents-entry:
   :no-typesetting:

Set the color outside the spatial map.

**Default:** ``w`` (white)

-ic/--inactive-color <COLOR>
----------------------------

.. option:: -ic <COLOR>, --inactive-color <COLOR>
   :no-contents-entry:
   :no-typesetting:

Set the color of inactive cells in two-dimensional maps.

**Default:** ``w`` (white)

-ge/--grid-edges <COLOR,WIDTH>
------------------------------

.. option:: -ge <COLOR,WIDTH>, --grid-edges <COLOR,WIDTH>
   :no-contents-entry:
   :no-typesetting:

Set the ``pcolormesh`` edge color and line width, for example ``black,1e-3``.

**Default:** empty, so cell edges are not displayed.

-fz/--fontsize <SIZE>
---------------------

.. option:: -fz <SIZE>, --fontsize <SIZE>
   :no-contents-entry:
   :no-typesetting:

Set the font size.

**Default:** ``12``

-dpi/--dpi <VALUE>
------------------

.. option:: -dpi <VALUE>, --dpi <VALUE>
   :no-contents-entry:
   :no-typesetting:

Set figure resolution in dots per inch.

**Default:** ``500``
