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
    scale: bool = False
    delax: bool = False
    printv: bool = False
    loop: bool = False
    global_: bool = False
    rst_range: bool = False
    sensor: bool = False
    layer: bool = False
    csvsummary: bool = False
    discrete: bool = True
    size: float = 0.0
    maskthr: float = 0.0
    interval: float = 0.0
    stress: float = 0.0
    xskl: float = 1.0
    yskl: float = 1.0
    ensemble: int = 0
    numc: int = 1
    clogthks: list = field(default_factory=list)
    namens: list = field(default_factory=list)
    names: list = field(default_factory=list)
    dual: list = field(default_factory=list)
    subfigs: list = field(default_factory=list)
    vrs: list = field(default_factory=list)
    filter: list = field(default_factory=list)
    title: list = field(default_factory=list)
    bounds: list = field(default_factory=list)
    dimensions: list = field(default_factory=list)
    vmin: list = field(default_factory=list)
    vmax: list = field(default_factory=list)
    grid: list = field(default_factory=list)
    cnum: list = field(default_factory=list)
    labels: list = field(default_factory=list)
    rm: list = field(default_factory=list)
    tunits: list = field(default_factory=list)
    adjust: list = field(default_factory=list)
    axgrid: list = field(default_factory=list)
    dpi: list = field(default_factory=list)
    cticks: list = field(default_factory=list)
    loc: list = field(default_factory=list)
    vtkformat: list = field(default_factory=list)
    vtknames: list = field(default_factory=list)
    log: list = field(default_factory=list)
    rotate: list = field(default_factory=list)
    save: list = field(default_factory=list)
    translate: list = field(default_factory=list)
    restart: list = field(default_factory=list)
    how: list = field(default_factory=list)
    distance: list = field(default_factory=list)
    histogram: list = field(default_factory=list)
    xlabel: list = field(default_factory=list)
    xformat: list = field(default_factory=list)
    xlnum: list = field(default_factory=list)
    xlog: list = field(default_factory=list)
    xlim: list = field(default_factory=list)
    ylabel: list = field(default_factory=list)
    yformat: list = field(default_factory=list)
    ylnum: list = field(default_factory=list)
    ylog: list = field(default_factory=list)
    ylim: list = field(default_factory=list)
    vsum: list = field(default_factory=list)
    summary: list = field(default_factory=list)
    time: list = field(default_factory=list)
    wells: list = field(default_factory=list)
    faults: list = field(default_factory=list)
    slide: list = field(default_factory=list)
    csvs: list = field(default_factory=list)
    mass: list = field(default_factory=list)
    smass: list = field(default_factory=list)
    xmass: list = field(default_factory=list)
    caprock: list = field(default_factory=list)
    lw_values: list = field(default_factory=list)
    units: list = field(default_factory=list)
    cformat: list = field(default_factory=list)
    cmaps: list = field(default_factory=list)
    cmdisc: list = field(default_factory=list)
    linestyle: list = field(default_factory=list)
    lw: list = field(default_factory=list)
    colors: list = field(default_factory=list)
    colors_default: list = field(default_factory=list)
    linestyle_default: list = field(default_factory=list)
    cbsfax: tuple[float, float, float, float] = (-1.0, -1.0, -1.0, -1.0)
    diff: str = ""
    colors_raw: str = ""
    output: str = ""
    name: str = ""
    bandprop: str = ""
    cf: str = ""
    fc: str = ""
    ncolor: str = ""
    mask: str = ""
    suptitle: str = ""
    clabel: str = ""
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
    restart: list = field(default_factory=lambda: [])
    tnrst: list = field(default_factory=lambda: [])
    nxyz: int = 0
    ntot: int = 0
    nx: int = 0
    ny: int = 0
    nz: int = 0
