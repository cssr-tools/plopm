# SPDX-FileCopyrightText: 2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0902

"""Central configuration structures for plopm"""

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import EGrid as OpmGrid
from opm.io.ecl import ERst as OpmRestart


@dataclass(slots=True)
class ConfigPlopm:
    """Plopm dataclass"""

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
    rst_range: bool = False
    sensor: bool = False
    layer: bool = False
    csv_column_summary: bool = False
    discrete: bool = True
    fontsize: float = 0.0
    mask_threshold: float = 0.0
    gif_interval: float = 0.0
    stress_coefficient: float = 0.0
    xskl: float = 1.0
    yskl: float = 1.0
    ensemble: int = 0
    numc: int = 1
    color_log_ticks: list = field(default_factory=list)
    namens: list = field(default_factory=list)
    names: list = field(default_factory=list)
    dual_grid: list = field(default_factory=list)
    subplot_grid: list = field(default_factory=list)
    vrs: list = field(default_factory=list)
    filter: list = field(default_factory=list)
    title: list = field(default_factory=list)
    clim: list = field(default_factory=list)
    figsize: list = field(default_factory=list)
    min_threshold: list = field(default_factory=list)
    max_threshold: list = field(default_factory=list)
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
    vsum: list = field(default_factory=list)
    summary: list = field(default_factory=list)
    time: list = field(default_factory=list)
    wells: list = field(default_factory=list)
    faults: list = field(default_factory=list)
    slice: list = field(default_factory=list)
    csv_columns: list = field(default_factory=list)
    mass: list = field(default_factory=list)
    smass: list = field(default_factory=list)
    xmass: list = field(default_factory=list)
    caprock: list = field(default_factory=list)
    linewidth_values: list = field(default_factory=list)
    units: list = field(default_factory=list)
    cb_format: list = field(default_factory=list)
    cmaps: list = field(default_factory=list)
    cmdisc: list = field(default_factory=list)
    linestyle: list = field(default_factory=list)
    linewidth: list = field(default_factory=list)
    colors: list = field(default_factory=list)
    colors_default: list = field(default_factory=list)
    linestyle_default: list = field(default_factory=list)
    colorbar_position: tuple[float, float, float, float] = (-1.0, -1.0, -1.0, -1.0)
    difference_input: str = ""
    colors_raw: str = ""
    output_dir: str = ""
    name: str = ""
    fill_between_style: str = ""
    colorbar_format: str = ""
    fc: str = ""
    inactive_color: str = ""
    mask_variable: str = ""
    suptitle: str = ""
    colorbar_label: str = ""
    whow: str = ""
    xunits: str = ""
    yunits: str = ""
    xunit: str = ""
    yunit: str = ""


@dataclass(slots=True)
class ReadData:
    """Reading the OPM output files"""

    init: OpmFile = None
    unrst: OpmRestart = None
    egrid: OpmGrid = None
    porv: NDArray = field(default_factory=lambda: np.array([]))
    dx: NDArray = field(default_factory=lambda: np.array([]))
    dy: NDArray = field(default_factory=lambda: np.array([]))
    dz: NDArray = field(default_factory=lambda: np.array([]))
    pv: NDArray = field(default_factory=lambda: np.array([]))
    actind: NDArray = field(default_factory=lambda: np.array([]))
    restart: list = field(default_factory=list)
    tnrst: list = field(default_factory=list)
    nxyz: int = 0
    ntot: int = 0
    nx: int = 0
    ny: int = 0
    nz: int = 0
