# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W0123,R0915,R0912,R1702,R0914,R0916

"""Utility functions to set the requiried input values by plopm"""

import argparse
import copy
import os
import shutil
import sys
from typing import cast

import matplotlib
import matplotlib.pyplot as plt
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import ESmry as OpmSummary

from plopm.config.config import ConfigPlopm
from plopm.utils.terminal import (
    cli_current_value,
    cli_error_value,
    cli_info_value,
    plopm_error,
    plopm_info,
)


def ini_cfg(cmdargs: argparse.Namespace) -> ConfigPlopm:
    """Initialize the configuration dataclass."""

    def find_all_cases(folder: str, suffix: str) -> list:
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
    cfg.output_dir = os.path.abspath(cmdargs.output_dir)
    names = cmdargs.input.split("  ")
    names = [var.split(" ") for var in names]
    cfg.namens = names

    for name in ["gif", "csv", "png", "vtk"]:
        setattr(cfg, name, cmdargs.format == name)

    cfg.difference_input = cmdargs.difference_input
    cfg.ensemble = int(cmdargs.ensemble)

    if cfg.difference_input:
        if cfg.difference_input[-1] in [".", "/"]:
            cfg.difference_input = find_first_case(cfg.difference_input, ".EGRID")
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
    cfg.vrs = cmdargs.variable.lower().split(",")
    handle_blocks(cfg)
    cfg.stress_coefficient = float(cmdargs.stress_coefficient)

    for cfg_name, cmdarg_name in [
        ("vtk_names", "vtk_names"),
        ("filename", "filename"),
    ]:
        setattr(cfg, cfg_name, getattr(cmdargs, cmdarg_name).split("  "))

    cfg.mass = ["gasm", "dism", "liqm", "vapm", "co2m", "h2om"]
    cfg.xmass = ["xco2l", "xh2ov", "xco2v", "xh2ol"]
    cfg.caprock = ["limipres", "overpres", "objepres"]
    for cfg_name, cmdarg_name in [
        ("filter", "filter"),
        ("restart", "restart"),
        ("scale_factor", "scale_factor"),
        ("vtk_format", "vtk_format"),
    ]:
        setattr(cfg, cfg_name, getattr(cmdargs, cmdarg_name).split(","))

    if cfg.restart[0] == "-1":
        cfg.restart = [-1]
    elif ":" in cfg.restart[0]:
        cfg.rst_range = True
        vals = cfg.restart[0].split(":")
        if len(vals) == 3:
            cfg.restart = list(
                range(
                    int(vals[0]),
                    int(vals[1]) + 1,
                    int(vals[2]),
                )
            )
        else:
            cfg.restart = list(
                range(
                    int(vals[0]),
                    int(vals[1]) + 1,
                )
            )
        if cfg.filename[0]:
            width = len(str(cfg.restart[-1]))
            cfg.filename = [
                cfg.filename[0] + f"{restart_value}".zfill(width)
                for restart_value in cfg.restart
            ]
    else:
        if "," in cmdargs.restart and (cfg.png or cfg.csv):
            cfg.rst_range = True
            width = len(str(cfg.restart[-1]))
            cfg.filename = [
                cfg.filename[0] + f"{restart_value}".zfill(width)
                for restart_value in cfg.restart
            ]
        cfg.restart = [int(restart_value) for restart_value in cfg.restart]
    for name in ["vtk_format", "scale_factor", "vtk_names"]:
        if len(getattr(cfg, name)) < len(cfg.vrs):
            setattr(
                cfg,
                name,
                [getattr(cfg, name)[0]] * len(cfg.vrs),
            )
    if not os.path.exists(cfg.output_dir):
        os.makedirs(cfg.output_dir, exist_ok=True)
    if cfg.vtk:
        return cfg

    cfg.csv_columns = cmdargs.csv_columns.split(";")
    cfg.csv_columns = [
        [int(val) if val else "" for val in var.split(",")] for var in cfg.csv_columns
    ]

    allcsvs = True
    for val in cfg.csv_columns:
        if not val[0]:
            allcsvs = False
        elif len(val) == 2:
            cfg.csv_column_summary = True

    if allcsvs:
        cfg.vrs = ["csv"]

    max_count = max(len(cfg.names[0]), len(cfg.vrs))
    if len(cfg.csv_columns) == 1 and not cfg.csv_columns[0][0]:
        cfg.csv_columns = [cfg.csv_columns[0]] * (max_count + 1)

    for cfg_name, cmdarg_name in [
        ("mask_variable", "mask_variable"),
        ("linewidth", "linewidth"),
        ("linestyle", "linestyle"),
        ("inactive_color", "inactive_color"),
    ]:
        setattr(cfg, cfg_name, getattr(cmdargs, cmdarg_name).lower())

    for cfg_name, cmdarg_name in [
        ("fontsize", "fontsize"),
        ("mask_threshold", "mask_threshold"),
        ("gif_interval", "gif_interval"),
    ]:
        setattr(cfg, cfg_name, float(getattr(cmdargs, cmdarg_name)))

    for cfg_name, cmdarg_name in [
        ("colorbar_ticks", "colorbar_ticks"),
        ("title", "title"),
    ]:
        setattr(cfg, cfg_name, getattr(cmdargs, cmdarg_name).split("  "))

    for cfg_name, cmdarg_name in [
        ("clim", "clim"),
        ("translation", "translation"),
        ("histogram", "histogram"),
    ]:
        setattr(cfg, cfg_name, getattr(cmdargs, cmdarg_name).split(" "))

    for cfg_name, cmdarg_name in [
        ("suptitle", "suptitle"),
        ("fill_between_style", "fill_between_style"),
        ("colorbar_label", "colorbar_label"),
    ]:
        setattr(cfg, cfg_name, getattr(cmdargs, cmdarg_name))

    cfg.clim = [var.split(",") for var in cfg.clim]
    cfg.translation = [var.split(",") for var in cfg.translation]
    cfg.colors_raw = cmdargs.colors
    cfg.colorbar_format = cmdargs.colorbar_format
    cfg.fc = cmdargs.facecolor
    cfg.legend_labels = cmdargs.legend_labels.split("   ")
    cfg.legend_labels = [var.split("  ") for var in cfg.legend_labels]
    cfg.hide_map_elements = [int(val) for val in cmdargs.hide_map_elements.split(",")]
    cfg.global_range = int(cmdargs.global_range) == 1

    for cfg_name, cmdarg_name in [
        ("equal_aspect", "equal_aspect"),
        ("remove_duplicate_labels", "remove_duplicate_labels"),
        ("gif_loop", "gif_loop"),
        ("list_variables", "list_variables"),
        ("step_plot", "step_plot"),
    ]:
        setattr(cfg, cfg_name, int(getattr(cmdargs, cmdarg_name)) == 1)

    for cfg_name, cmdarg_name in [
        ("figsize", "figsize"),
        ("distance", "distance"),
        ("aggregation", "aggregation"),
        ("rotation", "rotation"),
        ("color_log", "color_log"),
        ("legend_location", "legend_location"),
        ("axis_grid", "axis_grid"),
    ]:
        setattr(cfg, cfg_name, getattr(cmdargs, cmdarg_name).split(","))

    for cfg_name, cmdarg_name in [
        ("dpi", "dpi"),
        ("time_units", "time_units"),
        ("colorbar_tick_count", "colorbar_tick_count"),
        ("grid_edges", "grid_edges"),
    ]:
        setattr(cfg, cfg_name, getattr(cmdargs, cmdarg_name).split(","))

    for cfg_name, cmdarg_name in [
        ("dual_grid", "dual_grid"),
        ("subplot_grid", "subplot_grid"),
        ("min_threshold", "min_threshold"),
        ("max_threshold", "max_threshold"),
    ]:
        setattr(cfg, cfg_name, getattr(cmdargs, cmdarg_name).split(","))

    for axis_name in ["x", "y"]:
        setattr(
            cfg,
            f"{axis_name}units",
            getattr(cmdargs, f"{axis_name}units"),
        )
        setattr(
            cfg,
            f"{axis_name}label",
            getattr(cmdargs, f"{axis_name}label").split("  "),
        )
        setattr(
            cfg,
            f"{axis_name}format",
            getattr(cmdargs, f"{axis_name}format").split(","),
        )
        setattr(
            cfg,
            f"{axis_name}tick_count",
            getattr(cmdargs, f"{axis_name}tick_count").split(","),
        )
        setattr(
            cfg,
            f"{axis_name}log",
            getattr(cmdargs, f"{axis_name}log").split(","),
        )
        setattr(
            cfg,
            f"{axis_name}lim",
            getattr(cmdargs, f"{axis_name}lim").split(" "),
        )
        setattr(
            cfg,
            f"{axis_name}lim",
            [var.split(",") for var in getattr(cfg, f"{axis_name}lim")],
        )

    if cmdargs.color_log_ticks:
        cfg.color_log_ticks = [
            float(val) for val in cmdargs.color_log_ticks[1:-1].split(",")
        ]

    if cfg.colorbar_ticks[0]:
        for index, values in enumerate(cfg.colorbar_ticks):
            cfg.colorbar_ticks[index] = [val.strip() for val in values[1:-1].split(",")]
    if cmdargs.colorbar_position != "empty":
        cfg.colorbar_position = cast(
            tuple[float, float, float, float],
            tuple(map(float, cmdargs.colorbar_position.split(","))),
        )

    cfg.slice = cmdargs.slice.split(" ")
    cfg.slice = [
        [val if val else [-2, -2] for val in var.split(",")] for var in cfg.slice
    ]
    if [-2, -2] in cfg.slice[0]:
        for slice_index, var in enumerate(cfg.slice):
            for value_index, val in enumerate(var):
                if val[0] != -2:
                    if val == ":":
                        pass
                    elif ":" in val:
                        vals = val.split(":")
                        cfg.slice[slice_index][value_index] = [
                            int(vals[0]) - 1,
                            int(vals[1]),
                        ]
                    else:
                        int_value = int(val)
                        cfg.slice[slice_index][value_index] = [int_value - 1, int_value]
    elif ":" in cfg.slice[0]:
        cfg.layer = True
        for slice_index, var in enumerate(cfg.slice):
            for value_index, val in enumerate(var):
                if val != ":":
                    cfg.slice[slice_index][value_index] = int(val) - 1
                else:
                    cfg.slice[slice_index][value_index] = -1
    else:
        cfg.sensor = True
        for slice_index, var in enumerate(cfg.slice):
            for value_index, val in enumerate(var):
                cfg.slice[slice_index][value_index] = int(val) - 1

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

    cfg.linewidth_values = ["1"] * len(cfg.names[0])

    font = {"family": "normal", "weight": "normal", "size": cfg.fontsize}
    matplotlib.rc("font", **font)
    plt.rcParams.update(
        {
            "text.usetex": shutil.which("latex") is not None,
            "font.family": "monospace",
            "legend.columnspacing": 0.9,
            "legend.handlelength": 3.5,
            "legend.fontsize": cfg.fontsize,
            "lines.linewidth": 4,
            "axes.titlesize": cfg.fontsize,
            "axes.grid": False,
            "figure.figsize": (float(cfg.figsize[0]), float(cfg.figsize[1])),
        }
    )

    if len(cfg.filename) < len(cfg.vrs):
        cfg.filename = [cfg.filename[0]] * len(cfg.vrs)

    if len(cfg.clim) < len(cfg.vrs):
        cfg.clim = [cfg.clim[0]] * len(cfg.vrs)

    if cfg.difference_input and len(cfg.rotation) < 2:
        cfg.rotation = [cfg.rotation[0]] * 2
    elif len(cfg.rotation) < len(cfg.names[0]):
        cfg.rotation = [cfg.rotation[0]] * len(cfg.names[0])

    if cfg.difference_input and len(cfg.translation) < 2:
        cfg.translation = [cfg.translation[0]] * 2

    if len(cfg.translation) < len(cfg.names[0]):
        cfg.translation = [cfg.translation[0]] * len(cfg.names[0])

    if cfg.difference_input and len(cfg.slice) < 2:
        cfg.slice = [cfg.slice[0]] * 2

    for val in [
        "aggregation",
        "filter",
        "colorbar_ticks",
        "csv_columns",
        "dual_grid",
        "slice",
        "title",
    ]:
        if len(getattr(cfg, val)) < max_count:
            if val == "slice":
                current = getattr(cfg, val)
                setattr(
                    cfg,
                    val,
                    [copy.deepcopy(current[0]) for _ in range(max_count)],
                )
            else:
                setattr(cfg, val, [getattr(cfg, val)[0]] * max_count)
        elif len(cfg.restart) > 1 and cfg.subplot_grid[0]:
            if (
                len(getattr(cfg, val)) >= max(max_count, len(cfg.restart))
                and val == "title"
            ):
                continue
            if val == "slice":
                if cfg.gif and len(cfg.slice) >= len(cfg.names[0]):
                    continue
                current = getattr(cfg, val)
                setattr(
                    cfg,
                    val,
                    [copy.deepcopy(current[0]) for _ in range(len(cfg.restart))],
                )
            else:
                setattr(cfg, val, [getattr(cfg, val)[0]] * len(cfg.restart))

    if len(cfg.restart) > 1 and cfg.subplot_grid[0]:
        cfg.filename = [cmdargs.filename]
    if cfg.difference_input:
        cfg.aggregation = [cfg.aggregation[0]] * 2
        cfg.filter = [cfg.filter[0]] * 2

    for val in [
        "xformat",
        "yformat",
        "xlog",
        "ylog",
        "xlabel",
        "ylabel",
        "legend_labels",
        "time_units",
        "legend_location",
        "dpi",
        "ytick_count",
        "xtick_count",
        "filename",
        "axis_grid",
        "colorbar_tick_count",
        "color_log",
        "min_threshold",
        "max_threshold",
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
    cfg.cb_format = [".1f", ".0f", ".0f", ".2e", ".0f", ".0f"]
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
    elif cfg.difference_input:
        cfg.cmaps = ["RdYlGn"]
    elif cfg.mask_variable:
        cfg.cmaps = ["RdGy_r"]
    vrs = cfg.vrs
    if vrs:
        first_var = vrs[0]
        if first_var in ["wells", "faults"]:
            if cfg.aggregation[0]:
                if cfg.aggregation[0] not in ["min", "max"]:
                    plopm_error(
                        f"Unsuported value {cli_error_value(f'-agg {cfg.aggregation[0]}')} for "
                        f"{cli_info_value(f'-v {first_var}')}. Supported values are "
                        f"{cli_current_value('-agg min')} and {cli_current_value('-agg max')}."
                    )
                cfg.whow = cfg.aggregation[0]
            else:
                cfg.whow = "min"
            if not cfg.colors_raw:
                cfg.units = [" [-]"]
                cfg.cmaps = ["nipy_spectral"]
                cfg.cb_format = [".0f"]
        if (
            "num" in first_var
            and not cfg.mask_variable
            and not cfg.difference_input
            and not cfg.colors_raw
        ):
            cfg.cmaps = ["tab20"]
            cfg.units = [" [-]"]
            cfg.cb_format = [".0f"]
        if "index" in first_var:
            cfg.units = [" [-]"]
            cfg.cb_format = [".0f"]
    if cfg.colorbar_format:
        cfg.cb_format = cfg.colorbar_format.split(",")
    elif len(vrs) == 1 and "num" in vrs[0]:
        cfg.cb_format = [".0f"]
    elif cfg.difference_input:
        cfg.cb_format = [".1e"]
    num_vars = len(vrs)
    if len(cfg.cmaps) < num_vars or (
        num_vars == len(cfg.names[0]) and len(cfg.names[0]) > 1 and not cfg.colors_raw
    ):
        cfg.cmaps = [cfg.cmaps[0]] * num_vars
    if len(cfg.xlim) < num_vars:
        cfg.xlim = [cfg.xlim[0]] * num_vars
    if len(cfg.ylim) < num_vars:
        cfg.ylim = [cfg.ylim[0]] * num_vars
    if len(cfg.cb_format) < num_vars:
        cfg.cb_format = [cfg.cb_format[0]] * num_vars
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
    if cfg.list_variables:
        for ext in ["INIT", "UNRST"]:
            file = f"{name}.{ext}"
            if os.path.isfile(file):
                reader = OpmFile(file)
                keys = [
                    var[0]
                    for var in reader.arrays
                    if var[0]
                    not in ["INTEHEAD", "LOGIHEAD", "DOUBHEAD", "TABDIMS", "TAB"]
                ]
                if ext == "UNRST":
                    ntot = reader.count("PRESSURE")
                plopm_info(
                    f"the available {cli_info_value('-v')} variables for "
                    f"{cli_info_value(file)} are:"
                )
                print(keys)
                if ext == "UNRST":
                    plopm_info(
                        f"the available {cli_info_value('-r')} restarts for "
                        f"{cli_info_value(file)} are:"
                    )
                    print(list(range(ntot)))
    if (
        cfg.sensor
        or cfg.layer
        or cfg.distance[0]
        or cfg.histogram[0]
        or cfg.csv_column_summary
    ):
        return True
    if (
        first_var[:3] in ["krw", "krg"]
        or first_var[:4] in ["krow", "krog", "pcow", "pcog", "pcwg"]
        or first_var[:6] == "pcfact"
        or (first_var[:8] == "permfact" and cfg.slice == [[[-2, -2], [0, 1], [-2, -2]]])
    ):
        return True
    smspec_file = f"{name}.SMSPEC"
    if os.path.isfile(smspec_file):
        summary = OpmSummary(smspec_file).keys()
        if cfg.list_variables:
            plopm_info(
                f"the available {cli_info_value('-v')} variables for "
                f"{cli_info_value(smspec_file)} are:"
            )
            print(summary)
            sys.exit(0)
        smass = cfg.smass
        for name_v in vrs:
            base = name_v.split(" ")[0].upper()
            if base in summary or base.lower() in smass:
                return True
    if cfg.list_variables:
        sys.exit(0)
    return False


def ini_summary(cfg: ConfigPlopm) -> None:
    """Initialize the needed objects for the summary plots"""
    vrs = cfg.vrs
    nv = len(vrs)
    cfg.numc = 1 if len(cfg.names) < nv else nv
    for val in ["colors_raw", "linestyle", "linewidth"]:
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
            cfg.linewidth = [cfg.linewidth_values] * nv
    for axis_name in ["x", "y"]:
        key = f"{axis_name}lim"
        if len(getattr(cfg, key)) < nv and getattr(cfg, key)[0]:
            setattr(cfg, key, [getattr(cfg, key)[0]] * nv)
    if nv == 1 and len(cfg.linewidth[0]) < len(cfg.names[0]):
        cfg.linewidth[0] = [cfg.linewidth[0][0]] * len(cfg.names[0])
    for val in [
        "names",
        "title",
        "xformat",
        "yformat",
        "xlog",
        "ylog",
        "xlabel",
        "ylabel",
        "legend_labels",
        "time_units",
        "legend_location",
        "dpi",
        "ytick_count",
        "xtick_count",
        "scale_factor",
        "filename",
        "axis_grid",
    ]:
        if len(getattr(cfg, val)) < nv:
            setattr(cfg, val, [getattr(cfg, val)[0]] * nv)
