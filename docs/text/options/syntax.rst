.. _command-line-syntax:

Syntax and conventions
======================

A **plopm** command selects input data, variables, and an output:

.. code-block:: console

   plopm -i INPUT -v VARIABLES [OPTIONS]

For example:

.. code-block:: console

   plopm -i SPE11C -v pressure -s ,1, -r 2

Use ``plopm --help`` for the options supported by the installed version.

Canonical option names
----------------------

Each option has a short and a long canonical name:

.. code-block:: console

   plopm -i SPE11C -v pressure
   plopm --input SPE11C --variable pressure

Commands in this documentation use the short canonical names. The category
pages show both forms.

Paths and quoting
-----------------

Quote paths and values that contain spaces:

.. code-block:: console

   plopm -i "/path/to/my case/SPE11C" -v pressure

Multiple inputs
---------------

Separate input cases with spaces and quote the complete value:

.. code-block:: console

   plopm -i "SPE11C SPE11C_TUNED" -v pressure

See :option:`plopm -i`.

Multiple variables
------------------

Separate variables with commas:

.. code-block:: console

   plopm -i SPE11C -v pressure,sgas

See :option:`plopm -v`.

Expressions
-----------

Quote expressions containing spaces:

.. code-block:: console

   plopm -i SPE11C -v "pressure - 0pressure"

See :option:`plopm -v`.

Spatial selections
------------------

The spatial selection uses three comma-separated positions:

.. code-block:: text

   I,J,K

Select the plane at ``j=10``:

.. code-block:: console

   plopm -i SPE11C -v pressure -s ,10,

Select layers 5 through 10:

.. code-block:: console

   plopm -i SPE11C -v pressure -s ,,5:10

See :option:`plopm -s` and :ref:`tutorial-model-slices`.

Restart steps
-------------

Select one restart step:

.. code-block:: console

   plopm -i SPE11C -v pressure -r 5

Select several steps:

.. code-block:: console

   plopm -i SPE11C -v pressure -r 0,3,10

Select a range using ``start:end[:step]``:

.. code-block:: console

   plopm -i SPE11C -v pressure -r 5:505:250

See :option:`plopm -r`.

Aggregation
-----------

Select a range with ``-s`` and apply an aggregation method with ``-agg``:

.. code-block:: console

   plopm -i SPE11C -v pressure -s ,,5:10 -agg mean -r 2

Supported methods are ``min``, ``max``, ``sum``, ``mean``, ``pvmean``,
``harmonic``, ``arithmetic``, ``first``, and ``last``.

See :option:`plopm -agg` and :ref:`tutorial-projections`.

Text for multiple plots
-----------------------

Some title and label options use two spaces to separate text for different
plots. Quote the complete value:

.. code-block:: console

   plopm -i SPE11C -v pressure,sgas -sg 1,2 -t "Pressure  Gas saturation"

See :option:`plopm -t` and :option:`plopm -sg`.

Output formats
--------------

Use ``-m`` to select PNG, GIF, CSV, or VTK output:

.. code-block:: console

   plopm -i SPE11C -v pressure -m png
   plopm -i SPE11C -v pressure -m gif
   plopm -i SPE11C -v pressure -m csv
   plopm -i SPE11C -m vtk

See :option:`plopm -m`.

Getting help
------------

Display the built-in help:

.. code-block:: console

   plopm --help

Print the variables available for an input case:

.. code-block:: console

   plopm -i SPE11C -lv 1

See :option:`plopm -lv`.
