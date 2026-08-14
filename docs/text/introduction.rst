============
Introduction
============

.. image:: ./figs/plopm.png

This documentation describes the **plopm** tool hosted in `https://github.com/cssr-tools/plopm <https://github.com/cssr-tools/plopm>`_. 

Concept
-------
Simplified and flexible framework for quick visualization of `OPM Flow <https://opm-project.org>`_ geological models.
The approach is the generation of PNG figures from static (e.g, porosity, pore volume fluid in place numbers)
and dynamic (e.g., pressure, fluid saturations) properties given any 2D slide with the option to generate GIFs (e.g., the middle part of a reservoir in the xy plane),
as well as plotting any given summary vector (e.g., field gas in place a.k.a fgip). 

The **plopm** tool can be useful for quick inspection of geological models, as well as for generation of nice
figures for papers/presentations. Also, **plopm** can plot summary results from different simulation cases in the same figure (e.g., using subplots),
as well as the difference between given dynamic variables (e.g., pressure) for two different simulations cases. In addition, **plopm** can
convert OPM Flow output files to vtk, which allows to use other visualization/postprocessing tools (e.g., `paraview <https://www.paraview.org>`_). 

.. _overview:

Command-line options
--------------------
The current implementation supports the following executable with argument options, e.g., :

.. code-block:: bash

    plopm -i name(s)_of_input_file(s) -v name(s)_of_variables(s)

.. tip::

    Type in the terminal **plopm -h** to show a short description of the argument options.

Value and list syntax
+++++++++++++++++++++

Commas normally separate entries within one specification, while spaces
separate repeated specifications for different inputs, variables, or plots.
Enclose the complete argument in quotes when it contains spaces.

For example:

.. code-block:: console

   -v "pressure,sgas"
   -s "1,1,1 41,1,29 83,1,58"
   -y "[0,10000] [0,23000]"
   -histogram "50,norm 20,lognorm 100"
   -log "1,1,0"

The separators have the following general meanings:

* **Commas** separate components within one specification, such as
  ``2,4,9``, ``0,2,5``, or ``[100,-50]``.
* **Single spaces** separate repeated specifications, such as
  ``1,1,1 41,1,29 83,1,58`` or ``[0,10000] [0,23000]``.
* **Two spaces** separate free-text labels or titles when each value may
  itself contain spaces, such as ``Reference case  Modified case``.
* **Semicolons** separate CSV column specifications for different inputs. An
  empty specification skips the corresponding input, such as ``;1,2,5``.
* **Ampersands (&)** join filter conditions for the same input.
* **Commas in -filter** separate filter specifications for different
  inputs.
* **Empty entries** may act as placeholders where an option applies only to
  selected inputs.

For example:

.. code-block:: console

   -labels "Reference case  Modified case"
   -filter "fluxnum == 2 & sgas >= 0.2, satnum != 5"
   -i "table model" -v ",BWPR:256,1,5" -csv "1,3;"

Options
+++++++

``-i``, ``--input``
   Base name or full path of the input. Separate multiple inputs with spaces,
   e.g., ``SPE11B /home/user/SPE11B_TUNED`` (``SPE11B`` by default).

``-o``, ``--output``
   Base name or full path of the output folder (``.`` by default, i.e., the
   folder where plopm is executed).

``-v``, ``--variable``
   Variable specification(s) to plot. Separate variables with commas, e.g.,
   ``pressure,sgas``. Expressions are also supported, e.g.,
   ``pressure - 0pressure``. An empty entry may be used as a placeholder when
   the corresponding input is configured through ``-csv``, e.g.,
   ``-v ",BWPR:256,1,5" -csv "1,3;"``.

   Special variables include ``grid``, ``wells``, ``faults``, ``pcfact``,
   ``limipres``, ``overpres``, ``objepres``, ``krw``, ``krg``, ``krow``,
   ``krog``, ``pcow``, ``pcog``, ``pcwg``, ``gasm``, ``dism``, ``liqm``,
   ``vapm``, ``co2m``, ``h2om``, ``xco2l``, ``xh2ov``, ``xco2v``,
   ``xh2ol``, ``fwcdm``, and ``fgipm``
   (``poro,permx,permz,porv,fipnum,satnum`` by default).

``-m``, ``--mode``
   Output format: ``png``, ``gif``, ``csv``, or ``vtk`` (``png`` by
   default).

``-s``, ``--slide``
   Slide or location in ``i,j,k`` form. An empty entry selects a plane, e.g.,
   ``10,,``; a range projects over cells, e.g., ``,,5:10``; ``:`` selects a
   line, e.g., ``:,5,7``; and three indices select a cell over time, e.g.,
   ``2,4,9``. Separate multiple selections with spaces, e.g.,
   ``1,1,1 41,1,29 83,1,58`` (``,1,`` by default).

``-r``, ``--restart``
   Restart step(s), where ``0`` is the initial state and ``-1`` is the last.
   Separate selected steps with commas, e.g., ``0,2`` or ``0,3,10,20``, or
   use ``start:end[:step]``, e.g., ``1:3``, ``0:4:2``, or ``5:505:250``.
   The default is ``-1``; GIF output uses all available steps by default.

``-c``, ``--colors``
   Colormap, e.g., ``jet``, or summary-plot colors separated by commas, e.g.,
   ``b,r`` (empty by default, i.e., set by plopm).

``-b``, ``--bounds``
   Color-scale limits in the requested display order, e.g., ``[-0.1,11]`` or
   ``[11,-0.1]``. Separate limits for multiple plots with spaces (empty by
   default).

``-d``, ``--dimensions``
   Figure width and height in inches, separated by a comma, e.g., ``8,16``
   (``7,5`` by default).

``-f``, ``--size``
   Font size (``12`` by default).

``-t``, ``--title``
   Figure title. Separate titles for multiple plots with two spaces
   (``0`` by default).

``-suptitle``
   Title for a group of subfigures. Use ``0`` to remove it (empty by default,
   i.e., set by plopm).

``-clabel``
   Colorbar label. Separate labels for multiple plots with two spaces (empty
   by default, i.e., set by plopm).

``-xlabel``
   X-axis label. Separate labels for multiple plots with two spaces (empty by
   default, i.e., set by plopm).

``-ylabel``
   Y-axis label. Separate labels for multiple plots with two spaces (empty by
   default, i.e., set by plopm).

``-facecolor``
   Color outside the spatial map (``w`` by default, i.e., white).

``-dpi``
   Figure resolution in dots per inch (``500`` by default).

``-x``, ``--xlim``
   X-axis limits in the requested display order, e.g., ``[-100,200]`` or
   ``[200,-100]``. Separate limits for multiple plots with spaces, e.g.,
   ``[-100,200] [500,0]`` (empty by default).

``-y``, ``--ylim``
   Y-axis limits in the requested display order, e.g., ``[0,70]`` or
   ``[70,0]``. Separate limits for multiple plots with spaces, e.g.,
   ``[0,10000] [0,23000]`` (empty by default).

``-z``, ``--scale``
   Scale the axes equally in 2D maps: ``0`` or ``1`` (``1`` by default).

``-xlog``
   Enable the logarithmic x-axis using ``0`` or ``1``. Comma-separated
   settings are accepted when different plots require different values
   (``0`` by default).

``-ylog``
   Enable the logarithmic y-axis using ``0`` or ``1``. Comma-separated
   settings are accepted when different plots require different values
   (``0`` by default).

``-log``
   Enable logarithmic color scaling using ``0`` or ``1``. Separate settings
   for multiple variables with commas, e.g., ``1,1,0`` (``0`` by default).

``-clogthks``
   Tick values for logarithmic color scales, enclosed by brackets and
   separated by commas, e.g., ``[1,10,100]``. At least one corresponding
   ``-log`` setting must be ``1`` (empty by default).

``-a``, ``--adjust``
   Scaling factor applied to variable values, e.g., ``1e-9`` to display CO2
   mass in Mt. Separate factors for multiple variables or plots with commas,
   e.g., ``1e-5,1`` (``1`` by default).

``-xformat``
   X-axis number format, e.g., ``.2e`` (empty by default, i.e., set by
   plopm).

``-yformat``
   Y-axis number format, e.g., ``.1f`` (empty by default, i.e., set by
   plopm).

``-cformat``
   Colorbar number format, e.g., ``.2f`` (empty by default, i.e., set by
   plopm).

``-xlnum``
   Number of x-axis ticks (``5`` by default).

``-ylnum``
   Number of y-axis ticks (``5`` by default).

``-cnum``
   Number of colorbar ticks. Separate values for multiple plots with commas,
   e.g., ``3,6,2`` (empty by default, i.e., set by plopm).

``-cticks``
   Colorbar tick labels enclosed by brackets and separated by commas, e.g.,
   ``[G,F,E,D,C,ESF]`` (empty by default).

``-xunits``
   Spatial-map x-axis units: ``mm``, ``cm``, ``m``, or ``km`` (``m`` by
   default).

``-yunits``
   Spatial-map y-axis units: ``mm``, ``cm``, ``m``, or ``km`` (``m`` by
   default).

``-subfigs``
   Subplot rows and columns separated by a comma, e.g., ``2,2`` for four
   subplots (empty by default, i.e., separate figures).

``-loc``
   Legend location passed to ``matplotlib.pyplot.legend``: ``best``,
   ``upper right``, ``upper left``, ``lower left``, ``lower right``, ``right``,
   ``center left``, ``center right``, ``lower center``, ``upper center``, or
   ``center``. Use ``empty`` to remove the legend (``best`` by default).

``-labels``
   Summary-plot legend labels, separated by two spaces, e.g.,
   ``Reference case  Modified case`` (empty by default, i.e., set by plopm).

``-lw``
   Line widths separated by commas, e.g., ``1,2,1.5`` (empty by default,
   i.e., set by plopm).

``-e``, ``--linestyle``
   Line styles separated by commas, e.g., ``solid,dotted`` (empty by default,
   i.e., set by plopm).

``-axgrid``
   Display the summary-plot axis grid: ``0`` or ``1`` (``1`` by default).

``-remove``
   Remove the left axis, bottom axis, colorbar, and title using four
   comma-separated values of ``0`` or ``1`` (``0,0,0,0`` by default).

``-how``
   Aggregation or selection method for 2D slices and projections. Supported
   values are ``min``, ``max``, ``sum``, ``mean``, ``pvmean``, ``harmonic``,
   ``arithmetic``, ``first``, and ``last``. Separate methods for multiple
   variables or plots with commas, e.g., ``first,arithmetic,max``.

   By default, continuous variables are pore-volume weighted, extensive
   quantities are summed, indices retain discrete values, and permeabilities
   use directional harmonic or arithmetic averaging. For wells and faults,
   ``min`` shows cells containing at least one occurrence, while ``max``
   requires all projected cells to contain one (empty by default, i.e.,
   selected automatically).

``-global``
   Use the current slice range (``0``) or the whole 3D-model range (``1``)
   for color scaling (``0`` by default).

``-filter``
   Cell-selection conditions. Join conditions for one input with ``&`` and
   separate filters for different inputs with commas, e.g.,
   ``fluxnum == 2 & sgas >= 0.2, satnum != 5`` (empty by default). Dynamic
   variables such as ``sgas`` require ``RPORV`` in ``RPTRST``.

``-vmin``
   Minimum threshold used to remove variable values (empty by default).

``-vmax``
   Maximum threshold used to remove variable values (empty by default).

``-mask``
   Static variable used as the 2D-map background (empty by default).

``-maskthr``
   Threshold for the variable supplied through ``-mask`` (``1e-3`` by
   default).

``-ensemble``
   Ensemble plotting mode: ``1`` for mean and error bands, ``2`` for minimum,
   mean, and maximum, or ``3`` for both. Use ``0`` to disable ensemble
   plotting (``0`` by default).

``-bandprop``
   Fill colors and alpha values as comma-separated pairs, e.g.,
   ``r,0.1,g,0.2``. Used with ``-ensemble 1`` or ``-ensemble 3`` (empty by
   default, i.e., the mean color with alpha 0.2).

``-histogram``
   Histogram bins and optional distribution, e.g., ``20``, ``20,norm``, or
   ``20,lognorm``. Separate specifications for multiple plots with spaces,
   e.g., ``50,norm 20,lognorm 100`` (empty by default, i.e., no histogram).

``-distance``
   Compute the minimum or maximum distance to a sensor or lateral border:
   ``min,sensor``, ``max,sensor``, ``min,border``, or ``max,border``. For a
   sensor, provide its ``i,j,k`` location with ``-s``, e.g.,
   ``-s 1,2,3 -v "sgas > 1e-2" -distance max,sensor`` (empty by default).

``-stress``
   Stress coefficient used to compute pressure limits for ``limipres``,
   ``overpres``, and ``objepres`` (``0.134`` by default).

``-rotate``
   Grid rotation angle in degrees for 2D maps (``0`` by default).

``-translate``
   Grid translation in the x and y directions, e.g., ``[100,-50]``
   (``[0,0]`` by default).

``-csv``
   CSV column indices, starting at 1. Use ``t,value`` for a time series or
   ``x,y,value`` for a spatial map. Separate specifications for different
   inputs with semicolons; an empty specification skips the corresponding
   input, e.g., ``;1,2,5`` or ``1,3;`` (empty by default).

``-tunits``
   Summary x-axis time units: ``s``, ``m``, ``h``, ``d``, ``w``, ``y``,
   ``dates``, ``empty``, or ``tstep`` (``d`` by default).

``-save``
   Output file name (empty by default, i.e., set by plopm).

``-p``, ``--path``
   Path or command for the Flow executable, e.g., ``/home/build/bin/flow``.
   Used only to generate the grid for VTK output (``flow`` by default).

``-vtkformat``
   VTK format for each variable: ``Float64``, ``Float32``, ``Float16``,
   ``Int64``, ``UInt64``, ``Int32``, ``UInt32``, ``Int16``, ``UInt16``,
   ``Int8``, or ``UInt8``. Separate formats for multiple variables with
   commas (``Float64`` by default). This option applies only to VTK output.

``-vtknames``
   Custom VTK variable names separated by commas (empty by default, i.e., use
   the names supplied through ``-v``). This option applies only to VTK output.

``-diff``
   Base name or full path of the input model to subtract (empty by default).

``-ncolor``
   Color for inactive cells in 2D maps (``w`` by default, i.e., white).

``-grid``
   ``pcolormesh`` edge color and line width separated by a comma, e.g.,
   ``black,1e-3`` (empty by default, i.e., no grid).

``-cbsfax``
   Global colorbar position and size as ``left,bottom,width,height``, e.g.,
   ``0.40,0.01,0.2,0.02``. Use ``empty`` to remove it
   (``0.40,0.01,0.2,0.02`` by default).

``-delax``
   Remove duplicated axis labels in subplots: ``0`` or ``1`` (``0`` by
   default).

``-printv``
   Print the available variables: ``0`` or ``1`` (``0`` by default).

``-dual``
   Enable dual-grid processing using ``0`` or ``1`` (``0`` by default).

``-interval``
   GIF frame interval in milliseconds (``1000`` by default). This option
   applies only to GIF output.

``-loop``
   Loop GIFs indefinitely using ``0`` or ``1`` (``0`` by default). This
   option applies only to GIF output.

``-step``
   Use ``ax.step`` instead of ``ax.plot``: ``0`` or ``1`` (``0`` by
   default).
