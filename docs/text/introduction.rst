.. _introduction:

.. image:: figs/plopm.png

Introduction
============

**plopm** is a lightweight command-line tool for visualization and
postprocessing of OPM Flow geological models.

It can generate:

* two-dimensional maps of static and dynamic quantities;
* summary plots and comparisons between simulation cases;
* PNG figures and GIF animations;
* CSV data for further analysis;
* VTK files for three-dimensional visualization.

Basic usage
-----------

A typical command selects an input case, a variable, and a model slice:

.. code-block:: console

   plopm -i SPE11C -v pressure -s ,1,

This command plots pressure on the plane at ``j=1`` and writes a PNG to the
current directory.

Where to continue
-----------------

* See :doc:`installation` to install **plopm** and its optional dependencies.
* Follow the :doc:`tutorial` to progress from a first PNG to projections,
  comparisons, animations, and data export.
* Browse the :doc:`examples` for complete visualization recipes.
* Use the :doc:`command-line` for syntax and option descriptions.
* See the :doc:`api` to use **plopm** from Python.
* See :doc:`contributing` to report issues, request features, or contribute to
  **plopm**.
* Explore :doc:`related` for complementary open-source tools.

About the project
-----------------

**plopm** is funded by the `HPC Simulation Software for the Gigatonne
Storage Challenge project
<https://www.norceresearch.no/en/projects/hpc-simulation-software-for-the-gigatonne-storage-challenge>`_
(project number 622059) and the `Center for Sustainable Subsurface Resources
<https://cssr.no/>`_ (project number 331841).

Contributions are welcome. See :doc:`contributing` to propose changes or
`open an issue <https://github.com/cssr-tools/plopm/issues/new/choose>`_ to
report a problem or request a feature.
