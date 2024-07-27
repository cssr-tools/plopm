# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W0123

"""
Utiliy functions to set the requiried input values by plopm.
"""

import os
from io import StringIO
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

try:
    from opm.io.ecl import EclFile as OpmFile
    from opm.io.ecl import EGrid as OpmGrid
    from opm.io.ecl import ESmry as OpmSummary
except ImportError:
    print("The Python package opm was not found, using resdata")
try:
    from resdata.resfile import ResdataFile
    from resdata.summary import Summary
    from resdata.grid import Grid
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
    names = (cmdargs["input"].strip()).split(",")
    dic["names"], dic["name"] = names, names[0]
    if len(names) > 1:
        dic["names"] = names
    dic["coords"] = ["x", "y", "z"]
    dic["scale"] = cmdargs["scale"].strip()
    dic["use"] = cmdargs["use"].strip()
    dic["variable"] = cmdargs["variable"].strip()
    dic["size"] = float(cmdargs["size"])
    dic["legend"] = cmdargs["legend"].strip()
    dic["titles"] = cmdargs["title"].strip()
    dic["bounds"] = (cmdargs["bounds"].strip()).split(",")
    dic["dims"] = (cmdargs["dimensions"].strip()).split(",")
    dic["numbers"] = cmdargs["numbers"].strip()
    dic["linsty"] = cmdargs["linsty"].strip()
    dic["colormap"] = cmdargs["colormap"].strip()
    dic["xlim"], dic["ylim"], dic["wells"], dic["vsum"] = [], [], [], []
    dic["grid"], dic["summary"], dic["vsum"], dic["time"] = [], [], [], []
    dic["unrst"] = []
    dic["dtitle"] = ""
    dic["restart"] = int(cmdargs["restart"])
    dic["well"] = int(cmdargs["wells"])
    dic["grid"] = int(cmdargs["grid"])
    if dic["restart"] == -1:
        dic["restart"] = 0
    dic["slide"] = (
        np.genfromtxt(StringIO(cmdargs["slide"]), delimiter=",", dtype=int) - 1
    )
    if cmdargs["xlim"]:
        dic["xlim"] = np.genfromtxt(
            StringIO(cmdargs["xlim"]), delimiter=",", dtype=float
        )
    if cmdargs["ylim"]:
        dic["ylim"] = np.genfromtxt(
            StringIO(cmdargs["ylim"]), delimiter=",", dtype=float
        )
    return dic


def ini_readers(dic):
    """
    Set the classes for reading the properties

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["use"] == "resdata":
        dic["egrid"] = Grid(f"{dic['name']}.EGRID")
        dic["init"] = ResdataFile(f"{dic['name']}.INIT")
        dic["nx"] = dic["egrid"].nx
        dic["ny"] = dic["egrid"].ny
        dic["nz"] = dic["egrid"].nz
        if os.path.isfile(f"{dic['name']}.UNRST"):
            for name in dic["names"]:
                dic["unrst"].append(ResdataFile(f"{name}.UNRST"))
        if os.path.isfile(f"{dic['name']}.SMSPEC"):
            for name in dic["names"]:
                dic["summary"].append(Summary(f"{name}.SMSPEC"))
    else:
        dic["egrid"] = OpmGrid(f"{dic['name']}.EGRID")
        dic["init"] = OpmFile(f"{dic['name']}.INIT")
        dic["nx"] = dic["egrid"].dimension[0]
        dic["ny"] = dic["egrid"].dimension[1]
        dic["nz"] = dic["egrid"].dimension[2]
        if os.path.isfile(f"{dic['name']}.UNRST"):
            for name in dic["names"]:
                dic["unrst"].append(OpmFile(f"{name}.UNRST"))
        if os.path.isfile(f"{dic['name']}.SMSPEC"):
            for name in dic["names"]:
                dic["summary"].append(OpmSummary(f"{name}.SMSPEC"))
    if not os.path.exists(dic["output"]):
        os.system(f"mkdir {dic['output']}")
    ini_slides(dic)


def ini_slides(dic):
    """
    Initialize dictionary entries used for the 2D maps

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["slide"][0] > -1:
        dic["mx"], dic["my"] = 2 * dic["ny"] - 1, 2 * dic["nz"] - 1
        dic["xmeaning"], dic["ymeaning"] = "y", "z"
    elif dic["slide"][1] > -1:
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
    dic["colors"] = [
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
    dic["linestyle"] = [
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
    if dic["variable"]:
        initialize_variable(dic)
    else:
        dic["props"] = [
            "porv",
            "permx",
            "permz",
            "poro",
            "fipnum",
            "satnum",
        ]
        dic["units"] = [
            r" [m$^3$]",
            " [mD]",
            " [mD]",
            " [-]",
            " [-]",
            " [-]",
        ]
        dic["format"] = [
            lambda x, _: f"{x:.2e}",
            lambda x, _: f"{x:.0f}",
            lambda x, _: f"{x:.0f}",
            lambda x, _: f"{x:.1f}",
            lambda x, _: f"{x:.0f}",
            lambda x, _: f"{x:.0f}",
        ]
        dic["cmaps"] = [
            "terrain",
            "turbo",
            "turbo",
            "gnuplot",
            "tab20b",
            "tab20b",
        ]
    if dic["well"] == 1 or dic["grid"] == 1:
        dic["props"] = []
        dic["grid"] = 1
        dic["units"] = [" [-]"]
        dic["cmaps"] = ["nipy_spectral"]
        dic["format"] = [lambda x, _: f"{x:.0f}"]
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
            "figure.figsize": (int(dic["dims"][0]), int(dic["dims"][1])),
        }
    )
    dic["xc"], dic["yc"] = [], []


def initialize_variable(dic):
    """
    Initialize the properties according to the given variable

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["props"] = [dic["variable"]]
    if dic["variable"].lower() in ["disperc", "depth", "dx", "dy", "dz"]:
        dic["units"] = [" [m]"]
        dic["cmaps"] = ["jet"]
        dic["format"] = [lambda x, _: f"{x:.2e}"]
    elif dic["variable"].lower() in ["porv"]:
        dic["units"] = [r" [m$^3$]"]
        dic["cmaps"] = ["terrain"]
        dic["format"] = [lambda x, _: f"{x:.2e}"]
    elif dic["variable"].lower() in ["permx", "permy", "permz"]:
        dic["units"] = [" [mD]"]
        dic["cmaps"] = ["turbo"]
        dic["format"] = [lambda x, _: f"{x:.0f}"]
    elif "num" in dic["variable"].lower():
        dic["units"] = [" [-]"]
        dic["cmaps"] = ["tab20b"]
        dic["format"] = [lambda x, _: f"{x:.2f}"]
    else:
        dic["units"] = [" [-]"]
        dic["cmaps"] = ["gnuplot"]
        dic["format"] = [lambda x, _: f"{x:.0f}"]
    if dic["legend"]:
        dic["units"] = [f" {dic['legend']}"]
    if len(dic["names"]) == 2:
        dic["cmaps"] = ["seismic"]
    if dic["variable"].lower() in ["pressure"]:
        dic["units"] = [" [bar]"]
    if dic["variable"].lower() in ["sgas", "rsw"]:
        dic["format"] = [lambda x, _: f"{x:.2f}"]
    if dic["variable"].lower() in ["rvw"]:
        dic["format"] = [lambda x, _: f"{x:.2e}"]
    if dic["colormap"]:
        dic["cmaps"] = [dic["colormap"]]
    if dic["numbers"]:
        dic["format"] = [eval(dic["numbers"])]
