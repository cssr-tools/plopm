# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions to write the PNGs figures.
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


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


def make_2dmaps(dic):
    """
    Method to create the 2d maps using pcolormesh

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    maps = np.ones([dic["my"], dic["mx"]]) * np.nan
    if dic["well"] == 1:
        dic["props"] += ["wells"]
    elif dic["grid"] == 1:
        dic["props"] += ["grid"]
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
        ntick = 5
        if dic["well"] != 1 and dic["grid"] != 1:
            minc = dic[name][~np.isnan(dic[name])].min()
            maxc = dic[name][~np.isnan(dic[name])].max()
            if maxc == minc:
                ntick = 1
            elif name in ["fipnum", "satnum"]:
                ntick = maxc
        else:
            minc = 0
            maxc = len(dic["wells"])
        divider = make_axes_locatable(axis)
        vect = np.linspace(
            minc,
            maxc,
            ntick,
            endpoint=True,
        )
        if dic["well"] != 1 and dic["grid"] != 1:
            fig.colorbar(
                imag,
                cax=divider.append_axes("right", size="5%", pad=0.05),
                orientation="vertical",
                ticks=vect,
                label=dic["units"][n],
                format=dic["format"][n],
            )
        else:
            handle_well_or_grid(dic, fig, imag, divider, vect)
        imag.set_clim(
            minc,
            maxc,
        )
        handle_axis(dic, axis, name)
        fig.savefig(
            f"{dic['output']}/{name}_{dic['nslide']}.png", bbox_inches="tight", dpi=300
        )
        plt.close()


def handle_axis(dic, axis, name):
    """
    Method to handle the figure axis

    Args:
        dic (dict): Global dictionary\n
        axis (class): Axis object\n
        name (str): Property to plot

    Returns:
        axis (class): Modified axis object

    """
    if dic["scale"] == "yes":
        axis.axis("scaled")
    axis.set_xlabel(f"{dic['xmeaning']} [m]")
    axis.set_ylabel(f"{dic['ymeaning']} [m]")
    extra = ""
    if name == "porv":
        extra = f" (sum={sum(dic[name]):.3e})"
    axis.set_title(name + dic["tslide"] + dic["dtitle"] + extra)
    if name == "grid":
        axis.set_title(
            f"Grid = [{dic['nx']},{dic['ny']},{dic['nz']}], "
            + f"Total no. active cells = {max(dic['actind'])+1}"
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


def handle_well_or_grid(dic, fig, imag, divider, vect):
    """
    Method to create the 2d maps using pcolormesh

    Args:
        dic (dict): Global dictionary\n
        fig (class): Figure object\n
        imag (class): Actual plot object\n
        divider (class): Object for the color bar axis\n
        vect (array): Floats for the labels in the color bar

    Returns:
        fig (class): Modified figure object\n
        plt (class): Modified plotting object\n

    """
    fig.colorbar(
        imag,
        cax=divider.append_axes("right", size="0%", pad=0.05),
        orientation="vertical",
        ticks=vect,
        format=lambda x, _: "",
    )
    cmap = matplotlib.colormaps["nipy_spectral"]
    colors = cmap(np.linspace(0, 1, len(dic["wells"]) + 1))
    if len(dic["wells"]) < 20:
        for i, well in enumerate(dic["wells"]):
            if well[2] != well[3]:
                plt.text(
                    0,
                    i,
                    f"{i}-({well[0]+1},{well[1]+1},{well[2]+1}-{well[3]+1})",
                    c=colors[i],
                    fontweight="bold",
                )
            else:
                plt.text(
                    0,
                    i,
                    f"{i}-({well[0]+1},{well[1]+1},{well[2]+1})",
                    c=colors[i],
                    fontweight="bold",
                )
    else:
        for i, well in zip(
            [0, len(dic["wells"]) - 1], [dic["wells"][0], dic["wells"][-1]]
        ):
            if well[2] != well[3]:
                plt.text(
                    0,
                    i,
                    f"{i}-({well[0]+1},{well[1]+1},{well[2]+1}-{well[3]+1})",
                    c=colors[i],
                    fontweight="bold",
                )
            else:
                plt.text(
                    0,
                    i,
                    f"{i}-({well[0]+1},{well[1]+1},{well[2]+1})",
                    c=colors[i],
                    fontweight="bold",
                )
