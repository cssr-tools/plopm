plopm
=====

.. rst-class:: lead

   A lightweight and flexible tool for visualization and postprocessing of
   OPM Flow geological models.

**plopm** generates publication-ready PNG figures, GIF animations, CSV data,
and VTK files from OPM Flow simulation output.

.. grid:: 1 2 2 4
   :gutter: 3
   :margin: 4 0 4 0

   .. grid-item-card:: :octicon:`rocket;1.2em` Get started
      :link: introduction
      :link-type: doc

      Learn what **plopm** does and where to begin.

   .. grid-item-card:: :octicon:`download;1.2em` Install plopm
      :link: installation
      :link-type: doc

      Install **plopm** and the optional OPM Flow and LaTeX dependencies.

   .. grid-item-card:: :octicon:`book;1.2em` Follow the tutorial
      :link: tutorial
      :link-type: doc

      Progress from a first PNG to projections, comparisons, and data export.

   .. grid-item-card:: :octicon:`image;1.2em` Explore examples
      :link: examples
      :link-type: doc

      Browse task-oriented examples with figures and reproducible scripts.

Quick installation
------------------

Install the current development version from GitHub:

.. code-block:: console

   pip install git+https://github.com/cssr-tools/plopm.git

See :doc:`installation` for virtual environments, source installation, OPM
Flow, and optional LaTeX support.

Quick start
-----------

Plot pressure on the plane at ``j=1``:

.. code-block:: console

   plopm -i examples/SPE11B -v pressure -s ,1,

Display the built-in help or list the variables available for an input case:

.. code-block:: console

   plopm --help
   plopm -i examples/SPE11B -lv 1

See the :doc:`tutorial` for a guided workflow and the :doc:`command-line` for
exact syntax and option descriptions.

What can plopm do?
------------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Plot reservoir properties

      Visualize static and dynamic quantities on model slices and projections.

   .. grid-item-card:: Compare simulations

      Plot multiple cases, differences, summary vectors, and ensembles.

   .. grid-item-card:: Create reusable outputs

      Export PNG figures, GIF animations, CSV data, and VTK datasets.

   .. grid-item-card:: Support reproducible workflows

      Reproduce visualization and postprocessing tasks from shell scripts.

.. toctree::
   :hidden:
   :maxdepth: 2

   introduction
   installation
   tutorial
   examples
   command-line
   api
   contributing
   related
