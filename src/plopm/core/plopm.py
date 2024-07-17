#!/usr/bin/env python
# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1702

"""
Script to plot 2D maps of OPM Flow geological models.
"""

import argparse
import csv
from io import StringIO
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

try:
    from opm.io.ecl import EclFile as OpmFile
    from opm.io.ecl import EGrid as OpmGrid
except ImportError:
    print("The Python package opm was not found, using resdata")
try:
    from resdata.resfile import ResdataFile
    from resdata.grid import Grid
except ImportError:
    print("The resdata Python package was not found, using opm")


def plopm():
    """Main function for the plopm executable"""
    cmdargs = load_parser()
    dic = {"name": cmdargs["input"].strip()}
    dic["coords"] = ["x", "y", "z"]
    dic["scale"] = cmdargs["scale"].strip()
    dic["use"] = cmdargs["use"].strip()
    dic["size"] = float(cmdargs["size"])
    dic["xlim"], dic["ylim"] = [], []
    dic["slide"] = np.genfromtxt(StringIO(cmdargs["slide"]), delimiter=",", dtype=int)
    if cmdargs["xlim"]:
        dic["xlim"] = np.genfromtxt(
            StringIO(cmdargs["xlim"]), delimiter=",", dtype=float
        )
    if cmdargs["ylim"]:
        dic["ylim"] = np.genfromtxt(
            StringIO(cmdargs["ylim"]), delimiter=",", dtype=float
        )
    ini_properties(dic)
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
    get_wells(dic)
    get_mesh(dic)
    if dic["slide"][0] > -1:
        dic["tslide"] = f", slide i={dic['slide'][0]}"
        get_yzcoords(dic)
        map_yzcoords(dic)
    elif dic["slide"][1] > -1:
        dic["tslide"] = f", slide j={dic['slide'][1]}"
        get_xzcoords(dic)
        map_xzcoords(dic)
    else:
        dic["tslide"] = f", slide k={dic['slide'][2]}"
        get_xycoords(dic)
        map_xycoords(dic)
    make_2dmaps(dic)
    if dic["wellsij"] and dic["use"] == "resdata":
        get_xy_wells(dic)
        make_wells(dic)


def ini_properties(dic):
    """
    Define the properties to plot

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["props"] = [
        "porv",
        "permx",
        "permy",
        "permz",
        "poro",
        "fipnum",
        "satnum",
    ]
    dic["units"] = [
        r" [m$^3$]",
        " [mD]",
        " [mD]",
        " [mD]",
        " [-]",
        " [-]",
        " [-]",
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
    dic["cmaps"] = [
        "terrain",
        "turbo",
        "turbo",
        "turbo",
        "gnuplot",
        "tab20b",
        "tab20b",
        "jet",
        "gnuplot",
        "coolwarm",
        "coolwarm",
    ]
    dic["title"] = [
        "Pore volume",
        "X-permeability",
        "Y-permeability",
        "Z-permeability",
        "Porosity",
        "Fipnum",
        "Satnum",
    ]
    dic["format"] = [
        lambda x, _: f"{x:.2e}",
        lambda x, _: f"{x:.0f}",
        lambda x, _: f"{x:.0f}",
        lambda x, _: f"{x:.0f}",
        lambda x, _: f"{x:.1f}",
        lambda x, _: f"{x:.0f}",
        lambda x, _: f"{x:.0f}",
    ]
    if dic["use"] == "resdata":
        dic["nx"] = Grid(f"{dic['name']}.EGRID").nx
        dic["ny"] = Grid(f"{dic['name']}.EGRID").ny
        dic["nz"] = Grid(f"{dic['name']}.EGRID").nz
    else:
        dic["nx"] = OpmGrid(f"{dic['name']}.EGRID").dimension[0]
        dic["ny"] = OpmGrid(f"{dic['name']}.EGRID").dimension[1]
        dic["nz"] = OpmGrid(f"{dic['name']}.EGRID").dimension[2]


def get_yzcoords(dic):
    """
    Handle the coordinates from the OPM Grid to the 2D yz-mesh

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    n_k = dic["slide"][0]
    for j in range(dic["nz"]):
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [1, 7, 2, 8]):
            dic[f"{k}c"][-1].append(
                dic["mesh"][(dic["nz"] - j - 1) * dic["nx"] * dic["ny"]][n] + n_k
            )
        for i in range(dic["ny"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [1, 7, 2, 8]):
                dic[f"{k}c"][-1].append(
                    dic["mesh"][
                        (i + 1) * dic["nx"]
                        + (dic["nz"] - j - 1) * dic["nx"] * dic["ny"]
                    ][n]
                    + n_k
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [13, 19, 14, 20]):
            dic[f"{k}c"][-1].append(
                dic["mesh"][(dic["nz"] - j - 1) * dic["nx"] * dic["ny"]][n] + n_k
            )
        for i in range(dic["ny"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [13, 19, 14, 20]):
                dic[f"{k}c"][-1].append(
                    dic["mesh"][
                        (i + 1) * dic["nx"]
                        + (dic["nz"] - j - 1) * dic["nx"] * dic["ny"]
                    ][n]
                    + n_k
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
        for cell in Grid(f"{dic['name']}.EGRID").cells():
            if cell.active and cell.i == dic["slide"][0]:
                for name in dic["props"]:
                    dic[name + "a"][
                        2 * cell.j + 2 * (dic["nz"] - cell.k - 1) * dic["mx"]
                    ] = dic[name][cell.active_index]
                dic["porva"][2 * cell.j + 2 * (dic["nz"] - cell.k - 1) * dic["mx"]] = (
                    dic["porv"][cell.global_index]
                )
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
                        dic["porva"][2 * j + 2 * (dic["nz"] - k - 1) * dic["mx"]] = dic[
                            "porv"
                        ][i + j * dic["nx"] + k * dic["nx"] * dic["ny"]]


def get_mesh(dic):
    """
    Read the coordinates using either opm or resdata

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["use"] == "resdata":
        dic["mesh"] = Grid(f"{dic['name']}.EGRID").export_corners(
            Grid(f"{dic['name']}.EGRID").export_index()
        )
    else:
        dic["mesh"] = []
        for k in range(dic["nz"]):
            for j in range(dic["ny"]):
                for i in range(dic["nx"]):
                    dic["mesh"].append([])
                    for n in range(8):
                        dic["mesh"][-1] += [
                            OpmGrid(f"{dic['name']}.EGRID").xyz_from_ijk(i, j, k)[0][n],
                            OpmGrid(f"{dic['name']}.EGRID").xyz_from_ijk(i, j, k)[1][n],
                            OpmGrid(f"{dic['name']}.EGRID").xyz_from_ijk(i, j, k)[2][n],
                        ]
    (
        dic["xc"],
        dic["yc"],
    ) = (
        [],
        [],
    )


def get_xzcoords(dic):
    """
    Handle the coordinates from the OPM Grid to the 2D xz-mesh

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    n_k = dic["slide"][1] * dic["nx"]
    for j in range(dic["nz"]):
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [0, 3, 2, 5]):
            dic[f"{k}c"][-1].append(
                dic["mesh"][(dic["nz"] - j - 1) * dic["nx"] * dic["ny"]][n] + n_k
            )
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [0, 3, 2, 5]):
                dic[f"{k}c"][-1].append(
                    dic["mesh"][1 + i + (dic["nz"] - j - 1) * dic["nx"] * dic["ny"]][n]
                    + n_k
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [12, 15, 14, 17]):
            dic[f"{k}c"][-1].append(
                dic["mesh"][(dic["nz"] - j - 1) * dic["nx"] * dic["ny"]][n] + n_k
            )
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [12, 15, 14, 17]):
                dic[f"{k}c"][-1].append(
                    dic["mesh"][1 + i + (dic["nz"] - j - 1) * dic["nx"] * dic["ny"]][n]
                    + n_k
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
        for cell in Grid(f"{dic['name']}.EGRID").cells():
            if cell.active and cell.j == dic["slide"][1]:
                for name in dic["props"]:
                    dic[name + "a"][
                        2 * cell.i + 2 * (dic["nz"] - cell.k - 1) * dic["mx"]
                    ] = dic[name][cell.active_index]
                dic["porva"][2 * cell.i + 2 * (dic["nz"] - cell.k - 1) * dic["mx"]] = (
                    dic["porv"][cell.global_index]
                )
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
                        dic["porva"][2 * i + 2 * (dic["nz"] - k - 1) * dic["mx"]] = dic[
                            "porv"
                        ][i + j * dic["nx"] + k * dic["nx"] * dic["ny"]]


def get_xycoords(dic):
    """
    Handle the coordinates from the OPM Grid to the 2D xy-mesh

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    n_k = dic["slide"][2] * dic["nx"] * dic["ny"]
    for j in range(dic["ny"]):
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [0, 3, 1, 4]):
            dic[f"{k}c"][-1].append(dic["mesh"][j * dic["nx"]][n] + n_k)
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [0, 3, 1, 4]):
                dic[f"{k}c"][-1].append(dic["mesh"][1 + i + j * dic["nx"]][n] + n_k)
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [6, 9, 7, 10]):
            dic[f"{k}c"][-1].append(dic["mesh"][j * dic["nx"]][n] + n_k)
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [6, 9, 7, 10]):
                dic[f"{k}c"][-1].append(dic["mesh"][1 + i + j * dic["nx"]][n] + n_k)


def map_xycoords(dic):
    """
    Map the properties from the simulations to the 2D slide

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["use"] == "resdata":
        for cell in Grid(f"{dic['name']}.EGRID").cells():
            if cell.active and cell.k == dic["slide"][2]:
                for name in dic["props"]:
                    dic[name + "a"][2 * cell.i + 2 * cell.j * dic["mx"]] = dic[name][
                        cell.active_index
                    ]
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
            dic[name] = np.array(
                ResdataFile(f"{dic['name']}.INIT").iget_kw(name.upper())[0]
            )
        else:
            dic[name] = np.array(OpmFile(f"{dic['name']}.INIT")[name.upper()])
        dic[name + "a"] = np.ones(dic["mx"] * dic["my"]) * np.nan
    if dic["use"] == "opm":
        dic["actind"] = np.cumsum([1 if porv > 0 else 0 for porv in dic["porv"]]) - 1


def get_xy_wells(dic):
    """
    Get the top x,y coordinates from the geological model for the well figure

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["mesh"] = Grid(f"{dic['name']}.EGRID").export_corners(
        Grid(f"{dic['name']}.EGRID").export_index()
    )
    (
        dic["xw"],
        dic["yw"],
    ) = (
        [],
        [],
    )
    n_k = dic["slide"][2] * dic["nx"] * dic["ny"]
    for j in range(dic["ny"]):
        dic["xw"].append([])
        dic["yw"].append([])
        for k, n in zip(["x", "x", "y", "y"], [0, 3, 1, 4]):
            dic[f"{k}w"][-1].append(dic["mesh"][j * dic["nx"]][n] + n_k)
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [0, 3, 1, 4]):
                dic[f"{k}w"][-1].append(dic["mesh"][1 + i + j * dic["nx"]][n] + n_k)
        dic["xw"].append([])
        dic["yw"].append([])
        for k, n in zip(["x", "x", "y", "y"], [6, 9, 7, 10]):
            dic[f"{k}w"][-1].append(dic["mesh"][j * dic["nx"]][n] + n_k)
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [6, 9, 7, 10]):
                dic[f"{k}w"][-1].append(dic["mesh"][1 + i + j * dic["nx"]][n] + n_k)
    for cell in Grid(f"{dic['name']}.EGRID").cells():
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
    dic["wellsij"] = []
    wells = False
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
            if nrwo == "WELSPECS":
                wells = True


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
        if len(dic["xlim"]) > 1:
            axis.set_xlim(dic["xlim"])
        if len(dic["ylim"]) > 1:
            axis.set_ylim(dic["ylim"])
        axis.set_xlabel(f"{dic['xmeaning']} [m]")
        axis.set_ylabel(f"{dic['ymeaning']} [m]")
        extra = ""
        if name == "porv":
            extra = f" (sum={sum(dic[name]):.3e})"
        axis.set_title(dic["title"][n] + dic["tslide"] + extra)
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
        if dic["slide"][2] == -1:
            axis.invert_yaxis()
        fig.savefig(f"{name}.png", bbox_inches="tight", dpi=300)
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
    axis.axis("scaled")
    axis.set_title("Well's location, top view xy (k=0)")
    if dic["xlim"]:
        axis.set_xlim(dic["xlim"])
    if dic["ylim"]:
        axis.set_ylim(dic["ylim"])
    axis.set_xlabel(f"{dic['xmeaning']} [m]")
    axis.set_ylabel(f"{dic['ymeaning']} [m]")
    fig.savefig("wells.png", bbox_inches="tight", dpi=300)
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
        default="output",
        help="The base name of the output folder ('output' by default).",
    )
    parser.add_argument(
        "-s",
        "--slide",
        default=",0,",
        help="The slide for the 2d maps of the static variables, e.g,"
        " '10,,' to plot the xz plane on all cells with i=10+1 (',0,' "
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
    return vars(parser.parse_known_args()[0])


def main():
    """Main function"""
    plopm()
