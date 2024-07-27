# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W3301

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
    if (
        len(dic["cmaps"][0].split(",")) == len(dic["names"])
        and dic["cmaps"][0] != "gnuplot"
    ):
        dic["colors"] = dic["cmaps"][0].split(",")
    if len(dic["linsty"].split(";")) == len(dic["names"]) and dic["linsty"]:
        dic["linestyle"] = dic["linsty"].split(";")
    plt.rcParams.update({"axes.grid": True})
    fig, axis = plt.subplots()
    min_t, min_v = min(dic["time"][0]), min(dic["vsum"][0])
    max_t, max_v = max(dic["time"][0]), max(dic["vsum"][0])
    for i, name in enumerate(dic["names"]):
        label = name
        if len(name.split("/")) > 1:
            label = name.split("/")[-2] + "/" + name.split("/")[-1]
        axis.step(
            dic["time"][i],
            dic["vsum"][i],
            color=dic["colors"][i],
            ls=dic["linestyle"][i],
            label=label,
        )
        min_t = min(min_t, min(dic["time"][i]))
        min_v = min(min_v, min(dic["vsum"][i]))
        max_t = max(max_t, max(dic["time"][i]))
        max_v = max(max_v, max(dic["vsum"][i]))
    axis.set_ylabel(dic["props"][0])
    axis.set_xlabel("Time [s]")
    axis.set_xlim([min_t, max_t])
    axis.set_ylim([min_v, max_v])
    axis.set_xticks(
        np.linspace(
            min_t,
            max_t,
            4,
        )
    )
    axis.set_yticks(
        np.linspace(
            min_v,
            max_v,
            4,
        )
    )
    axis.legend()
    if dic["titles"] != "":
        axis.set_title(dic["titles"])
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
            if len(dic["bounds"]) == 2:
                minc = float(dic["bounds"][0][1:])
                maxc = float(dic["bounds"][1][:-1])
            elif len(dic["names"]) == 2:
                minmax = max(abs(maxc), abs(minc))
                minc = -minmax
                maxc = minmax
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
    if dic["titles"] != "":
        axis.set_title(dic["titles"])
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
