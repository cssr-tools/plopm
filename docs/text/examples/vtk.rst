.. _example-vtk:

Convert to VTK
==============

Export OPM Flow grid and property data to VTK for three-dimensional inspection
in `ParaView <https://www.paraview.org/>`_.

Requirements
------------

OPM Flow is required to generate the grid used by the VTK export. If the
``flow`` executable is not available on ``PATH``, select it with
:option:`plopm -fp`.

Export selected variables
-------------------------

Export temperature, FIP regions, total CO2 mass, and liquid-phase CO2 mass
fraction for restart steps 0 and 5:

.. code-block:: console

   plopm -i SPE11B -v temp,fipnum,co2m,xco2l -vf Float32,UInt16,Float64,Float16 -r 0,5 -m vtk

.. figure:: ../figs/vtk_temp.png
   :alt: SPE11B grid and temperature after 25 years viewed in ParaView
   :align: center
   :width: 90%

   Grid and temperature after 25 years of CO2 injection, viewed in ParaView.

Select VTK data types
---------------------

Use :option:`plopm -vf` to assign a VTK data type to each variable. The data
types correspond to the variables in the order supplied through
:option:`plopm -v`:

.. code-block:: text

   temp   -> Float32
   fipnum -> UInt16
   co2m   -> Float64
   xco2l  -> Float16

The selected types balance precision and file size:

``Float32``
   Stores temperature with single-precision floating-point values.

``UInt16``
   Stores the discrete ``fipnum`` region identifiers as unsigned integers.

``Float64``
   Preserves higher precision for total CO2 mass.

``Float16``
   Reduces storage for the bounded liquid-phase CO2 mass fraction.

Use a wider type when the expected value range or required numerical precision
cannot be represented safely by a smaller type.

Select restart steps
--------------------

The command uses :option:`plopm -r` to export the initial state and restart
step 5. **plopm** writes the selected variables for each requested step so the
results can be inspected or animated in ParaView.

Customize variable names
------------------------

Use :option:`plopm -vn` to assign custom names in the VTK output:

.. code-block:: console

   plopm -i SPE11B -v temp,fipnum,co2m,xco2l -vn temperature,fip_region,total_co2_mass,liquid_co2_fraction -vf Float32,UInt16,Float64,Float16 -r 0,5 -m vtk

The number of names supplied through :option:`plopm -vn` must match the number
of variables selected with :option:`plopm -v`.

Use a custom Flow executable
----------------------------

If Flow is installed outside ``PATH``, provide its executable explicitly:

.. code-block:: console

   plopm -i SPE11B -v temp,fipnum,co2m,xco2l -vf Float32,UInt16,Float64,Float16 -r 0,5 -m vtk -fp /path/to/flow

See :ref:`opm-flow-installation` for OPM Flow installation guidance and
:ref:`options-vtk` for the complete VTK option reference.

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_convert_to_vtk.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_convert_to_vtk.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_convert_to_vtk.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
