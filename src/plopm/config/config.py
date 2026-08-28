# SPDX-FileCopyrightText: 2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0103,R0902

"""Configuration and simulation-data models shared across plopm workflows.

PlopmConfig stores command-line options and normalized runtime settings used to
create summary plots, spatial maps, animations, and VTK output. SimData stores
OPM file handles, grid dimensions, and cell data loaded for one simulation case.

Both objects are mutable because CLI values are normalized and simulation data
are populated progressively during processing.
"""

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import EGrid as OpmGrid
from opm.io.ecl import ERst as OpmRestart


@dataclass(slots=True)
class PlopmConfig:
    """Options and runtime settings for a plopm operation.

    Most list fields contain one value per variable, case, or subplot after
    initialization. Values read from the CLI are normalized before plotting so
    downstream functions can use consistent indexing.

    Attributes
    ----------
    gif, csv, png, vtk
        Whether GIF, CSV, PNG, or VTK output is active for the current run.
    equal_aspect
        Whether spatial maps use the same scale along both coordinate axes.
    remove_duplicate_labels
        Whether repeated axis labels are hidden in subplot layouts.
    list_variables
        Whether available INIT, UNRST, and summary variables are printed.
    gif_loop
        Whether generated GIF animations repeat after the final frame.
    step_plot
        Whether one-dimensional series are drawn as step plots.
    global_range
        Whether map limits and features are evaluated globally instead of only
        within the selected slice.
    rst_range
        Whether PNG color limits are evaluated over the restart range.
    sensor
        Whether one-dimensional values are extracted at a grid-cell sensor.
    layer
        Whether one-dimensional values are extracted along a grid axis or layer.
    csv_column_summary
        Whether a one-dimensional series is read from CSV columns.
    discrete
        Whether the current spatial quantity uses discrete color categories.
    fontsize
        Base font size used in generated figures.
    mask_threshold
        Threshold applied to the selected mask variable.
    gif_interval
        Delay between GIF frames.
    stress_coefficient
        Vertical stress coefficient used for caprock-integrity quantities.
    xscale, yscale
        Factors converting grid coordinates to the requested spatial units.
    ensemble
        Ensemble mode controlling uncertainty bands and bounding members.
    ncolors
        Number of case-dependent styles used for summary plots.
    color_log_ticks
        Tick values used on logarithmic colorbars.
    case_labels
        User-provided case names used in legends and ensemble labels.
    cases
        Simulation-case paths grouped as requested by the CLI.
    dual_grid
        Per-variable flags enabling dual-porosity grid handling.
    subplot_grid
        Requested subplot rows and columns.
    variables
        Variables or variable expressions requested for processing.
    filters
        Property-filter expressions applied per case or variable.
    title
        Per-plot titles.
    clim
        Lower and upper color limits for spatial maps.
    figsize
        Figure width and height for each generated plot.
    min_threshold, max_threshold
        Limits outside which quantity values are hidden.
    grid_edges
        Per-map settings controlling cell-edge drawing.
    colorbar_tick_count
        Requested number of colorbar ticks.
    legend_labels
        Labels for cases, variables, or ensemble bounds.
    hide_map_elements
        Map components to omit, such as axes, labels, or colorbars.
    time_units
        Requested time unit for each one-dimensional plot.
    scale_factor
        Multipliers applied to plotted or exported quantity values.
    axis_grid
        Per-plot settings controlling the Matplotlib axis grid.
    dpi
        Output resolution for each generated figure.
    colorbar_ticks
        Explicit colorbar tick values.
    legend_location
        Per-plot legend placement.
    vtk_format
        VTK data type selected for each exported variable.
    vtk_names
        Variable names written to VTK cell-data arrays.
    color_log
        Flags selecting logarithmic color normalization.
    rotation
        Rotation angles applied to grid coordinates, in degrees.
    filename
        Output filenames normalized per requested plot.
    translation
        Coordinate translations applied after rotation.
    restart
        Selected OPM restart report steps.
    aggregation
        Aggregation method applied through a slice or selected cells.
    distance
        Distance method and target, such as a sensor or model boundaries.
    histogram
        Histogram settings, including the requested bins.
    xlabel, ylabel
        Per-plot axis labels.
    xformat, yformat
        Format strings used for axis tick labels.
    xtick_count, ytick_count
        Requested numbers of major ticks.
    xlog, ylog
        Flags selecting logarithmic axes.
    xlim, ylim
        Per-plot axis limits.
    vsum
        Summary-variable expressions prepared for plotting.
    summary
        Loaded or derived summary-series values.
    time
        Time coordinates associated with summary values.
    wells, faults
        Parsed feature locations used in spatial maps.
    slice
        Parsed i, j, and k selections used by all workflows.
    csv_columns
        CSV column settings retained in parsed per-plot form.
    mass_vars
        Supported component-mass quantities.
    summary_mass
        Summary vectors converted from standard volume to mass.
    mass_fracs
        Supported component mass-fraction quantities.
    caprock_vars
        Supported caprock-integrity quantities.
    linewidth_values
        Default line widths before per-variable normalization.
    units
        Display units associated with requested quantities.
    cb_formats
        Normalized numeric formats used for colorbar labels.
    colormaps
        Colormaps assigned to spatial variables.
    disc_colormaps
        Available colormaps suitable for discrete values.
    linestyle, linewidth, colors
        Normalized styles used by summary plots.
    colors_default, linestyle_default
        Default style sequences used when none are supplied.
    colorbar_position
        Relative position and size of an explicitly placed colorbar axis.
    difference_input
        Second case, folder, or file used to calculate differences.
    colors_raw
        Color specification received from the CLI before normalization.
    output_dir
        Directory in which generated files are written.
    case
        Primary case path used for file detection and classification.
    fill_between_style
        Colors and opacity values for ensemble uncertainty bands.
    colorbar_format
        Colorbar format specification received from the CLI.
    fc
        Figure or axes face color.
    inactive_color
        Color assigned to inactive grid cells.
    mask_variable
        Variable used to mask spatial-map values.
    suptitle
        Figure-level title shared by all subplots.
    colorbar_label
        User-provided colorbar label.
    slice_mode
        Mode used when retaining wells or faults in an aggregated slice.
    xunits, yunits
        Requested spatial unit codes for both coordinate axes.
    xunit, yunit
        Formatted spatial unit labels shown on the axes.
    slices
        Normalized half-open ranges used for spatial slice aggregation.
    csv_cols
        Normalized CSV column indices used for gridded CSV data.
    """

    # Output modes and processing switches
    gif: bool = False
    csv: bool = False
    png: bool = False
    vtk: bool = False
    equal_aspect: bool = False
    remove_duplicate_labels: bool = False
    list_variables: bool = False
    gif_loop: bool = False
    step_plot: bool = False
    global_range: bool = False
    rst_range: bool = False  # Evaluate color limits across restart steps
    sensor: bool = False
    layer: bool = False
    csv_column_summary: bool = False
    discrete: bool = True

    # Scalar plot and animation settings
    fontsize: float = 0.0
    mask_threshold: float = 0.0
    gif_interval: float = 0.0
    stress_coefficient: float = 0.0
    xscale: float = 1.0
    yscale: float = 1.0
    ensemble: int = 0  # 0: off; 1: band; 2: bounds; 3: both
    ncolors: int = 1

    # Input cases, variables, and normalized selections
    color_log_ticks: list = field(default_factory=list)
    case_labels: list = field(default_factory=list)  # Before path expansion
    cases: list = field(default_factory=list)  # Nested groups of case stems
    dual_grid: list = field(default_factory=list)
    subplot_grid: list = field(default_factory=list)
    variables: list = field(default_factory=list)
    filters: list = field(default_factory=list)

    # Figure, subplot, and axis settings
    title: list = field(default_factory=list)
    clim: list = field(default_factory=list)
    figsize: list = field(default_factory=list)
    min_threshold: list = field(default_factory=list)
    max_threshold: list = field(default_factory=list)

    # Color, line, and map styling
    grid_edges: list = field(default_factory=list)
    colorbar_tick_count: list = field(default_factory=list)
    legend_labels: list = field(default_factory=list)
    hide_map_elements: list = field(default_factory=list)
    time_units: list = field(default_factory=list)
    scale_factor: list = field(default_factory=list)
    axis_grid: list = field(default_factory=list)
    dpi: list = field(default_factory=list)
    colorbar_ticks: list = field(default_factory=list)
    legend_location: list = field(default_factory=list)

    # Generated output names and VTK settings
    vtk_format: list = field(default_factory=list)
    vtk_names: list = field(default_factory=list)
    color_log: list = field(default_factory=list)
    rotation: list = field(default_factory=list)
    filename: list = field(default_factory=list)
    translation: list = field(default_factory=list)
    restart: list = field(default_factory=list)
    aggregation: list = field(default_factory=list)
    distance: list = field(default_factory=list)
    histogram: list = field(default_factory=list)
    xlabel: list = field(default_factory=list)
    xformat: list = field(default_factory=list)
    xtick_count: list = field(default_factory=list)
    xlog: list = field(default_factory=list)
    xlim: list = field(default_factory=list)
    ylabel: list = field(default_factory=list)
    yformat: list = field(default_factory=list)
    ytick_count: list = field(default_factory=list)
    ylog: list = field(default_factory=list)
    ylim: list = field(default_factory=list)

    # Summary data, features, and derived quantities
    vsum: list = field(default_factory=list)
    summary: list = field(default_factory=list)
    time: list = field(default_factory=list)
    wells: list = field(default_factory=list)
    faults: list = field(default_factory=list)
    slice: list = field(default_factory=list)  # Parsed i, j, k selections
    csv_columns: list = field(default_factory=list)
    mass_vars: list = field(default_factory=list)
    summary_mass: list = field(default_factory=list)
    mass_fracs: list = field(default_factory=list)
    caprock_vars: list = field(default_factory=list)
    linewidth_values: list = field(default_factory=list)
    units: list = field(default_factory=list)
    cb_formats: list = field(default_factory=list)
    colormaps: list = field(default_factory=list)
    disc_colormaps: list = field(default_factory=list)
    linestyle: list = field(default_factory=list)
    linewidth: list = field(default_factory=list)
    colors: list = field(default_factory=list)
    colors_default: list = field(default_factory=list)
    linestyle_default: list = field(default_factory=list)
    colorbar_position: tuple[float, float, float, float] = (-1.0, -1.0, -1.0, -1.0)

    # String options and values derived during initialization
    difference_input: str = ""
    colors_raw: str = ""  # Before normalization into colors or colormaps
    output_dir: str = ""
    case: str = ""
    fill_between_style: str = ""
    colorbar_format: str = ""
    fc: str = ""
    inactive_color: str = ""
    mask_variable: str = ""
    suptitle: str = ""
    colorbar_label: str = ""
    slice_mode: str = ""  # min keeps intersections; max keeps exact positions
    xunits: str = ""
    yunits: str = ""
    xunit: str = ""
    yunit: str = ""


@dataclass(slots=True)
class SimData:
    """OPM readers, grid properties, and selected report steps for one case.

    Arrays in global cell order use the full ``nx * ny * nz`` grid. Arrays in
    active-cell order follow the indexing used by INIT and UNRST properties.

    Attributes
    ----------
    init, unrst, grid
        OPM readers for static properties, restart properties, and grid geometry.
    porv
        Pore volume in global cell order; inactive cells are non-positive.
    dx, dy, dz
        Cell dimensions in active-cell order.
    active_pv
        Pore volume in active-cell order.
    active_idx
        Mapping from global cell indices to active-cell indices.
    steps, times
        Selected restart report steps and their simulation times.
    ncells, nsteps
        Total grid-cell and available report-step counts.
    nx, ny, nz
        Grid dimensions along the i, j, and k axes.
    """

    # OPM file readers and grid geometry
    init: OpmFile = None
    unrst: OpmRestart = None
    grid: OpmGrid = None

    # Cell properties and global-to-active mapping
    porv: NDArray = field(default_factory=lambda: np.array([]))
    dx: NDArray = field(default_factory=lambda: np.array([]))
    dy: NDArray = field(default_factory=lambda: np.array([]))
    dz: NDArray = field(default_factory=lambda: np.array([]))
    active_pv: NDArray = field(default_factory=lambda: np.array([]))
    active_idx: NDArray = field(default_factory=lambda: np.array([]))

    # Selected report steps and simulation times
    steps: list = field(default_factory=list)
    times: list = field(default_factory=list)

    # Grid and report-step dimensions
    ncells: int = 0
    nsteps: int = 0
    nx: int = 0
    ny: int = 0
    nz: int = 0
