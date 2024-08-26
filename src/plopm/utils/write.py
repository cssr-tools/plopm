# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W3301,W0123,R0912,R0915,R0914

"""
Utiliy functions to write the PNGs figures.
"""

import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
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
    if dic["axgrid"] == 1:
        plt.rcParams.update({"axes.grid": True})
    fig, axis = plt.subplots()
    min_t, min_v = min(dic["time"][0]), min(dic["vsum"][0])
    max_t, max_v = max(dic["time"][0]), max(dic["vsum"][0])
    for i, name in enumerate(dic["names"]):
        label = name
        if len(name.split("/")) > 1:
            label = name.split("/")[-2] + "/" + name.split("/")[-1]
        if dic["labels"][0] != "":
            label = dic["labels"][i]
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
    axis.set_ylabel(dic["props"][0] + dic["units"][0])
    axis.set_ylim([min_v, max_v])
    axis.set_xlabel(dic["tunit"])
    if dic["xlabel"]:
        axis.set_xlabel(dic["xlabel"])
    if dic["ylabel"]:
        axis.set_ylabel(dic["ylabel"])
    if len(dic["xlim"]) > 1:
        axis.set_xlim([float(dic["xlim"][0][1:]), float(dic["xlim"][1][:-1])])
        xlabels = np.linspace(
            float(dic["xlim"][0][1:]),
            float(dic["xlim"][1][:-1]),
            dic["xlnum"],
        )
    elif dic["times"] != "dates":
        axis.set_xlim([min_t, max_t])
        xlabels = np.linspace(
            min_t,
            max_t,
            dic["xlnum"],
        )
    if len(dic["ylim"]) > 1:
        axis.set_ylim([float(dic["ylim"][0][1:]), float(dic["ylim"][1][:-1])])
        ylabels = np.linspace(
            float(dic["ylim"][0][1:]),
            float(dic["ylim"][1][:-1]),
            dic["ylnum"],
        )
    else:
        axis.set_ylim([min_v, max_v])
        ylabels = np.linspace(
            min_v,
            max_v,
            dic["ylnum"],
        )
    if dic["times"] != "dates":
        if dic["xformat"]:
            func = "f'{x:" + dic["xformat"] + "}'"
            axis.set_xticks([float(eval(func)) for x in xlabels])
            axis.set_xticklabels([eval(func) for x in xlabels])
        else:
            axis.set_xticks(xlabels)
    if dic["yformat"]:
        func = "f'{y:" + dic["yformat"] + "}'"
        axis.set_yticks([float(eval(func)) for y in ylabels])
        axis.set_yticklabels([eval(func) for y in ylabels])
    else:
        axis.set_yticks(ylabels)
    axis.legend()
    if dic["titles"] != "":
        axis.set_title(dic["titles"])
    fig.savefig(
        f"{dic['output']}/{dic['save'] if dic['save'] else dic['variable']}.png",
        bbox_inches="tight",
        dpi=dic["dpi"],
    )
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
        ntick = 5
        ncolor = dic["units"][n]
        if dic["well"] != 1 and dic["grid"] != 1:
            if dic["global"] == 0:
                minc = maps[~np.isnan(maps)].min()
                maxc = maps[~np.isnan(maps)].max()
            else:
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
                ntick = int(maxc)
        else:
            minc = 0
            maxc = len(dic["wells"])
        if dic["cnum"]:
            ntick = int(dic["cnum"])
        if dic["clabel"]:
            ncolor = dic["clabel"]
        cmap = matplotlib.colormaps.get_cmap(dic["cmaps"][n])
        if dic["ncolor"] != "w":
            cmap.set_bad(color=dic["ncolor"])
        if dic["grid"] == 1 and dic["well"] != 1:
            imag = axis.pcolormesh(
                dic["xc"],
                dic["yc"],
                maps,
                facecolors="none",
                edgecolors="black",
                lw=0.001,
            )
        elif dic["log"] == 0:
            imag = axis.pcolormesh(
                dic["xc"],
                dic["yc"],
                maps,
                shading="flat",
                cmap=cmap,
            )
        else:
            imag = axis.pcolormesh(
                dic["xc"],
                dic["yc"],
                maps,
                shading="flat",
                cmap=cmap,
                norm=colors.LogNorm(vmin=minc, vmax=maxc),
            )
        divider = make_axes_locatable(axis)
        vect = np.linspace(
            minc,
            maxc,
            ntick,
            endpoint=True,
        )
        if dic["well"] != 1 and dic["grid"] != 1 and dic["rm"][2] == 0:
            if dic["log"] == 0:
                fig.colorbar(
                    imag,
                    cax=divider.append_axes("right", size="5%", pad=0.05),
                    orientation="vertical",
                    ticks=vect,
                    label=ncolor,
                    format=dic["format"][n],
                )
            else:
                if minc == 0:
                    print(
                        f"It is not possible to plot {name} in log scale"
                        " since there are 0 values. Try without log."
                    )
                    sys.exit()
                fig.colorbar(
                    imag,
                    cax=divider.append_axes("right", size="5%", pad=0.05),
                    orientation="vertical",
                    label=ncolor,
                )
        else:
            handle_well_or_grid(dic, fig, imag, divider, vect)
        if dic["rm"][2] == 0:
            imag.set_clim(
                minc,
                maxc,
            )
        handle_axis(dic, axis, name)
        if dic["xlabel"] and dic["rm"][1] == 0:
            axis.set_xlabel(dic["xlabel"])
        elif dic["rm"][1] == 0:
            axis.set_xlabel(f"{dic['xmeaning']+dic['xunit']}")
        if dic["ylabel"] and dic["rm"][0] == 0:
            axis.set_ylabel(dic["ylabel"])
        elif dic["rm"][0] == 0:
            axis.set_ylabel(f"{dic['ymeaning']+dic['yunit']}")
        # axis.spines['left'].set_color('white')
        # axis.yaxis.label.set_color('white')
        # axis.tick_params(axis='y', colors='white')
        # plt.setp(axis.get_xticklabels(), visible=False)
        # axis.spines['bottom'].set_color('white')
        # axis.xaxis.label.set_color('white')
        # axis.tick_params(axis='x', colors='white')
        if dic["rm"][2] == 1:
            fig.delaxes(fig.axes[1])
        if dic["rm"][1] == 1:
            axis.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
        if dic["rm"][0] == 1:
            axis.tick_params(axis="y", which="both", left=False, labelleft=False)
        fig.set_facecolor(dic["fc"])
        name = f"{name}_{dic['nslide']}"
        fig.savefig(
            f"{dic['output']}/{dic['save'] if dic['save'] else name}.png",
            bbox_inches="tight",
            dpi=dic["dpi"],
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
    if dic["scale"] == 1:
        axis.axis("scaled")
    extra = ""
    if name == "porv":
        extra = f" (sum={sum(dic[name]):.3e})"
    if dic["rm"][3] == 0:
        axis.set_title(name + dic["tslide"] + dic["dtitle"] + extra)
    if name == "grid" and dic["rm"][3] == 0:
        axis.set_title(
            f"Grid = [{dic['nx']},{dic['ny']},{dic['nz']}], "
            + f"Total no. active cells = {max(dic['actind'])+1}"
        )
    if dic["titles"] != "" and dic["rm"][3] == 0:
        axis.set_title(dic["titles"])
    if dic["slide"][2] == -2:
        axis.invert_yaxis()
    if len(dic["xlim"]) > 1 and dic["rm"][1] == 0:
        axis.set_xlim([float(dic["xlim"][0][1:]), float(dic["xlim"][1][:-1])])
        xlabels = np.linspace(
            float(dic["xlim"][0][1:]),
            float(dic["xlim"][1][:-1]),
            dic["xlnum"],
        )
    else:
        xlabels = np.linspace(
            min(min(dic["xc"])) * dic["xskl"],
            max(max(dic["xc"])) * dic["xskl"],
            dic["xlnum"],
        )
    if dic["xformat"] and dic["rm"][1] == 0:
        func = "f'{x:" + dic["xformat"] + "}'"
        axis.set_xticks([float(eval(func)) / dic["xskl"] for x in xlabels])
        axis.set_xticklabels([eval(func) for x in xlabels])
    elif dic["rm"][1] == 0:
        axis.set_xticks(xlabels / dic["xskl"])
        if dic["xskl"] != 1:
            axis.set_xticklabels(xlabels)
    if len(dic["ylim"]) > 1 and dic["rm"][0] == 0:
        axis.set_ylim([float(dic["ylim"][0][1:]), float(dic["ylim"][1][:-1])])
        ylabels = np.linspace(
            float(dic["ylim"][0][1:]),
            float(dic["ylim"][1][:-1]),
            dic["ylnum"],
        )
    else:
        ylabels = np.linspace(
            min(min(dic["yc"])) * dic["yskl"],
            max(max(dic["yc"])) * dic["yskl"],
            dic["ylnum"],
        )
    if dic["yformat"] and dic["rm"][0] == 0:
        func = "f'{y:" + dic["yformat"] + "}'"
        axis.set_yticks([float(eval(func)) / dic["yskl"] for y in ylabels])
        axis.set_yticklabels([eval(func) for y in ylabels])
    elif dic["rm"][0] == 0:
        axis.set_yticks(ylabels / dic["yskl"])
        if dic["yskl"] != 1:
            axis.set_yticklabels(ylabels)


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
    colour = cmap(np.linspace(0, 1, len(dic["wells"]) + 1))
    if len(dic["wells"]) < 20:
        for i, well in enumerate(dic["wells"]):
            if well[2] != well[3]:
                plt.text(
                    0,
                    i,
                    f"{i}-({well[0]+1},{well[1]+1},{well[2]+1}-{well[3]+1})",
                    c=colour[i],
                    fontweight="bold",
                )
            else:
                plt.text(
                    0,
                    i,
                    f"{i}-({well[0]+1},{well[1]+1},{well[2]+1})",
                    c=colour[i],
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
                    c=colour[i],
                    fontweight="bold",
                )
            else:
                plt.text(
                    0,
                    i,
                    f"{i}-({well[0]+1},{well[1]+1},{well[2]+1})",
                    c=colour[i],
                    fontweight="bold",
                )
