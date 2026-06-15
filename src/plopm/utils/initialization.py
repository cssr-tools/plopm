# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W0123,R0915,R0912,R1702,R0914,R0916

"""Utiliy functions to set the requiried input values by plopm"""

import os
import sys
import shutil
from typing import cast
import matplotlib
import matplotlib.pyplot as plt
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import ESmry as OpmSummary
from plopm.config.config import ConfigPlopm


def ini_cfg(cmdargs: dict) -> ConfigPlopm:
    """Initialize the configuration dataclass"""

    def find_all_cases(folder: str, suffix: str) -> list[str]:
        folder_path = folder
        if folder_path[0] != ".":
            folder_path = "./" + folder_path
        names_found = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(suffix):
                    names_found.append(os.path.join(root, file)[2 : -len(suffix)])
        return sorted(names_found)

    def find_first_case(folder: str, suffix: str) -> str:
        folder_path = folder
        if folder_path[0] != ".":
            folder_path = "./" + folder_path
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(suffix):
                    return os.path.join(root, file)[2 : -len(suffix)]
        return folder

    cfg = ConfigPlopm()
    cfg.output = os.path.abspath(cmdargs["output"])
    names = cmdargs["input"].split("  ")
    names = [var.split(" ") for var in names]
    cfg.namens = names
    for name in ["gif", "csv", "png", "vtk"]:
        setattr(cfg, name, cmdargs["mode"] == name)
    cfg.diff = cmdargs["diff"]
    cfg.ensemble = int(cmdargs["ensemble"])
    if cfg.diff:
        if cfg.diff[-1] in [".", "/"]:
            cfg.diff = find_first_case(cfg.diff, ".EGRID")
        if names[0][0][-1] in [".", "/"]:
            names[0][0] = find_first_case(names[0][0], ".EGRID")
    elif names[0][0][-1] in [".", "/"]:
        folders = names[0]
        names = []
        for index, folder in enumerate(folders):
            if cfg.ensemble > 0 or index == 0:
                names.append([])
            if cfg.vtk:
                names[-1] = find_all_cases(folder, ".DATA")
            else:
                names[-1] = find_all_cases(folder, ".SMSPEC")
    cfg.names = names
    cfg.name = names[0][0]
    cfg.vrs = cmdargs["variable"].lower().split(",")
    handle_blocks(cfg)
    cfg.stress = float(cmdargs["stress"])
    for name in ["vtknames", "save"]:
        setattr(cfg, name, cmdargs[name].split("  "))
    cfg.mass = ["gasm", "dism", "liqm", "vapm", "co2m", "h2om"]
    cfg.xmass = ["xco2l", "xh2ov", "xco2v", "xh2ol"]
    cfg.caprock = ["limipres", "overpres", "objepres"]
    for name in ["filter", "restart", "adjust", "vtkformat"]:
        setattr(cfg, name, cmdargs[name].split(","))
    if cfg.restart[0] == "-1":
        cfg.restart = [-1]
    elif ":" in cfg.restart[0]:
        cfg.rst_range = True
        vals = cfg.restart[0].split(":")
        if len(vals) == 3:
            cfg.restart = list(range(int(vals[0]), int(vals[1]) + 1, int(vals[2])))
        else:
            cfg.restart = list(range(int(vals[0]), int(vals[1]) + 1))
        if cfg.save[0]:
            width = len(str(cfg.restart[-1]))
            cfg.save = [
                cfg.save[0] + f"{restart_value}".zfill(width)
                for restart_value in cfg.restart
            ]
    else:
        if "," in cmdargs["restart"] and (cfg.png or cfg.csv):
            cfg.rst_range = True
            width = len(str(cfg.restart[-1]))
            cfg.save = [
                cfg.save[0] + f"{restart_value}".zfill(width)
                for restart_value in cfg.restart
            ]
        cfg.restart = [int(restart_value) for restart_value in cfg.restart]
    for name in ["vtkformat", "adjust", "vtknames"]:
        if len(getattr(cfg, name)) < len(cfg.vrs):
            setattr(cfg, name, [getattr(cfg, name)[0]] * len(cfg.vrs))
    if not os.path.exists(cfg.output):
        os.makedirs(cfg.output, exist_ok=True)
    if cfg.vtk:
        return cfg
    cfg.csvs = cmdargs["csv"].split(";")
    cfg.csvs = [[int(val) if val else "" for val in var.split(",")] for var in cfg.csvs]
    allcsvs = True
    for val in cfg.csvs:
        if not val[0]:
            allcsvs = False
        else:
            if len(val) == 2:
                cfg.csvsummary = True
    if allcsvs:
        cfg.vrs = ["csv"]
    max_count = max(len(cfg.names[0]), len(cfg.vrs))
    if len(cfg.csvs) == 1 and not cfg.csvs[0][0]:
        cfg.csvs = [cfg.csvs[0]] * (max_count + 1)
    for name in ["mask", "lw", "linestyle", "ncolor"]:
        setattr(cfg, name, cmdargs[name].lower())
    for name in ["size", "maskthr", "interval"]:
        setattr(cfg, name, float(cmdargs[name]))
    for name in ["cticks", "title"]:
        setattr(cfg, name, cmdargs[name].split("  "))
    for name in ["bounds", "translate", "histogram"]:
        setattr(cfg, name, cmdargs[name].split(" "))
    for name in [
        "suptitle",
        "bandprop",
        "clabel",
    ]:
        setattr(cfg, name, cmdargs[name])
    cfg.bounds = [var.split(",") for var in cfg.bounds]
    cfg.translate = [var.split(",") for var in cfg.translate]
    cfg.colors_raw = cmdargs["colors"]
    cfg.cf = cmdargs["cformat"]
    cfg.fc = cmdargs["facecolor"]
    cfg.labels = cmdargs["labels"].split("   ")
    cfg.labels = [var.split("  ") for var in cfg.labels]
    cfg.rm = [int(val) for val in cmdargs["remove"].split(",")]
    cfg.global_ = int(cmdargs["global"]) == 1
    for name in ["scale", "delax", "loop", "printv"]:
        setattr(cfg, name, int(cmdargs[name]) == 1)
    for name in [
        "dimensions",
        "distance",
        "how",
        "rotate",
        "log",
        "loc",
        "axgrid",
    ]:
        setattr(cfg, name, cmdargs[name].split(","))
    for name in ["dpi", "tunits", "cnum", "grid"]:
        setattr(cfg, name, cmdargs[name].split(","))
    for name in ["dual", "subfigs", "vmin", "vmax"]:
        setattr(cfg, name, cmdargs[name].split(","))
    for axis_name in ["x", "y"]:
        setattr(cfg, f"{axis_name}units", cmdargs[f"{axis_name}units"])
        setattr(cfg, f"{axis_name}label", cmdargs[f"{axis_name}label"].split("  "))
        setattr(cfg, f"{axis_name}format", cmdargs[f"{axis_name}format"].split(","))
        setattr(cfg, f"{axis_name}lnum", cmdargs[f"{axis_name}lnum"].split(","))
        setattr(cfg, f"{axis_name}log", cmdargs[f"{axis_name}log"].split(","))
        setattr(cfg, f"{axis_name}lim", cmdargs[f"{axis_name}lim"].split(" "))
        setattr(
            cfg,
            f"{axis_name}lim",
            [var.split(",") for var in getattr(cfg, f"{axis_name}lim")],
        )
    if cmdargs["clogthks"]:
        cfg.clogthks = [float(val) for val in cmdargs["clogthks"][1:-1].split(",")]
    if cfg.cticks[0]:
        for index, values in enumerate(cfg.cticks):
            cfg.cticks[index] = [val.strip() for val in values[1:-1].split(",")]
    if cmdargs["cbsfax"] != "empty":
        cfg.cbsfax = cast(
            tuple[float, float, float, float],
            tuple(map(float, cmdargs["cbsfax"].split(","))),
        )
    cfg.slide = cmdargs["slide"].split(" ")
    cfg.slide = [
        [val if val else [-2, -2] for val in var.split(",")] for var in cfg.slide
    ]
    if [-2, -2] in cfg.slide[0]:
        for slide_index, var in enumerate(cfg.slide):
            for value_index, val in enumerate(var):
                if val[0] != -2:
                    if val == ":":
                        pass
                    elif ":" in val:
                        vals = val.split(":")
                        cfg.slide[slide_index][value_index] = [
                            int(vals[0]) - 1,
                            int(vals[1]),
                        ]
                    else:
                        int_value = int(val)
                        cfg.slide[slide_index][value_index] = [int_value - 1, int_value]
    elif ":" in cfg.slide[0]:
        cfg.layer = True
        for slide_index, var in enumerate(cfg.slide):
            for value_index, val in enumerate(var):
                if val != ":":
                    cfg.slide[slide_index][value_index] = int(val) - 1
                else:
                    cfg.slide[slide_index][value_index] = -1
    else:
        cfg.sensor = True
        for slide_index, var in enumerate(cfg.slide):
            for value_index, val in enumerate(var):
                cfg.slide[slide_index][value_index] = int(val) - 1

    cfg.smass = ["fwcdm", "fgipm"]

    cfg.colors_default = [
        "k",
        "b",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
        "#1f77b4",
        "r",
    ]

    cfg.linestyle_default = [
        "-",
        "--",
        (0, (1, 1)),
        "-.",
        (0, (1, 10)),
        (0, (1, 1)),
        (5, (10, 3)),
        (0, (5, 10)),
        (0, (5, 5)),
        (0, (5, 1)),
        (0, (3, 10, 1, 10)),
        (0, (3, 5, 1, 5)),
        (0, (3, 1, 1, 1)),
        (0, (3, 5, 1, 5, 1, 5)),
        (0, (3, 10, 1, 10, 1, 10)),
        (0, (3, 1, 1, 1, 1, 1)),
        (0, ()),
    ]
    for val in cfg.vrs:
        for oper in ["=", "<", ">"]:
            if oper in val:
                cfg.discrete = False

    cfg.lw_values = ["1"] * len(cfg.names[0])

    font = {"family": "normal", "weight": "normal", "size": cfg.size}
    matplotlib.rc("font", **font)
    plt.rcParams.update(
        {
            "text.usetex": shutil.which("latex") is not None,
            "font.family": "monospace",
            "legend.columnspacing": 0.9,
            "legend.handlelength": 3.5,
            "legend.fontsize": cfg.size,
            "lines.linewidth": 4,
            "axes.titlesize": cfg.size,
            "axes.grid": False,
            "figure.figsize": (float(cfg.dimensions[0]), float(cfg.dimensions[1])),
        }
    )

    if len(cfg.save) < len(cfg.vrs):
        cfg.save = [cfg.save[0]] * len(cfg.vrs)

    if len(cfg.bounds) < len(cfg.vrs):
        cfg.bounds = [cfg.bounds[0]] * len(cfg.vrs)

    if cfg.diff and len(cfg.rotate) < 2:
        cfg.rotate = [cfg.rotate[0]] * 2
    elif len(cfg.rotate) < len(cfg.names[0]):
        cfg.rotate = [cfg.rotate[0]] * len(cfg.names[0])

    if cfg.diff and len(cfg.translate) < 2:
        cfg.translate = [cfg.translate[0]] * 2

    if len(cfg.translate) < len(cfg.names[0]):
        cfg.translate = [cfg.translate[0]] * len(cfg.names[0])

    if cfg.diff and len(cfg.slide) < 2:
        cfg.slide = [cfg.slide[0]] * 2

    for val in ["how", "filter", "cticks", "csvs", "dual", "slide", "title"]:
        if len(getattr(cfg, val)) < max_count:
            setattr(cfg, val, [getattr(cfg, val)[0]] * max_count)
        elif len(cfg.restart) > 1 and cfg.subfigs[0]:
            setattr(cfg, val, [getattr(cfg, val)[0]] * len(cfg.restart))

    if len(cfg.restart) > 1 and cfg.subfigs[0]:
        cfg.save = [cmdargs["save"]]

    if cfg.diff:
        cfg.how = [cfg.how[0]] * 2
        cfg.filter = [cfg.filter[0]] * 2

    for val in [
        "xformat",
        "yformat",
        "xlog",
        "ylog",
        "xlabel",
        "ylabel",
        "labels",
        "tunits",
        "loc",
        "dpi",
        "ylnum",
        "xlnum",
        "save",
        "axgrid",
        "cnum",
        "log",
        "vmin",
        "vmax",
    ]:
        if len(getattr(cfg, val)) < len(cfg.vrs):
            setattr(cfg, val, [getattr(cfg, val)[0]] * len(cfg.vrs))

    return cfg


def handle_blocks(cfg: ConfigPlopm) -> None:
    """For block i,j,k quantities, do not split the commas"""
    vrs_in = cfg.vrs
    count = len(vrs_in)
    vrs = []
    index = 0
    while index < count:
        if index < count - 2 and ":" in vrs_in[index] and vrs_in[index + 1].isnumeric():
            vrs.append(
                vrs_in[index] + "," + vrs_in[index + 1] + "," + vrs_in[index + 2]
            )
            index += 3
        else:
            vrs.append(vrs_in[index])
            index += 1
    cfg.vrs = vrs


def ini_properties(cfg: ConfigPlopm) -> None:
    """Define the properties to plot"""
    cfg.units = [" [-]", " [mD]", " [mD]", r" [m$^3$]", " [-]", " [-]"]
    cfg.cformat = [".1f", ".0f", ".0f", ".2e", ".0f", ".0f"]
    cfg.cmaps = ["jet", "turbo", "turbo", "terrain", "tab20b", "tab20b"]
    cmdisc = [
        "Pastel1",
        "Pastel2",
        "Paired",
        "Accent",
        "Dark2",
        "Set1",
        "Set2",
        "Set3",
        "tab10",
        "tab20",
        "tab20b",
        "tab20c",
        "cet_glasbey_bw",
        "cet_glasbey",
        "cet_glasbey_cool",
        "cet_glasbey_warm",
        "cet_glasbey_dark",
        "cet_glasbey_light",
        "cet_glasbey_category10",
        "cet_glasbey_hv",
    ]
    cfg.cmdisc = [cmap + "_r" for cmap in cmdisc] + cmdisc
    if cfg.colors_raw:
        cfg.cmaps = cfg.colors_raw.split(",")
    elif cfg.diff:
        cfg.cmaps = ["RdYlGn"]
    elif cfg.mask:
        cfg.cmaps = ["RdGy_r"]
    vrs = cfg.vrs
    if vrs:
        first_var = vrs[0]
        if first_var in ["wells", "faults"]:
            if cfg.how[0]:
                if cfg.how[0] not in ["min", "max"]:
                    print(f"Unsuported value -how '{cfg.how[0]}' for wells/faults.")
                    print("Supported values are 'min' and 'max'.")
                    sys.exit()
                cfg.whow = cfg.how[0]
            else:
                cfg.whow = "min"
            if not cfg.colors_raw:
                cfg.units = [" [-]"]
                cfg.cmaps = ["nipy_spectral"]
                cfg.cformat = [".0f"]
        if "num" in first_var and not cfg.mask and not cfg.diff and not cfg.colors_raw:
            cfg.cmaps = ["tab20"]
            cfg.units = [" [-]"]
            cfg.cformat = [".0f"]
        if "index" in first_var:
            cfg.units = [" [-]"]
            cfg.cformat = [".0f"]
    if cfg.cf:
        cfg.cformat = cfg.cf.split(",")
    elif len(vrs) == 1 and "num" in vrs[0]:
        cfg.cformat = [".0f"]
    elif cfg.diff:
        cfg.cformat = [".1e"]
    num_vars = len(vrs)
    if len(cfg.cmaps) < num_vars or (
        num_vars == len(cfg.names[0]) and len(cfg.names[0]) > 1 and not cfg.colors_raw
    ):
        cfg.cmaps = [cfg.cmaps[0]] * num_vars
    if len(cfg.xlim) < num_vars:
        cfg.xlim = [cfg.xlim[0]] * num_vars
    if len(cfg.ylim) < num_vars:
        cfg.ylim = [cfg.ylim[0]] * num_vars
    if len(cfg.cformat) < num_vars:
        cfg.cformat = [cfg.cformat[0]] * num_vars
    cfg.xskl, cfg.xunit = initialize_spatial(cfg.xunits)
    cfg.yskl, cfg.yunit = initialize_spatial(cfg.yunits)


def initialize_spatial(unit: str) -> tuple[float, str]:
    """Handle the units for the axis in the spatial maps"""
    return {
        "m": (1.0, " [m]"),
        "km": (1e-3, " [km]"),
        "cm": (1e2, " [cm]"),
        "mm": (1e3, " [mm]"),
    }.get(unit, (1.0, ""))


def initialize_mass(mskl: float) -> str:
    """Initialize the mass properties according to the given variable"""
    return {
        1e-3: " [t]",
        1e-6: " [Kt]",
        1e-9: " [Mt]",
        1e3: " [g]",
        1e6: " [mg]",
        1: " [kg]",
    }.get(mskl, "")


def is_summary(cfg: ConfigPlopm) -> bool:
    """Check flag arguments and files for summary plot"""
    name = cfg.name
    vrs = cfg.vrs
    first_var = vrs[0] if vrs else ""
    ntot = 0
    if cfg.printv:
        for ext, what in (("init", "init"), ("unrst", "restart")):
            file = f"{name}.{ext.upper()}"
            if os.path.isfile(file):
                reader = OpmFile(file)
                keys = [
                    var[0]
                    for var in reader.arrays
                    if var[0]
                    not in ["INTEHEAD", "LOGIHEAD", "DOUBHEAD", "TABDIMS", "TAB"]
                ]
                if ext == "unrst":
                    ntot = reader.count("PRESSURE")
                print(f"The {what} available variables for {name} are:")
                print(keys)
                if ext == "unrst":
                    print(f"The available restarts for {name} are:")
                    print(list(range(ntot)))
    if cfg.sensor or cfg.layer or cfg.distance[0] or cfg.histogram[0] or cfg.csvsummary:
        return True
    if (
        first_var[:3] in ["krw", "krg"]
        or first_var[:4] in ["krow", "krog", "pcow", "pcog", "pcwg"]
        or first_var[:6] == "pcfact"
    ):
        return True
    smspec_file = f"{name}.SMSPEC"
    if os.path.isfile(smspec_file):
        summary = OpmSummary(smspec_file).keys()
        if cfg.printv:
            print(f"The summary available variables for {name} are:")
            print(summary)
            sys.exit(0)
        smass = cfg.smass
        for name_v in vrs:
            base = name_v.split(" ")[0].upper()
            if base in summary or base.lower() in smass:
                return True
    if cfg.printv:
        sys.exit(0)
    return False


def ini_summary(cfg: ConfigPlopm) -> None:
    """Initialize the needed objects for the summary plots"""
    vrs = cfg.vrs
    nv = len(vrs)
    cfg.numc = 1 if len(cfg.names) < nv else nv
    for val in ["colors_raw", "linestyle", "lw"]:
        if getattr(cfg, val):
            tmp = [var.split(",") for var in getattr(cfg, val).split(":")]
            if len(tmp) < nv:
                tmp = [tmp[0]] * nv
            setattr(cfg, "colors" if val == "colors_raw" else val, tmp)
        elif val == "colors_raw":
            cfg.colors = [cfg.colors_default] * nv
        elif val == "linestyle":
            cfg.linestyle = [cfg.linestyle_default] * nv
        else:
            cfg.lw = [cfg.lw_values] * nv
    for axis_name in ["x", "y"]:
        key = f"{axis_name}lim"
        if len(getattr(cfg, key)) < nv and getattr(cfg, key)[0]:
            setattr(cfg, key, [getattr(cfg, key)[0]] * nv)
    if nv == 1 and len(cfg.lw[0]) < len(cfg.names[0]):
        cfg.lw[0] = [cfg.lw[0][0]] * len(cfg.names[0])
    for val in [
        "names",
        "title",
        "xformat",
        "yformat",
        "xlog",
        "ylog",
        "xlabel",
        "ylabel",
        "labels",
        "tunits",
        "loc",
        "dpi",
        "ylnum",
        "xlnum",
        "adjust",
        "save",
        "axgrid",
    ]:
        if len(getattr(cfg, val)) < nv:
            setattr(cfg, val, [getattr(cfg, val)[0]] * nv)
