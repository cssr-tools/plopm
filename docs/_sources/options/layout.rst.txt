.. _options-layout:

Figure and subplot layout
=========================

Set figure dimensions, subplot layout, and the global colorbar.

.. program:: plopm

-fs/--figsize <WIDTH,HEIGHT>
----------------------------

.. option:: -fs <WIDTH,HEIGHT>, --figsize <WIDTH,HEIGHT>
   :no-contents-entry:
   :no-typesetting:

Set the figure width and height in inches, separated by a comma, for example ``8,16``.

**Default:** ``7,5``

-sg/--subplot-grid <ROWS,COLUMNS>
---------------------------------

.. option:: -sg <ROWS,COLUMNS>, --subplot-grid <ROWS,COLUMNS>
   :no-contents-entry:
   :no-typesetting:

Set the number of subplot rows and columns, separated by a comma, for example ``2,2`` for four subplots.

**Default:** empty, so separate figures are created.

-cbp/--colorbar-position <LEFT,BOTTOM,WIDTH,HEIGHT>
---------------------------------------------------

.. option:: -cbp <LEFT,BOTTOM,WIDTH,HEIGHT>, --colorbar-position <LEFT,BOTTOM,WIDTH,HEIGHT>
   :no-contents-entry:
   :no-typesetting:

Set the global colorbar position and size as ``left,bottom,width,height``, for example ``0.1,0.95,0.8,0.02``.

Use ``empty`` to remove the global colorbar.

**Default:** ``0.2,0.01,0.6,0.02``

-rdl/--remove-duplicate-labels <0|1>
------------------------------------

.. option:: -rdl <0|1>, --remove-duplicate-labels <0|1>
   :no-contents-entry:
   :no-typesetting:

Remove duplicated axis labels in subplot layouts when set to ``1``.

**Default:** ``0``
