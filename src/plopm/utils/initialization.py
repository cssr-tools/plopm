# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W0123,R0915,R0912

"""
Utiliy functions to set the requiried input values by plopm.
"""

import os
import sys
import matplotlib
import matplotlib.pyplot as plt

try:
    from opm.io.ecl import EclFile as OpmFile
    from opm.io.ecl import ESmry as OpmSummary
except ImportError:
    print("The Python package opm was not found, using resdata")
try:
    from resdata.resfile import ResdataFile
    from resdata.summary import Summary
except ImportError:
    print("The resdata Python package was not found, using opm")


def ini_dic(cmdargs):
    """
    Initialize the global dictionary

    Args:
        cmdargs (dict): Command arguments

    Returns:
        dic (dict): Modified global dictionary

    """
    dic = {"output": cmdargs["output"].strip()}
    names = (cmdargs["input"].strip()).split("  ")
    names = [var.split(" ") for var in names]
    dic["mode"] = cmdargs["mode"].strip()
    if names[0][0] == "." or names[0][0] == "./":
        names = []
        names.append([])
        for root, _, files in os.walk("."):
            for file in files:
                if dic["mode"] == "vtk":
                    if file.endswith(".DATA"):
                        names[-1].append(os.path.join(root, file)[2:-5])
                else:
                    if file.endswith(".SMSPEC"):
                        names[-1].append(os.path.join(root, file)[2:-7])
    dic["names"], dic["name"] = names, names[0][0]
    dic["coords"] = ["x", "y", "z"]
    dic["scale"] = int(cmdargs["scale"])
    dic["delax"] = int(cmdargs["delax"])
    dic["printv"] = int(cmdargs["printv"])
    dic["subfigs"] = (cmdargs["subfigs"].strip()).split(",")
    dic["use"] = cmdargs["use"].strip()
    dic["vrs"] = (cmdargs["variable"].strip()).split(",")
    dic["lw"] = cmdargs["lw"].strip()
    dic["size"] = float(cmdargs["size"])
    dic["maskthr"] = float(cmdargs["maskthr"])
    dic["interval"] = float(cmdargs["interval"])
    dic["loop"] = int(cmdargs["loop"])
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
    # dic["skl"] = float(cmdargs["adjust"])
    dic["avar"] = (cmdargs["adjust"].strip()).split(",")
    dic["axgrid"] = (cmdargs["axgrid"].strip()).split(",")
    dic["dpi"] = (cmdargs["dpi"].strip()).split(",")
    dic["loc"] = (cmdargs["loc"].strip()).split(",")
    dic["vtkformat"] = (cmdargs["vtkformat"].strip()).split(",")
    dic["vtknames"] = (cmdargs["vtknames"].strip()).split("  ")
    dic["log"] = (cmdargs["log"].strip()).split(",")
    dic["rotate"] = (cmdargs["rotate"].strip()).split(",")
    dic["global"] = int(cmdargs["global"])
    dic["save"] = (cmdargs["save"].strip()).split("  ")
    dic["translate"] = (cmdargs["translate"]).split(" ")
    dic["translate"] = [var.split(",") for var in dic["translate"]]
    dic["restart"] = (cmdargs["restart"].strip()).split(",")
    dic["cbsfax"] = [float(val) for val in (cmdargs["cbsfax"].strip()).split(",")]
    for i in ["x", "y"]:
        dic[f"{i}units"] = cmdargs[f"{i}units"].strip()
        dic[f"{i}label"] = (cmdargs[f"{i}label"].strip()).split(" ")
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
    ]:
        dic[name] = []
    dic["dtitle"] = ""
    if dic["restart"][0] == "-1":
        dic["restart"] = [-1]
    elif int(dic["restart"][0]) == 0 and len(dic["restart"]) == 2:
        dic["restart"] = list(range(0, int(dic["restart"][1]) + 1))
    else:
        dic["restart"] = [int(i) for i in dic["restart"]]
    dic["slide"] = (cmdargs["slide"]).split(" ")
    dic["slide"] = [
        [val if val else [-2, -2] for val in var.split(",")] for var in dic["slide"]
    ]
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
    dic["mass"] = ["gasm", "dism", "liqm", "vapm", "co2m", "h2om"]
    dic["smass"] = ["FWCDM", "FGIPM"]
    dic["xmass"] = ["xco2l", "xh2ov", "xco2v", "xh2ol"]
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
    dic["LW"] = ["1"] * len(dic["names"][0])
    font = {"family": "normal", "weight": "normal", "size": dic["size"]}
    matplotlib.rc("font", **font)
    plt.rcParams.update(
        {
            "text.usetex": True,
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
                if dic["use"] == "resdata":
                    reader = ResdataFile(f"{dic['name']}.{ext.upper()}")
                    keys = list(reader.keys())
                    if ext == "unrst":
                        ntot = len(reader.iget_kw("PRESSURE"))
                else:
                    reader = OpmFile(f"{dic['name']}.{ext.upper()}")
                    keys = list(reader.keys())
                    if ext == "unrst":
                        ntot = reader.count("PRESSURE")
                print(f"The {what} available variables for {dic['name']} are:")
                print(keys)
                if ext == "unrst":
                    print(f"The available restarts for {dic['name']} are:")
                    print(list(range(0, ntot)))
    if os.path.isfile(f"{dic['name']}.SMSPEC"):
        if dic["use"] == "resdata":
            summary = Summary(f"{dic['name']}.SMSPEC").keys()
        else:
            summary = OpmSummary(f"{dic['name']}.SMSPEC").keys()
        if dic["printv"] == 1:
            print(f"The summary available variables for {dic['name']} are:")
            print(summary)
            sys.exit()
        for name in dic["vrs"]:
            if name.upper() in summary + dic["smass"]:
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
    if dic["colors"]:
        dic["cmaps"] = dic["colors"].split(",")
    elif dic["diff"]:
        dic["cmaps"] = ["RdYlGn"]
    elif dic["mask"]:
        dic["cmaps"] = ["RdGy_r"]
    if dic["vrs"]:  # dic["well"] == 1
        if dic["vrs"][0] == "wells":
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
    if len(dic["cmaps"]) < len(dic["vrs"]):
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
