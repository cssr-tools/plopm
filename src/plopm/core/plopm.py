#!/usr/bin/env python
# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1702, W0123, W1401

"""
Script to plot 2D maps of OPM Flow geological models.
"""

import argparse
import csv
import os
from io import StringIO
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

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


def plopm():
    """Main function for the plopm executable"""
    cmdargs = load_parser()
    dic = ini_dic(cmdargs)
    ini_properties(dic)
    ini_readers(dic)
    if not os.path.exists(dic["output"]):
        os.system(f"mkdir {dic['output']}")
    if dic["slide"][0] > -1:
        dic["mx"], dic["my"] = 2 * dic["ny"] - 1, 2 * dic["nz"] - 1
        dic["xmeaning"], dic["ymeaning"] = "y", "z"
    elif dic["slide"][1] > -1:
        dic["mx"], dic["my"] = 2 * dic["nx"] - 1, 2 * dic["nz"] - 1
        dic["xmeaning"], dic["ymeaning"] = "x", "z"
    else:
        dic["mx"], dic["my"] = 2 * dic["nx"] - 1, 2 * dic["ny"] - 1
        dic["xmeaning"], dic["ymeaning"] = "x", "y"
    dic["wx"], dic["wy"] = 2 * dic["nx"] - 1, 2 * dic["ny"] - 1
    get_kws(dic)
    if len(dic["vsum"]) > 0:
        make_summary(dic)
        return
    get_mesh(dic)
    if dic["wells"] == 1:
        get_wells(dic)
        get_xy_wells(dic)
        make_wells(dic)
        return
    if dic["slide"][0] > -1:
        dic["tslide"] = f", slide i={dic['slide'][0]+1}"
        dic["nslide"] = f"{dic['slide'][0]+1},*,*"
        get_yzcoords(dic)
        map_yzcoords(dic)
    elif dic["slide"][1] > -1:
        dic["tslide"] = f", slide j={dic['slide'][1]+1}"
        dic["nslide"] = f"*,{dic['slide'][1]+1},*"
        get_xzcoords(dic)
        map_xzcoords(dic)
    else:
        dic["tslide"] = f", slide k={dic['slide'][2]+1}"
        dic["nslide"] = f"*,*,{dic['slide'][2]+1}"
        get_xycoords(dic)
        map_xycoords(dic)
    make_2dmaps(dic)


def make_summary(dic):
    """
    Plot the summary variable

    Args:
        cmdargs (dict): Command arguments

    Returns:
        None

    """
    plt.rcParams.update({"axes.grid": True})
    fig, axis = plt.subplots()
    if len(dic["cmaps"]) == 1:
        axis.step(dic["time"], dic["vsum"], color=dic["cmaps"][0])
    else:
        axis.step(dic["time"], dic["vsum"], color="b")
    axis.set_ylabel(dic["props"][0])
    axis.set_xlabel("Time [s]")
    axis.set_xlim([min(dic["time"]), max(dic["time"])])
    axis.set_ylim([min(dic["vsum"]), max(dic["vsum"])])
    axis.set_xticks(
        np.linspace(
            min(dic["time"]),
            max(dic["time"]),
            4,
        )
    )
    axis.set_yticks(
        np.linspace(
            min(dic["vsum"]),
            max(dic["vsum"]),
            4,
        )
    )
    fig.savefig(f"{dic['output']}/{dic['variable']}.png", bbox_inches="tight", dpi=300)
    plt.close()


def ini_dic(cmdargs):
    """
    Initialize the global dictionary

    Args:
        cmdargs (dict): Command arguments

    Returns:
        dic (dict): Modified global dictionary

    """
    dic = {"name": cmdargs["input"].strip()}
    dic["coords"] = ["x", "y", "z"]
    dic["scale"] = cmdargs["scale"].strip()
    dic["use"] = cmdargs["use"].strip()
    dic["variable"] = cmdargs["variable"].strip()
    dic["size"] = float(cmdargs["size"])
    dic["legend"] = cmdargs["legend"].strip()
    dic["numbers"] = cmdargs["numbers"].strip()
    dic["colormap"] = cmdargs["colormap"].strip()
    dic["output"] = cmdargs["output"].strip()
    dic["xlim"], dic["ylim"], dic["wellsij"], dic["vsum"] = [], [], [], []
    dic["dtitle"] = ""
    dic["restart"] = int(cmdargs["restart"])
    dic["wells"] = int(cmdargs["wells"])
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
            dic["unrst"] = ResdataFile(f"{dic['name']}.UNRST")
        if os.path.isfile(f"{dic['name']}.SMSPEC"):
            dic["summary"] = Summary(f"{dic['name']}.SMSPEC")
    else:
        dic["egrid"] = OpmGrid(f"{dic['name']}.EGRID")
        dic["init"] = OpmFile(f"{dic['name']}.INIT")
        dic["nx"] = dic["egrid"].dimension[0]
        dic["ny"] = dic["egrid"].dimension[1]
        dic["nz"] = dic["egrid"].dimension[2]
        if os.path.isfile(f"{dic['name']}.UNRST"):
            dic["unrst"] = OpmFile(f"{dic['name']}.UNRST")
        if os.path.isfile(f"{dic['name']}.SMSPEC"):
            dic["summary"] = OpmSummary(f"{dic['name']}.SMSPEC")


def ini_properties(dic):
    """
    Define the properties to plot

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["variable"]:
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
        if dic["numbers"]:
            dic["format"] = [eval(dic["numbers"])]
        if dic["colormap"]:
            dic["cmaps"] = [dic["colormap"]]
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
            "figure.figsize": (8, 16),
        }
    )


def get_yzcoords(dic):
    """
    Handle the coordinates from the OPM Grid to the 2D yz-mesh

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for j in range(dic["nz"]):
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [1, 7, 2, 8]):
            dic[f"{k}c"][-1].append(
                dic["mesh"][(dic["nz"] - j - 1) * dic["nx"] * dic["ny"]][n]
            )
        for i in range(dic["ny"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [1, 7, 2, 8]):
                dic[f"{k}c"][-1].append(
                    dic["mesh"][
                        (i + 1) * dic["nx"]
                        + (dic["nz"] - j - 1) * dic["nx"] * dic["ny"]
                    ][n]
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [13, 19, 14, 20]):
            dic[f"{k}c"][-1].append(
                dic["mesh"][(dic["nz"] - j - 1) * dic["nx"] * dic["ny"]][n]
            )
        for i in range(dic["ny"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [13, 19, 14, 20]):
                dic[f"{k}c"][-1].append(
                    dic["mesh"][
                        (i + 1) * dic["nx"]
                        + (dic["nz"] - j - 1) * dic["nx"] * dic["ny"]
                    ][n]
                )


def map_yzcoords(dic):
    """
    Map the properties from the simulations to the 2D slide

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["use"] == "resdata":
        for cell in dic["egrid"].cells():
            if cell.active and cell.i == dic["slide"][0]:
                for name in dic["props"]:
                    dic[name + "a"][
                        2 * cell.j + 2 * (dic["nz"] - cell.k - 1) * dic["mx"]
                    ] = dic[name][cell.active_index]
                if "porv" in dic["props"]:
                    dic["porva"][
                        2 * cell.j + 2 * (dic["nz"] - cell.k - 1) * dic["mx"]
                    ] = dic["porv"][cell.global_index]
    else:
        for k in range(dic["nz"]):
            for j in range(dic["ny"]):
                for i in range(dic["nx"]):
                    if (
                        dic["porv"][i + j * dic["nx"] + k * dic["nx"] * dic["ny"]] > 0
                        and i == dic["slide"][0]
                    ):
                        for name in dic["props"]:
                            dic[name + "a"][
                                2 * j + 2 * (dic["nz"] - k - 1) * dic["mx"]
                            ] = dic[name][
                                dic["actind"][
                                    i + j * dic["nx"] + k * dic["nx"] * dic["ny"]
                                ]
                            ]
                        if "porv" in dic["props"]:
                            dic["porva"][
                                2 * j + 2 * (dic["nz"] - k - 1) * dic["mx"]
                            ] = dic["porv"][
                                i + j * dic["nx"] + k * dic["nx"] * dic["ny"]
                            ]


def get_mesh(dic):
    """
    Read the coordinates using either opm or resdata

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["use"] == "resdata":
        dic["mesh"] = dic["egrid"].export_corners(dic["egrid"].export_index())
    else:
        dic["mesh"] = []
        for k in range(dic["nz"]):
            for j in range(dic["ny"]):
                for i in range(dic["nx"]):
                    dic["mesh"].append([])
                    for n in range(8):
                        dic["mesh"][-1] += [
                            dic["egrid"].xyz_from_ijk(i, j, k)[0][n],
                            dic["egrid"].xyz_from_ijk(i, j, k)[1][n],
                            dic["egrid"].xyz_from_ijk(i, j, k)[2][n],
                        ]
    dic["xc"], dic["yc"] = [], []


def get_xzcoords(dic):
    """
    Handle the coordinates from the OPM Grid to the 2D xz-mesh

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for j in range(dic["nz"]):
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [0, 3, 2, 5]):
            dic[f"{k}c"][-1].append(
                dic["mesh"][(dic["nz"] - j - 1) * dic["nx"] * dic["ny"]][n]
            )
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [0, 3, 2, 5]):
                dic[f"{k}c"][-1].append(
                    dic["mesh"][1 + i + (dic["nz"] - j - 1) * dic["nx"] * dic["ny"]][n]
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [12, 15, 14, 17]):
            dic[f"{k}c"][-1].append(
                dic["mesh"][(dic["nz"] - j - 1) * dic["nx"] * dic["ny"]][n]
            )
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [12, 15, 14, 17]):
                dic[f"{k}c"][-1].append(
                    dic["mesh"][1 + i + (dic["nz"] - j - 1) * dic["nx"] * dic["ny"]][n]
                )


def map_xzcoords(dic):
    """
    Map the properties from the simulations to the 2D slide

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["use"] == "resdata":
        for cell in dic["egrid"].cells():
            if cell.active and cell.j == dic["slide"][1]:
                for name in dic["props"]:
                    dic[name + "a"][
                        2 * cell.i + 2 * (dic["nz"] - cell.k - 1) * dic["mx"]
                    ] = dic[name][cell.active_index]
                if "porv" in dic["props"]:
                    dic["porva"][
                        2 * cell.i + 2 * (dic["nz"] - cell.k - 1) * dic["mx"]
                    ] = dic["porv"][cell.global_index]
    else:
        for k in range(dic["nz"]):
            for j in range(dic["ny"]):
                for i in range(dic["nx"]):
                    if (
                        dic["porv"][i + j * dic["nx"] + k * dic["nx"] * dic["ny"]] > 0
                        and j == dic["slide"][1]
                    ):
                        for name in dic["props"]:
                            dic[name + "a"][
                                2 * i + 2 * (dic["nz"] - k - 1) * dic["mx"]
                            ] = dic[name][
                                dic["actind"][
                                    i + j * dic["nx"] + k * dic["nx"] * dic["ny"]
                                ]
                            ]
                        if "porv" in dic["props"]:
                            dic["porva"][
                                2 * i + 2 * (dic["nz"] - k - 1) * dic["mx"]
                            ] = dic["porv"][
                                i + j * dic["nx"] + k * dic["nx"] * dic["ny"]
                            ]


def get_xycoords(dic):
    """
    Handle the coordinates from the OPM Grid to the 2D xy-mesh

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for j in range(dic["ny"]):
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [0, 3, 1, 4]):
            dic[f"{k}c"][-1].append(dic["mesh"][j * dic["nx"]][n])
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [0, 3, 1, 4]):
                dic[f"{k}c"][-1].append(dic["mesh"][1 + i + j * dic["nx"]][n])
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [6, 9, 7, 10]):
            dic[f"{k}c"][-1].append(dic["mesh"][j * dic["nx"]][n])
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [6, 9, 7, 10]):
                dic[f"{k}c"][-1].append(dic["mesh"][1 + i + j * dic["nx"]][n])


def map_xycoords(dic):
    """
    Map the properties from the simulations to the 2D slide

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["use"] == "resdata":
        for cell in dic["egrid"].cells():
            if cell.active and cell.k == dic["slide"][2]:
                for name in dic["props"]:
                    dic[name + "a"][2 * cell.i + 2 * cell.j * dic["mx"]] = dic[name][
                        cell.active_index
                    ]
                if "porv" in dic["props"]:
                    dic["porva"][2 * cell.i + 2 * cell.j * dic["mx"]] = dic["porv"][
                        cell.global_index
                    ]
    else:
        for k in range(dic["nz"]):
            for j in range(dic["ny"]):
                for i in range(dic["nx"]):
                    if (
                        dic["porv"][i + j * dic["nx"] + k * dic["nx"] * dic["ny"]] > 0
                        and k == dic["slide"][2]
                    ):
                        for name in dic["props"]:
                            dic[name + "a"][2 * i + 2 * j * dic["mx"]] = dic[name][
                                dic["actind"][
                                    i + j * dic["nx"] + k * dic["nx"] * dic["ny"]
                                ]
                            ]
                        if "porv" in dic["props"]:
                            dic["porva"][2 * i + 2 * j * dic["mx"]] = dic["porv"][
                                i + j * dic["nx"] + k * dic["nx"] * dic["ny"]
                            ]


def get_kws(dic):
    """
    Get the static properties from the INIT file using ResdataFile

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for name in dic["props"]:
        if dic["use"] == "resdata":
            if dic["init"].has_kw(name.upper()):
                dic[name] = np.array(dic["init"].iget_kw(name.upper())[0])
            elif dic["unrst"].has_kw(name.upper()):
                dic[name] = np.array(
                    dic["unrst"].iget_kw(name.upper())[dic["restart"] - 1]
                )
                ntot = len(dic["unrst"].iget_kw(name.upper()))
                dic["dtitle"] = (
                    f", rst {ntot if dic['restart']==0 else dic['restart']} out of {ntot}"
                )
            elif dic["summary"].has_key(name.upper()):
                dic["vsum"] = dic["summary"][name.upper()].values
                dic["time"] = dic["summary"]["TIME"].values
                return
        else:
            if dic["init"].count(name.upper()):
                dic[name] = np.array(dic["init"][name.upper()])
            elif dic["unrst"].count(name.upper()):
                nrst = (
                    dic["restart"] - 1
                    if dic["restart"] > 0
                    else dic["unrst"].count(name.upper()) - 1
                )
                dic[name] = np.array(dic["unrst"][name.upper(), nrst])
                ntot = dic["unrst"].count(name.upper())
                dic["dtitle"] = (
                    f", rst {ntot if dic['restart']==0 else dic['restart']} out of {ntot}"
                )
            elif name.upper() in dic["summary"].keys():
                dic["vsum"] = dic["summary"][name.upper()]
                dic["time"] = dic["summary"]["TIME"]
                return
        dic[name + "a"] = np.ones(dic["mx"] * dic["my"]) * np.nan
    if dic["use"] == "opm":
        dic["porv"] = np.array(dic["init"]["PORV"])
        dic["actind"] = np.cumsum([1 if porv > 0 else 0 for porv in dic["porv"]]) - 1


def get_xy_wells(dic):
    """
    Get the top x,y coordinates from the geological model for the well figure

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["mesh"] = dic["egrid"].export_corners(dic["egrid"].export_index())
    (
        dic["xw"],
        dic["yw"],
    ) = (
        [],
        [],
    )
    for j in range(dic["ny"]):
        dic["xw"].append([])
        dic["yw"].append([])
        for k, n in zip(["x", "x", "y", "y"], [0, 3, 1, 4]):
            dic[f"{k}w"][-1].append(dic["mesh"][j * dic["nx"]][n])
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [0, 3, 1, 4]):
                dic[f"{k}w"][-1].append(dic["mesh"][1 + i + j * dic["nx"]][n])
        dic["xw"].append([])
        dic["yw"].append([])
        for k, n in zip(["x", "x", "y", "y"], [6, 9, 7, 10]):
            dic[f"{k}w"][-1].append(dic["mesh"][j * dic["nx"]][n])
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [6, 9, 7, 10]):
                dic[f"{k}w"][-1].append(dic["mesh"][1 + i + j * dic["nx"]][n])
    for cell in dic["egrid"].cells():
        if cell.active:
            dic["wellsa"][2 * cell.i + 2 * cell.j * dic["wx"]] = len(dic["wellsij"])
    for i, well in enumerate(dic["wellsij"]):
        dic["wellsa"][2 * well[1] + 2 * well[2] * dic["wx"]] = i


def get_wells(dic):
    """
    Using the input deck (.DATA) to read the i,j well locations

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["wellsa"] = np.ones((dic["wx"]) * (dic["wy"])) * np.nan
    wells, sources = False, False
    with open(f"{dic['name']}.DATA", "r", encoding="utf8") as file:
        for row in csv.reader(file):
            nrwo = str(row)[2:-2]
            if wells:
                if len(nrwo.split()) < 2:
                    break
                dic["wellsij"].append(
                    [
                        nrwo.split()[0],
                        int(nrwo.split()[2]) - 1,
                        int(nrwo.split()[3]) - 1,
                    ]
                )
            if sources:
                if len(nrwo.split()) < 2:
                    break
                dic["wellsij"].append(
                    [
                        f"SOURCE{len(dic['wellsij'])+1}",
                        int(nrwo.split()[0]) - 1,
                        int(nrwo.split()[1]) - 1,
                    ]
                )
            if nrwo == "WELSPECS":
                wells = True
            if nrwo == "SOURCE":
                sources = True


def make_2dmaps(dic):
    """
    Method to create the 2d maps using pcolormesh

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    maps = np.ones([dic["my"], dic["mx"]]) * np.nan
    for n, name in enumerate(dic["props"]):
        fig, axis = plt.subplots()
        for i in np.arange(0, dic["my"]):
            maps[i, :] = dic[name + "a"][i * (dic["mx"]) : (i + 1) * (dic["mx"])]
        imag = axis.pcolormesh(
            dic["xc"],
            dic["yc"],
            maps,
            shading="flat",
            cmap=dic["cmaps"][n],
        )
        if dic["scale"] == "yes":
            axis.axis("scaled")
        axis.set_xlabel(f"{dic['xmeaning']} [m]")
        axis.set_ylabel(f"{dic['ymeaning']} [m]")
        extra = ""
        if name == "porv":
            extra = f" (sum={sum(dic[name]):.3e})"
        axis.set_title(name + dic["tslide"] + dic["dtitle"] + extra)
        minc = dic[name][~np.isnan(dic[name])].min()
        maxc = dic[name][~np.isnan(dic[name])].max()
        ntick = 5
        if maxc == minc:
            ntick = 1
        elif name in ["fipnum", "satnum"]:
            ntick = maxc
        divider = make_axes_locatable(axis)
        vect = np.linspace(
            minc,
            maxc,
            ntick,
            endpoint=True,
        )
        fig.colorbar(
            imag,
            cax=divider.append_axes("right", size="5%", pad=0.05),
            orientation="vertical",
            ticks=vect,
            label=dic["units"][n],
            format=dic["format"][n],
        )
        imag.set_clim(
            minc,
            maxc,
        )
        if dic["slide"][2] == -2:
            axis.invert_yaxis()
        axis.set_xticks(
            np.linspace(
                min(min(dic["xc"])),
                max(max(dic["xc"])),
                4,
            )
        )
        axis.set_yticks(
            np.linspace(
                min(min(dic["yc"])),
                max(max(dic["yc"])),
                4,
            )
        )
        if len(dic["xlim"]) > 1:
            axis.set_xlim(dic["xlim"])
        if len(dic["ylim"]) > 1:
            axis.set_ylim(dic["ylim"])
        fig.savefig(
            f"{dic['output']}/{name}_{dic['nslide']}.png", bbox_inches="tight", dpi=300
        )
        plt.close()


def make_wells(dic):
    """
    If there are any well, we only plot them on the top xy view

     Args:
         dic (dict): Global dictionary

     Returns:
         dic (dict): Modified global dictionary

    """
    maps = np.ones([dic["wy"], dic["wx"]]) * np.nan
    fig, axis = plt.subplots()
    for i in np.arange(0, dic["wy"]):
        maps[i, :] = dic["wellsa"][i * (dic["wx"]) : (i + 1) * (dic["wx"])]
    imag = axis.pcolormesh(
        dic["xw"],
        dic["yw"],
        maps,
        shading="flat",
        cmap="nipy_spectral",
    )
    minc = 0
    maxc = len(dic["wellsij"])
    divider = make_axes_locatable(axis)
    vect = np.linspace(
        minc,
        maxc,
        5,
        endpoint=True,
    )
    fig.colorbar(
        imag,
        cax=divider.append_axes("right", size="0%", pad=0.05),
        orientation="vertical",
        ticks=vect,
        format=lambda x, _: "",
    )
    imag.set_clim(
        minc,
        maxc,
    )
    cmap = matplotlib.colormaps["nipy_spectral"]
    colors = cmap(np.linspace(0, 1, len(dic["wellsij"]) + 1))
    for i, well in enumerate(dic["wellsij"]):
        plt.text(0, i, f"{i}-({well[1]+1},{well[2]+1})", c=colors[i], fontweight="bold")
    if dic["scale"] == "yes":
        axis.axis("scaled")
    axis.set_title("Well's location, top view xy (k=1)")
    axis.set_xlabel(f"{dic['xmeaning']} [m]")
    axis.set_ylabel(f"{dic['ymeaning']} [m]")
    axis.set_xticks(
        np.linspace(
            min(min(dic["xw"])),
            max(max(dic["xw"])),
            4,
        )
    )
    axis.set_yticks(
        np.linspace(
            min(min(dic["yw"])),
            max(max(dic["yw"])),
            4,
        )
    )
    if dic["xlim"]:
        axis.set_xlim(dic["xlim"])
    if dic["ylim"]:
        axis.set_ylim(dic["ylim"])
    fig.savefig(f"{dic['output']}/wells.png", bbox_inches="tight", dpi=300)
    plt.close()


def load_parser():
    """Argument options"""
    parser = argparse.ArgumentParser(
        description="plopm, a Python tool to plot 2D surfaces" " from OPM simulations.",
    )
    parser.add_argument(
        "-i",
        "--input",
        default="SPE11B",
        help="The base name of the deck ('SPE11B' by default).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=".",
        help="The base name of the output folder ('.' by default).",
    )
    parser.add_argument(
        "-s",
        "--slide",
        default=",1,",
        help="The slide for the 2d maps of the static variables, e.g,"
        " '10,,' to plot the xz plane on all cells with i=10 (',1,' "
        " by default, i.e., the xz surface at j=1.)",
    )
    parser.add_argument(
        "-z",
        "--scale",
        default="yes",
        help="Scale the 2d maps ('yes' by default)",
    )
    parser.add_argument(
        "-f",
        "--size",
        default=14,
        help="The font size ('14' by default)",
    )
    parser.add_argument(
        "-x",
        "--xlim",
        default="",
        help="Set the lower and upper bounds in the 2D map along x ('' by default).",
    )
    parser.add_argument(
        "-y",
        "--ylim",
        default="",
        help="Set the lower and upper bounds in the 2D map along y ('' by default).",
    )
    parser.add_argument(
        "-u",
        "--use",
        default="resdata",
        help="Use resdata or opm Python libraries ('resdata' by default).",
    )
    parser.add_argument(
        "-v",
        "--variable",
        default="",
        help="Specify the name of the static vairable to plot (e.g.,'depth') ('' by "
        "default, i.e., plotting: porv, permx, permz, poro, fipnum, and satnum).",
    )
    parser.add_argument(
        "-c",
        "--colormap",
        default="",
        help="Specify the colormap (e.g., 'jet') ('' by default, i.e., set by "
        " plopm).",
    )
    parser.add_argument(
        "-n",
        "--numbers",
        default="",
        help="Specify the format for the numbers in the colormap (e.g., "
        "\"lambda x, _: f'{x:.0f}'\") ('' by default, i.e., set by plopm).",
    )
    parser.add_argument(
        "-l",
        "--legend",
        default="",
        help="Specify the units (e.g., \"[m\$^2\$]\") ('' by "
        "default, i.e., set by plopm).",
    )
    parser.add_argument(
        "-r",
        "--restart",
        default="-1",
        help="Restart number to plot the dynamic variable, where 1 corresponds to "
        "the initial one ('-1' by default, i.e., the last restart file).",
    )
    parser.add_argument(
        "-w",
        "--wells",
        default=0,
        help="Plot the xz-position of the wells or sources ('0' by default).",
    )
    return vars(parser.parse_known_args()[0])


def main():
    """Main function"""
    plopm()
