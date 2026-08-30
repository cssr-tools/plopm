.. _options-vtk:

VTK output
==========

These options apply only when ``-m vtk`` is selected.

.. program:: plopm

-vf/--vtk-format <FORMATS>
--------------------------

.. option:: -vf <FORMATS>, --vtk-format <FORMATS>
   :no-contents-entry:
   :no-typesetting:

Set the VTK data type for each variable. Supported formats are ``Float64``, ``Float32``, ``Float16``, ``Int64``, ``UInt64``, ``Int32``, ``UInt32``, ``Int16``, ``UInt16``, ``Int8``, and ``UInt8``.

Separate formats for multiple variables with commas.

**Default:** ``Float64``

-vn/--vtk-names <NAMES>
-----------------------

.. option:: -vn <NAMES>, --vtk-names <NAMES>
   :no-contents-entry:
   :no-typesetting:

Set custom VTK variable names separated by commas.

**Default:** empty, so the names supplied through :option:`plopm -v` are used.
