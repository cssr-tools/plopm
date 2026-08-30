.. _tutorial:

Tutorial
========

Learn **plopm** with the two- and three-dimensional SPE11B and SPE11C cases. Start with one PNG,
then progress to slices, projections, comparisons, animations, and data export.

Before starting, complete the :doc:`installation` and ensure that the
`SPE11B and SPE11C output files
<https://github.com/cssr-tools/plopm/tree/main/examples/>`_
(``.EGRID``, ``.INIT``, ``.UNRST``, ``.SMSPEC``, and ``.UNSMRY``) are
available under ``examples/``.

.. tip::

   Generate all tutorial figures and files from the repository root:

   .. code-block:: console

      . tests/scripts/docs_tutorial.sh

   .. grid:: 1 2 2 2
      :gutter: 2

      .. grid-item::

         .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_tutorial.sh
            :color: primary
            :outline:
            :expand:

            View script

      .. grid-item::

         .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_tutorial.sh
            :color: secondary
            :outline:
            :expand:

            View raw script

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: 1. Generate the first PNG
      :link: tutorial-first-png
      :link-type: ref

      Plot one quantity on one model plane.

   .. grid-item-card:: 2. Select variables and steps
      :link: tutorial-variables-steps
      :link-type: ref

      Plot static and dynamic quantities at selected restart steps.

   .. grid-item-card:: 3. Slice the 3D model
      :link: tutorial-model-slices
      :link-type: ref

      Select planes, ranges, lines, and cells.

   .. grid-item-card:: 4. Project and average
      :link: tutorial-projections
      :link-type: ref

      Reduce three-dimensional quantities to two-dimensional views.

   .. grid-item-card:: 5. Improve figure appearance
      :link: tutorial-appearance
      :link-type: ref

      Adjust output paths, labels, colors, limits, and resolution.

   .. grid-item-card:: 6. Create subfigures
      :link: tutorial-subfigures
      :link-type: ref

      Compare variables, steps, and projected quantities.

   .. grid-item-card:: 7. Follow changes over time
      :link: tutorial-time-dependent
      :link-type: ref

      Create time-dependent plots and animations.

   .. grid-item-card:: 8. Export CSV and VTK
      :link: tutorial-export
      :link-type: ref

      Export processed data for analysis and visualization.

.. toctree::
   :hidden:
   :maxdepth: 1

   tutorial/first-png
   tutorial/variables-and-steps
   tutorial/model-slices
   tutorial/projections
   tutorial/appearance
   tutorial/subfigures
   tutorial/time-dependent-output
   tutorial/export
