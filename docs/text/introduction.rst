============
Introduction
============

.. image:: ./figs/plopm.png

This documentation describes the content of the **plopm** tool. 

Concept
-------
Simplified and flexible framework for quick visualization of OPM Flow geological models.
The approach is the generation of PNG figures from the static properties
(porosity, pore volume, permeability, fluid in place numbers, and saturation numbers)
given any 2D slide (e.g., the middle part of a reservoir in the xy plane). 

The **plopm** tool can be useful for quick inspection of geological models, as well as for generation of nice
figures for papers/presentations. 

Extension to plot additional static variables, as well as 
dynamic variables, is work in progress (you could easily extend the main script now as well
to plot any additional static/dynamic variable).

.. _overview:

Overview
--------
The current implementation supports the following executable with the argument options:

.. code-block:: bash

    plopm -i some_input -o some_output_folder

where 

- \-i: The base name of the input deck and output files (`SPE11B` by default).
- \-o: The base name of the output folder (`output` by default).
- \-f: The font size (`14` by default).
- \-s: The slide for the 2D maps of the static variables, e.g, `10,,` to plot the xz plane on all cells with i=10+1 (`,0,` by default, i.e., the xz surface at j=1).
- \-x: Option to set the lower and upper bounds in the 2D map along x (`` by default).
- \-y: Option to set the lower and upper bounds in the 2D map along y (`` by default).
- \-z: The option to scale the axis in the 2d maps (`yes` by default).

Installation
------------
See the `Github page <https://github.com/cssr-tools/plopm>`_.

.. tip::
    Check the `CI.yml <https://github.com/cssr-tools/plopm/blob/main/.github/workflows/CI.yml>`_ file.

Getting started
---------------
See the :doc:`examples <./examples>`.

.. tip::
    Check the `tests <https://github.com/cssr-tools/plopm/blob/main/tests>`_.