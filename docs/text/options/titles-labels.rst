.. _options-titles-labels:

Titles, labels, and legends
===========================

Set titles, labels, legends, and the visibility of map elements.

.. program:: plopm

-t/--title <TITLE>
------------------

.. option:: -t <TITLE>, --title <TITLE>
   :no-contents-entry:
   :no-typesetting:

Set the figure title. Separate titles for multiple plots with two spaces:

.. code-block:: console

   plopm -t "Reference case  Modified case"

**Default:** ``0``

-st/--suptitle <TITLE>
----------------------

.. option:: -st <TITLE>, --suptitle <TITLE>
   :no-contents-entry:
   :no-typesetting:

Set the title for a group of subplots. Use ``0`` to remove it.

**Default:** empty, so **plopm** sets the title.

-xl/--xlabel <LABEL>
--------------------

.. option:: -xl <LABEL>, --xlabel <LABEL>
   :no-contents-entry:
   :no-typesetting:

Set the x-axis label. Separate labels for multiple plots with two spaces.

**Default:** empty, so **plopm** sets the labels.

-yl/--ylabel <LABEL>
--------------------

.. option:: -yl <LABEL>, --ylabel <LABEL>
   :no-contents-entry:
   :no-typesetting:

Set the y-axis label. Separate labels for multiple plots with two spaces.

**Default:** empty, so **plopm** sets the labels.

-cbl/--colorbar-label <LABEL>
-----------------------------

.. option:: -cbl <LABEL>, --colorbar-label <LABEL>
   :no-contents-entry:
   :no-typesetting:

Set the colorbar label. Separate labels for multiple plots with two spaces.

**Default:** empty, so **plopm** sets the labels.

-llb/--legend-labels <LABELS>
-----------------------------

.. option:: -llb <LABELS>, --legend-labels <LABELS>
   :no-contents-entry:
   :no-typesetting:

Set summary-plot legend labels. Separate labels with two spaces:

.. code-block:: console

   plopm -llb "Reference case  Modified case"

**Default:** empty, so **plopm** sets the labels.

-ll/--legend-location <LOCATION>
--------------------------------

.. option:: -ll <LOCATION>, --legend-location <LOCATION>
   :no-contents-entry:
   :no-typesetting:

Set the legend location passed to ``matplotlib.pyplot.legend``. Accepted values are ``best``, ``upper right``, ``upper left``, ``lower left``, ``lower right``, ``right``, ``center left``, ``center right``, ``lower center``, ``upper center``, and ``center``.

Use ``empty`` to remove the legend.

**Default:** ``best``

-hide/--hide-map-elements <LEFT,BOTTOM,COLORBAR,TITLE>
------------------------------------------------------

.. option:: -hide <LEFT,BOTTOM,COLORBAR,TITLE>, --hide-map-elements <LEFT,BOTTOM,COLORBAR,TITLE>
   :no-contents-entry:
   :no-typesetting:

Hide the left axis, bottom axis, colorbar, and title using four comma-separated ``0`` or ``1`` values in that order.

For example, ``1,0,1,0`` hides the left axis and colorbar while retaining the bottom axis and title.

**Default:** ``0,0,0,0``
