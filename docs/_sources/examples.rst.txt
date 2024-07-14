********
Examples
********

======
SPE11B 
======

The simulation files located in the `examples folder <https://github.com/cssr-tools/plopm/blob/main/examples>`_ were generated using 
`pyopmspe11 <https://github.com/OPM/pyopmspe11>`_ by running this `configuration file <https://github.com/OPM/pyopmspe11/blob/main/examples/hello_world/spe11b.txt>`_. 
Then, if you succeed in installing **plopm**, inside the `examples folder <https://github.com/cssr-tools/plopm/blob/main/examples>`_ by typing in the terminal

.. code-block:: bash

    plopm

the following figure should be generated (this example is used in the `tests <https://github.com/cssr-tools/plopm/blob/main/tests>`_, then it runs with the default terminal argument options).

.. figure:: figs/satnum_spe11b.png

The default argument options are:

.. code-block:: bash

    plopm -i SPE11B -o output -s ,,0 -f 14 -x '' -y ''

See the :ref:`overview` or run `plopm -h` for the definition of the argument options.

=====
Norne 
=====

This example relies on the input deck `NORNE_ATW2013.DATA <https://github.com/OPM/opm-tests/blob/master/norne/NORNE_ATW2013.DATA>`_ 
and the simulation results in `opm-tests <https://github.com/OPM/opm-tests/tree/master/norne/ECL.2014.2>`_. Then, if you
download the files in that folder and add the input deck in the same folder, then by using the **plopm** tool:

.. code-block:: bash

    plopm -i NORNE_ATW2013 -o . -s ,,0 -x 455600,462200 -y 7319500,7327100

these are some of the generated figures:

.. image:: ./figs/plopm.png

Here, we plot the top view (xy axis, k=1), and we set the xlim (-x) and ylim (-y) in order to reduce the white space outside the active cells.

============
Generic deck 
============

See/run the `test_generic_deck.py <https://github.com/cssr-tools/plopm/blob/main/tests/test_generic_deck.py>`_ 
for an example where **plopm** is used to generate figures from the 
`SPE10_MODEL2 model <https://github.com/OPM/opm-data/tree/master/spe10model2>`_ by downloading the files and using the
`OPM Flow <https://opm-project.org/?page_id=19>`_ simulator.

.. image:: ./figs/spe10.png

.. code-block:: bash

    plopm -i SPE10_MODEL2 -o . -s 50,,