# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W0123,R0915,R0912,R1702,R0914,R0916

"""
Utiliy functions to set the requiried input values by plopm.
"""

import os
import sys
import shutil
import matplotlib
import matplotlib.pyplot as plt
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import ESmry as OpmSummary


def ini_dic(cmdargs):
    """
    Initialize the global dictionary

    Args:
        cmdargs (dict): Command arguments

    Returns:
        dic (dict): Modified global dictionary

    """
    dic = {"output": os.path.abspath(cmdargs["output"].strip())}
    names = (cmdargs["input"].strip()).split("  ")
    names = [var.split(" ") for var in names]
    dic["namens"] = names
    dic["mode"] = cmdargs["mode"].strip()
    dic["ensemble"] = int(cmdargs["ensemble"])
    if names[0][0][-1] in [".", "/"]:
        folders = names[0]
        names = []
        for i, folder in enumerate(folders):
            if dic["ensemble"] > 0 or i == 0:
                names.append([])
            if folder[0] != ".":
                folder = "./" + folder
            for root, _, files in os.walk(folder):
                for file in files:
                    if dic["mode"] == "vtk":
                        if file.endswith(".DATA"):
                            names[-1].append(os.path.join(root, file)[2:-5])
                    else:
                        if file.endswith(".SMSPEC"):
                            names[-1].append(os.path.join(root, file)[2:-7])
            names[-1] = sorted(names[-1])
    dic["names"], dic["name"] = names, names[0][0]
    dic["coords"] = ["x", "y", "z"]
    dic["scale"] = int(cmdargs["scale"])
    dic["delax"] = int(cmdargs["delax"])
    dic["printv"] = int(cmdargs["printv"])
    dic["bandprop"] = cmdargs["bandprop"]
    dic["subfigs"] = (cmdargs["subfigs"].strip()).split(",")
    dic["vrs"] = (cmdargs["variable"].strip()).split(",")
    dic["lw"] = cmdargs["lw"].strip()
    dic["size"] = float(cmdargs["size"])
    dic["maskthr"] = float(cmdargs["maskthr"])
    dic["interval"] = float(cmdargs["interval"])
    dic["stress"] = float(cmdargs["stress"])
    dic["loop"] = int(cmdargs["loop"])
    dic["filter"] = (cmdargs["filter"].strip()).split(",")
    dic["titles"] = (cmdargs["title"].strip()).split("  ")
    dic["bounds"] = (cmdargs["bounds"].strip()).split(" ")
    dic["bounds"] = [var.split(",") for var in dic["bounds"]]
    dic["dims"] = (cmdargs["dimensions"].strip()).split(",")
    dic["cf"] = cmdargs["cformat"].strip()
    dic["linestyle"] = cmdargs["linestyle"].strip()
    dic["colors"] = cmdargs["colors"].strip()
    dic["vmin"] = (cmdargs["vmin"].strip()).split(",")
    dic["vmax"] = (cmdargs["vmax"].strip()).split(",")
    dic["flow"] = cmdargs["path"].strip()
    dic["grid"] = (cmdargs["grid"].strip()).split(",")
    dic["fc"] = cmdargs["facecolor"].strip()
    dic["ncolor"] = cmdargs["ncolor"].strip()
    dic["cnum"] = (cmdargs["cnum"].strip()).split(",")
    dic["mask"] = cmdargs["mask"].strip()
    dic["suptitle"] = cmdargs["suptitle"].strip()
    dic["diff"] = cmdargs["diff"].strip()
    dic["clabel"] = cmdargs["clabel"].strip()
    dic["labels"] = (cmdargs["labels"].strip()).split("   ")
    dic["labels"] = [var.split("  ") for var in dic["labels"]]
    dic["rm"] = (cmdargs["remove"].strip()).split(",")
    dic["rm"] = [int(val) for val in dic["rm"]]
    dic["tunits"] = (cmdargs["tunits"].strip()).split(",")
    dic["avar"] = (cmdargs["adjust"].strip()).split(",")
    dic["axgrid"] = (cmdargs["axgrid"].strip()).split(",")
    dic["dpi"] = (cmdargs["dpi"].strip()).split(",")
    dic["cticks"] = (cmdargs["cticks"].strip()).split("  ")
    dic["loc"] = (cmdargs["loc"].strip()).split(",")
    dic["vtkformat"] = (cmdargs["vtkformat"].strip()).split(",")
    dic["vtknames"] = (cmdargs["vtknames"].strip()).split("  ")
    dic["log"] = (cmdargs["log"].strip()).split(",")
    dic["clogthks"] = cmdargs["clogthks"].strip()
    dic["rotate"] = (cmdargs["rotate"].strip()).split(",")
    dic["global"] = int(cmdargs["global"])
    dic["save"] = (cmdargs["save"].strip()).split("  ")
    dic["translate"] = (cmdargs["translate"]).split(" ")
    dic["translate"] = [var.split(",") for var in dic["translate"]]
    dic["restart"] = (cmdargs["restart"].strip()).split(",")
    dic["cbsfax"] = cmdargs["cbsfax"].strip()
    dic["nwells"], dic["lwells"] = 0, []
    dic["how"] = (cmdargs["how"].strip()).split(",")
    dic["distance"] = (cmdargs["distance"].strip()).split(",")
    dic["histogram"] = (cmdargs["histogram"].strip()).split(" ")
    for i in ["x", "y"]:
        dic[f"{i}units"] = cmdargs[f"{i}units"].strip()
        dic[f"{i}label"] = (cmdargs[f"{i}label"].strip()).split("  ")
        dic[f"{i}format"] = (cmdargs[f"{i}format"].strip()).split(",")
        dic[f"{i}lnum"] = (cmdargs[f"{i}lnum"].strip()).split(",")
        dic[f"{i}log"] = (cmdargs[f"{i}log"].strip()).split(",")
        dic[f"{i}lim"] = (cmdargs[f"{i}lim"]).split(" ")
        dic[f"{i}lim"] = [var.split(",") for var in dic[f"{i}lim"]]
    for name in [
        "vsum",
        "summary",
        "vsum",
        "time",
        "wells",
        "faults",
    ]:
        dic[name] = []
    dic["dtitle"] = ""
    if dic["clogthks"]:
        dic["clogthks"] = [float(val) for val in dic["clogthks"][1:-1].split(",")]
    if dic["cticks"][0]:
        for i, values in enumerate(dic["cticks"]):
            dic["cticks"][i] = [val.strip() for val in values[1:-1].split(",")]
    dic["rst_range"] = False
    if dic["cbsfax"] != "empty":
        dic["cbsfax"] = [float(val) for val in (cmdargs["cbsfax"].strip()).split(",")]
    if dic["restart"][0] == "-1":
        dic["restart"] = [-1]
    elif ":" in dic["restart"][0]:
        dic["rst_range"] = True
        vals = dic["restart"][0].split(":")
        if len(vals) == 3:
            dic["restart"] = list(range(int(vals[0]), int(vals[1]) + 1, int(vals[2])))
        else:
            dic["restart"] = list(range(int(vals[0]), int(vals[1]) + 1))
        if dic["save"][0]:
            dic["save"] = [
                dic["save"][0] + f"{i}".zfill(len(str(dic["restart"][-1])))
                for i in dic["restart"]
            ]
    else:
        dic["restart"] = [int(i) for i in dic["restart"]]
    dic["sensor"], dic["layer"] = False, False
    dic["slide"] = (cmdargs["slide"]).split(" ")
    dic["slide"] = [
        [val if val else [-2, -2] for val in var.split(",")] for var in dic["slide"]
    ]
    dic["csvs"] = (cmdargs["csv"]).split(";")
    dic["csvs"] = [
        [int(val) if val else "" for val in var.split(",")] for var in dic["csvs"]
    ]
    dic["csvsummary"], allcsvs = False, True
    for val in dic["csvs"]:
        if not val[0]:
            allcsvs = False
        else:
            if len(val) == 2:
                dic["csvsummary"] = True
    if allcsvs:
        dic["vrs"] = ["csv"]
    if len(dic["csvs"]) == 1 and not dic["csvs"][0][0]:
        dic["csvs"] = [dic["csvs"][0]] * (
            max(len(dic["names"][0]), len(dic["vrs"])) + 1
        )
    if [-2, -2] in dic["slide"][0]:
        for i, var in enumerate(dic["slide"]):
            for j, val in enumerate(var):
                if val[0] != -2:
                    if ":" in val:
                        dic["slide"][i][j] = [
                            int(val.split(":")[0]) - 1,
                            int(val.split(":")[1]),
                        ]
                    else:
                        dic["slide"][i][j] = [int(val) - 1, int(val)]
    elif ":" in dic["slide"][0]:
        dic["layer"] = True
        for i, var in enumerate(dic["slide"]):
            for j, val in enumerate(var):
                if val != ":":
                    dic["slide"][i][j] = int(val) - 1
                else:
                    dic["slide"][i][j] = -1
    else:
        dic["sensor"] = True
        for i, var in enumerate(dic["slide"]):
            for j, val in enumerate(var):
                dic["slide"][i][j] = int(val) - 1
    dic["mass"] = ["gasm", "dism", "liqm", "vapm", "co2m", "h2om"]
    dic["smass"] = ["FWCDM", "FGIPM"]
    dic["xmass"] = ["xco2l", "xh2ov", "xco2v", "xh2ol"]
    dic["caprock"] = ["limipres", "overpres", "objepres"]
    if not os.path.exists(dic["output"]):
        os.system(f"mkdir {dic['output']}")
    dic["COLORS"] = [
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
    dic["LINESTYLE"] = [
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
    dic["discrete"] = True
    for val in dic["vrs"]:
        for oper in ["=", "<", ">"]:
            if oper in val:
                dic["discrete"] = False
    dic["LW"] = ["1"] * len(dic["names"][0])
    font = {"family": "normal", "weight": "normal", "size": dic["size"]}
    matplotlib.rc("font", **font)
    plt.rcParams.update(
        {
            "text.usetex": shutil.which("latex") != "None",
            "font.family": "monospace",
            "legend.columnspacing": 0.9,
            "legend.handlelength": 3.5,
            "legend.fontsize": dic["size"],
            "lines.linewidth": 4,
            "axes.titlesize": dic["size"],
            "axes.grid": False,
            "figure.figsize": (float(dic["dims"][0]), float(dic["dims"][1])),
        }
    )
    for name in ["vtkformat", "avar", "vtknames"]:
        if len(dic[name]) < len(dic["vrs"]):
            dic[name] = [dic[name][0]] * len(dic["vrs"])
    if len(dic["save"]) < len(dic["vrs"]):
        dic["save"] = [dic["save"][0]] * len(dic["vrs"])
    if len(dic["bounds"]) < len(dic["vrs"]):
        dic["bounds"] = [dic["bounds"][0]] * len(dic["vrs"])
    if dic["diff"] and len(dic["rotate"]) < 2:
        dic["rotate"] = [dic["rotate"][0]] * 2
    elif len(dic["rotate"]) < len(dic["names"][0]):
        dic["rotate"] = [dic["rotate"][0]] * len(dic["names"][0])
    if dic["diff"] and len(dic["translate"]) < 2:
        dic["translate"] = [dic["translate"][0]] * 2
    if len(dic["translate"]) < len(dic["names"][0]):
        dic["translate"] = [dic["translate"][0]] * len(dic["names"][0])
    if len(dic["titles"]) < max(len(dic["names"][0]), len(dic["vrs"])):
        dic["titles"] = [dic["titles"][0]] * max(len(dic["names"][0]), len(dic["vrs"]))
    if dic["diff"] and len(dic["slide"]) < 2:
        dic["slide"] = [dic["slide"][0]] * 2
    elif len(dic["slide"]) < max(len(dic["names"][0]), len(dic["vrs"])):
        dic["slide"] = [dic["slide"][0]] * max(len(dic["names"][0]), len(dic["vrs"]))
    for val in ["how", "filter", "cticks"]:
        if len(dic[val]) < max(len(dic["names"][0]), len(dic["vrs"])):
            dic[val] = [dic[val][0]] * max(len(dic["names"][0]), len(dic["vrs"]))
    if dic["diff"]:
        dic["how"] = [dic["how"][0]] * 2
        dic["filter"] = [dic["filter"][0]] * 2
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
        "avar",
        "save",
        "axgrid",
        "cnum",
        "log",
        "vmin",
        "vmax",
    ]:
        if len(dic[val]) < len(dic["vrs"]):
            dic[val] = [dic[val][0]] * len(dic["vrs"])
    return dic


def ini_summary(dic):
    """
    Initialize the needed objects for the summary plots

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["numc"] = 1 if len(dic["names"]) < len(dic["vrs"]) else len(dic["vrs"])
    for val in ["colors", "linestyle", "lw"]:
        if dic[val]:
            dic[val] = dic[val].split(":")
            dic[val] = [var.split(",") for var in dic[val]]
            if len(dic[val]) < len(dic["vrs"]):
                dic[val] = [dic[val][0]] * len(dic["vrs"])
        else:
            dic[val] = [dic[val.upper()]] * len(dic["vrs"])
    for i in ["x", "y"]:
        if len(dic[f"{i}lim"]) < len(dic["vrs"]) and dic[f"{i}lim"][0][0]:
            dic[f"{i}lim"] = [dic[f"{i}lim"][0]] * len(dic["vrs"])
    for val in [
        "names",
        "titles",
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
        "avar",
        "save",
        "axgrid",
    ]:
        if len(dic[val]) < len(dic["vrs"]):
            dic[val] = [dic[val][0]] * len(dic["vrs"])


def is_summary(dic):
    """
    Check flag arguments and files for summary plot

    Args:
        dic (dict): Global dictionary

    Returns:
        bool: True if one variable is in the summary keys

    """
    ntot = 0
    if dic["printv"] == 1:
        for ext, what in zip(["init", "unrst"], ["init", "restart"]):
            if os.path.isfile(f"{dic['name']}.{ext.upper()}"):
                reader = OpmFile(f"{dic['name']}.{ext.upper()}")
                keys = list(reader.keys())
                if ext == "unrst":
                    ntot = reader.count("PRESSURE")
                print(f"The {what} available variables for {dic['name']} are:")
                print(keys)
                if ext == "unrst":
                    print(f"The available restarts for {dic['name']} are:")
                    print(list(range(0, ntot)))
    if (
        dic["sensor"]
        or dic["layer"]
        or dic["distance"][0]
        or dic["histogram"][0]
        or dic["vrs"][0].lower()[:3] in ["krw", "krg"]
        or dic["vrs"][0].lower()[:4] in ["krow", "krog", "pcow", "pcog", "pcwg"]
        or dic["vrs"][0].lower()[:6] == "pcfact"
        or dic["csvsummary"]
    ):
        return True
    if os.path.isfile(f"{dic['name']}.SMSPEC"):
        summary = OpmSummary(f"{dic['name']}.SMSPEC").keys()
        if dic["printv"] == 1:
            print(f"The summary available variables for {dic['name']} are:")
            print(summary)
            sys.exit()
        for name in dic["vrs"]:
            names = name.split(" ")
            if names[0].upper() in summary + dic["smass"]:
                return True
    if dic["printv"] == 1:
        sys.exit()
    return False


def ini_slides(dic, n):
    """
    Initialize dictionary entries used for the 2D maps

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["slide"][n][0][0] > -1:
        dic["mx"], dic["my"] = 2 * dic["ny"] - 1, 2 * dic["nz"] - 1
        dic["xmeaning"], dic["ymeaning"] = "y", "z"
    elif dic["slide"][n][1][0] > -1:
        dic["mx"], dic["my"] = 2 * dic["nx"] - 1, 2 * dic["nz"] - 1
        dic["xmeaning"], dic["ymeaning"] = "x", "z"
    else:
        dic["mx"], dic["my"] = 2 * dic["nx"] - 1, 2 * dic["ny"] - 1
        dic["xmeaning"], dic["ymeaning"] = "x", "y"


def ini_properties(dic):
    """
    Define the properties to plot

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["units"] = [
        " [-]",
        " [mD]",
        " [mD]",
        r" [m$^3$]",
        " [-]",
        " [-]",
    ]
    dic["cformat"] = [
        ".1f",
        ".0f",
        ".0f",
        ".2e",
        ".0f",
        ".0f",
    ]
    dic["cmaps"] = [
        "jet",
        "turbo",
        "turbo",
        "terrain",
        "tab20b",
        "tab20b",
    ]
    dic["cmdisc"] = []
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
    for color in cmdisc:
        dic["cmdisc"].insert(0, color + "_r")
    dic["cmdisc"] += cmdisc
    if dic["colors"]:
        dic["cmaps"] = dic["colors"].split(",")
    elif dic["diff"]:
        dic["cmaps"] = ["RdYlGn"]
    elif dic["mask"]:
        dic["cmaps"] = ["RdGy_r"]
    if dic["vrs"][0] == "wells" or dic["vrs"][0] == "faults":
        if dic["how"][0]:
            if dic["how"][0] not in ["min", "max"]:
                print(f"Unsuported value -how '{dic['how'][0]}' for wells/faults. ")
                print("Supported values are 'min' and 'max'.")
                sys.exit()
            else:
                dic["whow"] = dic["how"][0]
        else:
            dic["whow"] = "min"
    if dic["vrs"]:
        if (dic["vrs"][0] == "wells" or dic["vrs"][0] == "faults") and not dic[
            "colors"
        ]:
            dic["units"] = [" [-]"]
            dic["cmaps"] = ["nipy_spectral"]
            dic["cformat"] = [".0f"]
        if (
            "num" in dic["vrs"][0]
            and not dic["mask"]
            and not dic["diff"]
            and not dic["colors"]
        ):
            dic["cmaps"] = ["tab20"]
            dic["units"] = [" [-]"]
            dic["cformat"] = [".0f"]
        if "index" in dic["vrs"][0]:
            dic["units"] = [" [-]"]
            dic["cformat"] = [".0f"]
    if dic["cf"]:
        dic["cformat"] = dic["cf"].split(",")
    elif len(dic["vrs"]) == 1 and "num" in dic["vrs"][0]:
        dic["cformat"] = [".0f"]
    if len(dic["cmaps"]) < len(dic["vrs"]) or (
        len(dic["vrs"]) == len(dic["names"][0])
        and len(dic["names"][0]) > 1
        and not dic["colors"]
    ):
        dic["cmaps"] = [dic["cmaps"][0]] * len(dic["vrs"])
    if len(dic["xlim"]) < len(dic["vrs"]):
        dic["xlim"] = [dic["xlim"][0]] * len(dic["vrs"])
    if len(dic["ylim"]) < len(dic["vrs"]):
        dic["ylim"] = [dic["ylim"][0]] * len(dic["vrs"])
    if len(dic["cformat"]) < len(dic["vrs"]):
        dic["cformat"] = [dic["cformat"][0]] * len(dic["vrs"])
    dic["xskl"], dic["xunit"] = initialize_spatial(dic["xunits"])
    dic["yskl"], dic["yunit"] = initialize_spatial(dic["yunits"])


def initialize_spatial(unit):
    """
    Handle the units for the axis in the spatial maps

    Args:
        unit (str): Type for the axis unit

    Returns:
        scale (float): Scale for the coordinates\n
        unit (str): Units for the axis

    """
    if unit == "m":
        return 1, " [m]"
    if unit == "km":
        return 1e-3, " [km]"
    if unit == "cm":
        return 1e2, " [cm]"
    return 1e3, " [mm]"


def initialize_mass(mskl):
    """
    Initialize the mass properties according to the given variable

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    vunit = ""
    if mskl == 1e-3:
        vunit = " [t]"
    elif mskl == 1e-6:
        vunit = " [Kt]"
    elif mskl == 1e-9:
        vunit = " [Mt]"
    elif mskl == 1e3:
        vunit = " [g]"
    elif mskl == 1e6:
        vunit = " [mg]"
    elif mskl == 1:
        vunit = " [kg]"
    return vunit
