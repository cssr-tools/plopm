********
Examples
********

===========
Hello world 
===========

The simulation files located in the `examples folder <https://github.com/cssr-tools/plopm/blob/main/examples>`_ were generated using 
`pyopmspe11 <https://github.com/OPM/pyopmspe11>`_ by running this `configuration file <https://github.com/OPM/pyopmspe11/blob/main/examples/hello_world/spe11b.txt>`_. 
Then, if you succeed in installing **plopm**, inside the `examples folder <https://github.com/cssr-tools/plopm/blob/main/examples>`_ by typing in the terminal

.. code-block:: bash

    plopm -i SPE11B

the following figure should be generated (this example is used in the `tests <https://github.com/cssr-tools/plopm/blob/main/tests>`_, then it runs with the default terminal argument options).

.. figure:: figs/spe11b_satnum_*,1,*_t5.png

See the :ref:`overview` or run `plopm -h` for the definition of the argument options, as well as using `-printv` flag to output the available
summary, init, and restart available variables given an input deck.

For example, for the gas saturation at the report step number 4 using a given colormap (-c):

.. code-block:: bash

    plopm -i SPE11B -v sgas -r 4 -c cubehelix

.. figure:: figs/spe11b_sgas_*,1,*_t4.png

and for the gas in place summary vector given a color, line style, font size, dimension of the figure, line width, and using dates for the times:

.. code-block:: bash

    plopm -i SPE11B -v fgip -c b -e dotted -f 12 -d 5,5 -lw 4 -tunits dates

.. figure:: figs/fgip.png
    :scale: 7%

To plot cell values over time, this can be achieved by:

.. code-block:: bash

    plopm -i 'SPE11B SPE11B SPE11B' -v 'pressure - 0pressure' -s '1,1,1 41,1,29 83,1,58' -labels 'Top left corner  Middle  Right lower corner' -ylabel 'Pressure increase at the sensor locations [bar]' -yformat .0f -xlnum 11 -tunits dates

.. figure:: figs/spe11b_pressure-0pressure.png
    :scale: 20%

============
Generic deck 
============

See/run the `test_generic_deck.py <https://github.com/cssr-tools/plopm/blob/main/tests/test_generic_deck.py>`_ 
for an example where **plopm** is used to generate figures from the 
`SPE10_MODEL2 model <https://github.com/OPM/opm-data/tree/master/spe10model2>`_ by downloading the files and using the
`OPM Flow <https://opm-project.org/?page_id=19>`_ simulator.

.. image:: ./figs/spe10_model2_permz_*,4,*_t0.png

.. code-block:: bash

    plopm -i SPE10_MODEL2 -v permz -s ,4, -log 1 -xunits km -yunits km -xlnum 6 -yformat .2f -t 'K$_z$ at the forth slide in the xz plane' -b '[1e-7,1e3]'

Here, we look at the forth slide in the xz plane and use log scale for the permeability in the z direction, as well as changing the axis units to km, 
setting the format to the numbers to two floats in the y axis, and setting manually the upper and lower bound for the color map.

To plot information for the grid, and also the location of the wells from the top view, this is achieved by:

.. code-block:: bash

    plopm -i SPE10_MODEL2 -s ,,1 -d 3,4 -f 8 -v grid -remove 0,0,1,0 && plopm -i SPE10_MODEL2 -s ,,1 -d 3,4 -f 8 -v wells -remove 0,0,0,1

.. image:: ./figs/wells.png

Here, we use the remove flag to delete the colorbar axis in the maps for the grid and to delete the generated title in the wells plot (the first entry
in remove would delete the left axis, e.g., the y label and y ticks in this example, while the second entry if set to 1 would remove the x axis).

===============================
Rotation, translation, and zoom
===============================

This example relies on the simulation results in `opm-tests <https://github.com/OPM/opm-tests/tree/master/norne/ECL.2014.2>`_. If you
download the files in that folder, then by using the **plopm** tool:

.. code-block:: bash

    plopm -i NORNE_ATW2013 -s ,,1

these are some of the generated figures:

.. image:: ./figs/norne.png

In order to reduce the white space outside the active cells, as well as to rotate the grid and translate it, this can be ahieved by:

.. code-block:: bash

    plopm -i NORNE_ATW2013 -s ,,1 -rotate 65 -translate '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,7600]' -f 8

.. image:: ./figs/norne_transformed.png

To show all faults in the model and to only show the ones connected all along the z direction, this can be achieved by:

.. code-block:: bash

    plopm -i NORNE_ATW2013 -v faults -s ,,1 -rotate 65 -translate '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -f 8 -global 1
    plopm -i NORNE_ATW2013 -v faults -s ,,1:22 -rotate 65 -translate '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -f 8 -how max

.. image:: ./figs/norne_faults.png

To show all wells in the model and to only show the ones with at least one perforation on the top layer, this can be achieved by:

.. code-block:: bash

    plopm -i NORNE_ATW2013 -v wells -s ,,1 -rotate 65 -translate '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -f 8 -global 1
    plopm -i NORNE_ATW2013 -v wells -s ,,1 -rotate 65 -translate '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -f 8 

.. image:: ./figs/norne_wells.png

.. note::

    For plotting the faults and wells, they must be specified in the input deck (no via include files).

==========================
Projections and subfigures
==========================

Here is an example of making a single figure plotting subfigures and using different approaches to project the quantities:

.. code-block:: bash

    plopm -i NORNE_ATW2013 -v 'index_k,permx,poro' -s ',,1:22 ,,1:22 ,,1:22' -how 'first,arithmetic,max' -subfigs 1,3 -rotate 65 -translate '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -d 24,10 -c 'PuOr,vanimo,jet' -cformat '.0f,.0f,.2f' -cnum '2,4,8' -suptitle 0 -t "Top k values using first  Averaged permx using arithmetic  Values of porosity using max" -f 18

.. image:: ./figs/norne_atw2013_poro_i,j,1:22_t64.png

==============
Convert to VTK 
==============
Inside the `examples folder <https://github.com/cssr-tools/plopm/blob/main/examples>`_, then we can create VTKs from the
OPM Flow simulation results (i.e., .EGRID, .INIT, .UNRST). For example, to create VTKS for the temperature, fipnum, the co2 mass, and the co2 mass fraction in the liquid phase  
from the restart files from the initial (0) to the number 5 restart, using a OPM Flow build from source in a given path, this can be achieved by:

.. code-block:: bash
    
    plopm -i SPE11B -v temp,fipnum,co2m,xco2l -vtkformat Float32,UInt16,Float64,Float32 -r 0,5 -m vtk

.. figure:: ./figs/vtk_temp.png

    Visualization using paraview of the grid and temperature after 25 years of CO2 injection.

.. note::

    It is possible to write directly VTKs from OPM Flow simulations by adding the flag **--enable-vtk-output=true**.
    However, there are quantities that are not written (e.g., fipnum, flores), in addition to quantities not supported
    such as component mass (e.g., co2, h2o). This is when **plopm** can be helpful.

=====================
Different input files 
=====================
Let us assume we have two different runs in different folders for the spe11b case, where the firsts results are save
in a folder called spe11b, and simulation results where the injection rate has been increased are saved in a folder
called spe11b_larger_inj. Then, to plot the summary vector for both runs we can execute:

.. code-block:: bash

    plopm -i 'spe11b/SPE11B spe11b_larger_inj/SPE11B' -v 'fgip,fgipm,RGIP:3 / 2' -a 1,1e-6 -tunits w -d 10,5 -c r,b -e 'solid,dashed' -t 'Field gas in place  Comparing the total mass  Half gas in place in fipnum 3' -f 14 -subfigs 2,2 -delax 1 -loc empty,empty,empty,center -save comparison

.. image:: ./figs/comparison.png
    :scale: 6%

Here, using subplots, we plot the gas in place, injected mass and scaled to kilo tons, the regional gas in place in fipnum 3 divided by 2, and the time is shown in weeks.

.. tip::
    For any summary variable, one can give the path to more than two different simulation cases, just by separating the folder paths by spaces in the -i.

To look at the difference between these two simulations for the dynamic variable sgas at the restar step 3, this can be achieved by executing:

.. code-block:: bash

    plopm -i spe11b_larger_inj/SPE11B -v sgas -r 3 -diff spe11b/SPE11B -remove 0,0,0,1

.. image:: ./figs/sgas_diff.png

To changue the colormap and setting the colorbar limits manually, this can be achieved by:

.. code-block:: bash
    
    plopm -i spe11b_larger_inj/SPE11B -v sgas -r 3 -diff spe11b/SPE11B -remove 0,0,0,1 -c tab20c_r -b '[0,0.8]' -cnum 9

.. image:: ./figs/sgas_diff_edit.png

============
GIF and mask 
============
To create a gif and mask the results using the satnum numbers (any variable should be supported) for the different rock properties, this can be achieved by:

.. code-block:: bash

    plopm -v xco2l -subfigs 1,2 -i 'spe11b/SPE11B spe11b_larger_inj/SPE11B' -d 16,2.5 -mask satnum -r 0,5 -m gif -dpi 1000 -t "spe11b  spe11b larger injection" -f 16 -interval 1000 -loop 1 -cformat .2f -cbsfax 0.30,0.01,0.4,0.02

.. image:: ./figs/xco2l.gif