.. _options-output:

Output options
==============

Choose the output format, directory, and filename.

.. program:: plopm

-m/--format <FORMAT>
--------------------

.. option:: -m <FORMAT>, --format <FORMAT>
   :no-contents-entry:
   :no-typesetting:

Select the output format: ``png``, ``gif``, ``csv``, or ``vtk``.

**Default:** ``png``

-o/--output-dir <DIRECTORY>
---------------------------

.. option:: -o <DIRECTORY>, --output-dir <DIRECTORY>
   :no-contents-entry:
   :no-typesetting:

Set the base name or full path of the output directory.

**Default:** ``.``, the directory where **plopm** is executed.

-fn/--filename <NAME>
---------------------

.. option:: -fn <NAME>, --filename <NAME>
   :no-contents-entry:
   :no-typesetting:

Set the output filename.

**Default:** empty, so **plopm** generates the name.
