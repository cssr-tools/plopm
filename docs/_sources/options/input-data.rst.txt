.. _options-input-data:

Input and data selection
========================

Select simulation inputs, variables, restart steps, CSV columns, and the Flow executable.

.. program:: plopm

-i/--input <INPUT>
------------------

.. option:: -i <INPUT>, --input <INPUT>
   :no-contents-entry:
   :no-typesetting:

Set the base name or full path of the input. Separate multiple inputs with spaces, for example ``SPE11B /home/user/SPE11B_TUNED``.

**Default:** ``SPE11B``

-v/--variable <VARIABLES>
-------------------------

.. option:: -v <VARIABLES>, --variable <VARIABLES>
   :no-contents-entry:
   :no-typesetting:

Select the variables to plot. Separate variables with commas, for example ``pressure,sgas``.

An empty entry can act as a placeholder when the corresponding input is configured with :option:`plopm -cc`:

.. code-block:: console

   plopm -v ",BWPR:256,1,5" -cc "1,3;"

Special variables include ``grid``, ``wells``, ``faults``, ``pcfact``, ``limipres``, ``overpres``, ``objepres``, ``krw``, ``krg``, ``krow``, ``krog``, ``pcow``, ``pcog``, ``pcwg``, ``gasm``, ``dism``, ``liqm``, ``vapm``, ``co2m``, ``h2om``, ``xco2l``, ``xh2ov``, ``xco2v``, ``xh2ol``, ``fwcdm``, and ``fgipm``.

**Default:** ``poro,permx,permz,porv,fipnum,satnum``

-r/--restart <STEPS>
--------------------

.. option:: -r <STEPS>, --restart <STEPS>
   :no-contents-entry:
   :no-typesetting:

Select restart steps. ``0`` is the initial state and ``-1`` is the last state. Separate selected steps with commas, for example ``0,2`` or ``0,3,10,20``, or use ``start:end[:step]``, for example ``1:3``, ``0:4:2``, or ``5:505:250``.

GIF output uses all available steps when this option is omitted.

**Default:** ``-1``

-cc/--csv-columns <COLUMNS>
---------------------------

.. option:: -cc <COLUMNS>, --csv-columns <COLUMNS>
   :no-contents-entry:
   :no-typesetting:

Set CSV column indices, starting at 1. Use ``t,value`` for a time series or ``x,y,value`` for a spatial map.

Separate specifications for different inputs with semicolons. An empty specification skips the corresponding input, for example ``;1,2,5`` or ``1,3;``.

**Default:** empty

-fp/--flow-path <COMMAND>
-------------------------

.. option:: -fp <COMMAND>, --flow-path <COMMAND>
   :no-contents-entry:
   :no-typesetting:

Set the path or command for the Flow executable, for example ``/home/build/bin/flow``. This is used only to generate the grid for VTK output.

**Default:** ``flow``
