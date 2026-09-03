.. _examples-gallery:

Examples
========

Select an example to view its commands, figures, and related options.

See `this presentation <https://opm-project.org/wp-content/uploads/2025/06/OPM_summit_2025_Landa-Marban_tools_pycopm_plopm.pdf>`_ from the OPM summit 2025 for additional examples using **plopm**,
as well as the one from `the OPM summit 2026 <https://opm-project.org/wp-content/uploads/2026/05/24_David-Landa-Marban.pdf>`_.

.. warning::

   The default view is ``-s ,1,`` with equal axis scaling ``-asp 1``. For models with a
   large lateral extent, use ``-s ,,1 -asp 0`` for an unscaled top view.

.. note::

   OPM Flow is required to reproduce the examples with the supplied shell
   scripts. Install it before running them; see
   :ref:`opm-flow-installation`.

.. tip::

   Generate all documented figures from the repository root:

   .. code-block:: console

      . tests/scripts/docs_all.sh

   .. grid:: 1 2 2 2
      :gutter: 2

      .. grid-item::

         .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_all.sh
            :color: primary
            :outline:
            :expand:

            View script

      .. grid-item::

         .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_all.sh
            :color: secondary
            :outline:
            :expand:

            View raw script

Example gallery
---------------

.. grid:: 1 1 2 2
   :gutter: 3

   .. grid-item-card:: Hello world
      :link: example-hello-world
      :link-type: ref
      :img-top: figs/spe11b_sgas_i,1,k_t4.png

      Create maps, summary plots, and cell time series.

   .. grid-item-card:: Colormaps and subfigures
      :link: example-colormaps
      :link-type: ref
      :img-top: figs/spe11b_disperc_i,1,k_t5.png

      Use named, RGB, and HEX colormaps, as well as subfigures.

   .. grid-item-card:: Generic deck
      :link: example-generic-deck
      :link-type: ref
      :img-top: figs/spe10_model2_permz_*,4,*_t0.png

      Plot a generic OPM Flow model.

   .. grid-item-card:: Rotation, translation, and zoom
      :link: example-transformations
      :link-type: ref
      :img-top: figs/norne_transformed.png

      Transform, crop, and inspect Norne.

   .. grid-item-card:: Wells and faults
      :link: example-wells-faults
      :link-type: ref
      :img-top: figs/norne_faults.png

      Show wells and faults in Norne.

   .. grid-item-card:: Projections and subfigures
      :link: example-projections
      :link-type: ref
      :img-top: figs/norne_atw2013_poro_i,j,1:22_t64.png

      Combine projection methods in one figure.

   .. grid-item-card:: Histograms
      :link: example-histograms
      :link-type: ref
      :img-top: figs/norne_atw2013_permx.png

      Plot property distributions.

   .. grid-item-card:: Caprock integrity
      :link: example-caprock
      :link-type: ref
      :img-top: figs/norne_atw2013_overpres_i,j,1:22_t64.png

      Evaluate pressure limits.

   .. grid-item-card:: Reading CSV files
      :link: example-csv
      :link-type: ref
      :img-top: figs/spe11b_spatial_map_500y_xco2l_csv_t100.png

      Combine CSV and OPM Flow data.

   .. grid-item-card:: Convert to VTK
      :link: example-vtk
      :link-type: ref
      :img-top: figs/vtk_temp.png

      Export data for ParaView.

   .. grid-item-card:: Relative permeability and capillary pressure
      :link: example-relative-permeability
      :link-type: ref
      :img-top: figs/saturation_functions.png

      Plot saturation functions.

   .. grid-item-card:: Different inputs and ensembles
      :link: example-ensembles
      :link-type: ref
      :img-top: figs/ensemble.png

      Compare cases and ensembles.

   .. grid-item-card:: Filters
      :link: example-filters
      :link-type: ref
      :img-top: figs/filter_opm.png

      Select cells with conditions.

   .. grid-item-card:: GIFs and masks
      :link: example-animations
      :link-type: ref
      :img-top: figs/xco2l.gif

      Animate results and apply masks.

   .. grid-item-card:: Graphical abstract
      :link: example-graphical-abstract
      :link-type: ref
      :img-top: figs/plopm.png

      Reproduce the graphical abstract.

.. toctree::
   :hidden:
   :maxdepth: 1

   examples/hello-world
   examples/colormaps-subfigures
   examples/generic-deck
   examples/transformations
   examples/wells-faults
   examples/projections
   examples/histograms
   examples/caprock
   examples/csv
   examples/vtk
   examples/relative-permeability
   examples/ensembles
   examples/filters
   examples/animations
   examples/graphical-abstract
