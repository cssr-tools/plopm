.. _example-transformations:

Rotation, translation, and zoom
===============================

Transform, crop, and inspect the Norne grid.

Start with the Norne top view
-----------------------------

Plot the first layer before applying coordinate transformations:

.. code-block:: console

   plopm -i NORNE_ATW2013 -s ,,1

.. figure:: ../figs/norne.png
   :alt: Original top view of the Norne grid
   :align: center
   :width: 90%

   Original top view of the first Norne layer.

Rotate, translate, and crop the grid
------------------------------------

Rotate the model by 65 degrees, translate the coordinates, and crop the map to
the selected x and y limits:

.. code-block:: console

   plopm -i NORNE_ATW2013 -s ,,1 -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,7600]' -fz 8

.. figure:: ../figs/norne_transformed.png
   :alt: Rotated, translated, and cropped Norne grid
   :align: center
   :width: 90%

   Norne after rotation, translation, and spatial cropping.

The transformation options are applied in the following order:

* :option:`plopm -rot` rotates the grid counterclockwise by the selected angle
  in degrees.
* :option:`plopm -tr` translates the rotated x and y coordinates.
* :option:`plopm -x` and :option:`plopm -y` crop the displayed coordinate
  range.
* :option:`plopm -fz` sets the font size.

Use the same transformation values when comparing properties, faults, wells,
or other spatial outputs from the same model. See :doc:`wells-faults` for Norne
fault and well examples using this transformation.

Reproduce this example
----------------------

Run the complete workflow from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_rotation_translation_zoom.sh

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/plopm/blob/main/tests/scripts/docs_rotation_translation_zoom.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/plopm/main/tests/scripts/docs_rotation_translation_zoom.sh
         :color: secondary
         :outline:
         :expand:

         View raw script

.. button-ref:: examples-gallery
   :ref-type: ref
   :color: primary
   :outline:

   Back to the examples gallery
