============
Introduction
============

.. image:: ./figs/plopm.png

This documentation describes the **plopm** tool hosted in `https://github.com/cssr-tools/plopm <https://github.com/cssr-tools/plopm>`_. 

Concept
-------
Simplified and flexible framework for quick visualization of `OPM Flow <https://opm-project.org>`_ geological models.
The approach is the generation of PNG figures from static (e.g, porosity, pore volume fluid in place numbers)
and dynamic (e.g., pressure, fluid saturations) properties given any 2D slide (e.g., the middle part of a reservoir in the xy plane),
as well as plotting any given summary vector (e.g., field gas in place a.k.a fgip). 

The **plopm** tool can be useful for quick inspection of geological models, as well as for generation of nice
figures for papers/presentations. Also, **plopm** can plot summary results from different simulation cases in the same figure,
as well as the difference between given dynamic variables (e.g., pressure) for two different simulations cases. In addition, **plopm** can
convert OPM Flow output files to vtk, which allows to use other visualization/postprocessing tools (e.g., `paraview <https://www.paraview.org>`_)

.. _overview:

Overview
--------
The current implementation supports the following executable with the argument options:

.. code-block:: bash

    plopm -i name(s)_of_input_file(s)

where 

-i    The base name (or full path) of the input files; if more than one is given, separate them by ',' (e.g, 'SPE11B,/home/user/SPE11B_TUNED') ('SPE11B' by default).
-o    The base name (or full path) of the output folder ('.' by default, i.e., the folder where plopm is executed).
-v    Specify the name of the vairable to plot, e.g., 'pressure', in addition to special extensive quantities for the mass such as 'gasm', 'dism', 'liqm', 'vapm', 'co2m', 'h2om', 'fwcdm', and 'fgipm' ('' by default, i.e., plotting: porv, permx, permz, poro, fipnum, and satnum).
-m    Generate 'png' or 'vtk' files ('png' by default).
-s    The slide in the 3D model to plot the 2D maps, e.g, '10,,' to plot the xz plane on all cells with i=10 (',1,' by default, i.e., the xz surface at j=1).
-p    Path to flow, e.g., '/home/build/bin/flow'. This is used to generate the grid for the vtk files ('flow' by default).
-z    Scale the axis in the 2D maps ('1' by default).
-f    The font size ('14' by default).
-x    Set the lower and upper bounds along x, e.g., '[-100,200]' ('' by default).
-y    Set the lower and upper bounds along y, e.g., '[-10,300]' ('' by default).
-u    Use resdata or opm Python libraries ('resdata' by default).
-c    Specify the colormap, e.g., 'jet', or color(s) for the summary, e.g., 'b,r' ('' by default, i.e., set by plopm).
-e    Specify the linestyles separated by ';', e.g., 'solid;:' ('' by default, i.e., set by plopm).
-n    Specify the format for the numbers in the colormap, e.g., "lambda x, _    f'{x:.0f}'" ('' by default, i.e., set by plopm).
-b    Specify the upper and lower bounds for the color map, e.g., '[-0.1,11]' ('' by default, i.e., set by plopm).
-d    Specify the dimensions in inches generated png, e.g., '5,5' ('8,16' by default).
-l    Specify the units of the variable, e.g., \"[m\\$^2\\$]\" ('' by default, i.e., set by plopm).
-t    Specify the figure title, e.g., 'Final saturation map' ('' by default, i.e., set by plopm).
-r    Restart number to plot the dynamic variable, where 1 corresponds to the initial one ('-1' by default, i.e., the last restart file).
-w    Plot the positions of the wells or sources ('0' by default).
-g    Plot information about the number of cells in the x, y, and z directions and number of active grid cells ('0' by default).
-a    Scale the mass variable, e.g., 1e-9 for the color bar for the CO2 mass to be in Mt ('1' by default).
-time       For the x axis in the summary use seconds 's', minutes 'm', hours 'h', days 'd', weeks 'w', years 'y', or dates 'dates' ('s' by default).
-ylabel     Text for the y axis ('' by default, i.e., set by plopm).
-xlabel     Text for the x axis ('' by default, i.e., set by plopm).
-ylnum      Number of y axis labels ('4' by default).
-xlnum      Number of x axis labels ('4' by default).
-cnum       Number of color labels ('' by default, i.e., set by plopm).
-clabel     Text for the colorbar ('' by default, i.e., set by plopm).
-labels     Legend in the summary plot, separated by commas if more than one ('' by default, i.e., set by plopm).
-axgrid     Set axis.grid to True for the summary plots ('1' by default).
-dpi        Dots per inch for the figure ('300' by default).
-xformat    Format for the x numbers, e.g., .2e for exponential notation ('' by default, i.e., set by plopm).
-yformat    Format for the y numbers, e.g., .1f for one decimal ('' by default, i.e., set by plopm).
-xunits     For the x axis in the spatial maps meters 'm', kilometers 'km', centimeters 'cm', or milimeters 'mm' ('m' by default).
-yunits     For the y axis in the spatial maps meters 'm', kilometers 'km', centimeters 'cm', or milimeters 'mm' ('m' by default).
-remove     Set the entries to 1 to remove in the spatial maps the left axis, bottom axis, colorbar, and title ('0,0,0,0' by default).
-facecolor  Color outside the spatial map ('w' by default, i.e., white).
-save       Name of the output files ('' by default, i.e., set by plopm).
-log        Log scale for the color map ('0' by default).
-rotate     Grades to rotate the grid in the 2D maps ('0' by default).
-translate  Translate the grid in the 2D maps x,y directions ('[0,0]' by default).
-global     Min and max in the colorbars from the current 2D slide values (0) or whole 3D model '1' ('0' by default).
-ncolor     Color for the inactive cells in the 2D maps ('w' by default, i.e., white).

.. tip::

    Type in the terminal **plopm --help** to show these argument options.  