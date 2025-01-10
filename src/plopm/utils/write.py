# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W3301,W0123,R0912,R0915,R0914,R1702,W0611,R0913,R0917,C0302,C0115

"""
Utiliy functions to write the PNGs figures.
"""

import sys
import colorcet
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors
from matplotlib.ticker import LogFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
from plopm.utils.readers import read_summary, get_quantity, get_readers, initialize_time
from plopm.utils.initialization import ini_slides
from plopm.utils.mapping import (
    handle_slide_x,
    handle_slide_y,
    handle_slide_z,
    rotate_grid,
    map_xzcoords,
    map_xycoords,
    map_yzcoords,
)


def make_summary(dic):
    """
    Plot the summary variable

    Args:
        cmdargs (dict): Command arguments

    Returns:
        None

    """
    dic["fig"], dic["axis"] = [], []
    if dic["subfigs"][0]:
        dic["fig"], dic["axis"] = plt.subplots(
            int(dic["subfigs"][0]), int(dic["subfigs"][1]), layout="compressed"
        )
    for j, quan in enumerate(dic["vrs"]):
        k = j
        if not dic["subfigs"][0]:
            dic["fig"], dic["axis"] = plt.subplots(1, 1, layout="compressed")
            dic["axis"] = np.array([dic["axis"]])
            k = 0
        dic["axis"].flat[k].grid(int(dic["axgrid"][j]))
        for i, name in enumerate(dic["names"][j]):
            jj = j
            if len(dic["vrs"]) == len(dic["names"][0]) and not dic["subfigs"][0]:
                jj = i
                quan = dic["vrs"][i]
            time, var, tunit, vunit = read_summary(
                dic, name, quan, dic["tunits"][jj], float(dic["avar"][jj])
            )
            label = name
            if len(name.split("/")) > 1:
                label = name.split("/")[-2] + "/" + name.split("/")[-1]
            if dic["labels"][0][0]:
                label = dic["labels"][jj][i]
            dic["axis"].flat[k].step(
                time,
                var,
                color=dic["colors"][jj][i],
                ls=dic["linestyle"][jj][i],
                label=label,
                lw=float(dic["lw"][jj][i]),
            )
            if i == 0:
                min_t, min_v = min(time), min(var)
                max_t, max_v = max(time), max(var)
            else:
                min_t = min(min_t, min(time))
                min_v = min(min_v, min(var))
                max_t = max(max_t, max(time))
                max_v = max(max_v, max(var))
        dic["axis"].flat[k].set_ylabel(quan + vunit)
        dic["axis"].flat[k].set_ylim([min_v, max_v])
        if dic["delax"] == 0 or k + int(dic["subfigs"][1]) >= len(dic["vrs"]):
            dic["axis"].flat[k].set_xlabel(tunit)
            if dic["xlabel"][0]:
                dic["axis"].flat[k].set_xlabel(dic["xlabel"][j])
        if dic["ylabel"][0]:
            dic["axis"].flat[k].set_ylabel(dic["ylabel"][j])
        if len(dic["xlim"]) > 1:
            dic["axis"].flat[k].set_xlim(
                [float(dic["xlim"][j][0][1:]), float(dic["xlim"][j][1][:-1])]
            )
            xlabels = np.linspace(
                float(dic["xlim"][j][0][1:]),
                float(dic["xlim"][j][1][:-1]),
                int(dic["xlnum"][j]),
            )
        elif tunit != "Dates":
            dic["axis"].flat[k].set_xlim([min_t, max_t])
            xlabels = np.linspace(
                min_t,
                max_t,
                int(dic["xlnum"][j]),
            )
        if len(dic["ylim"]) > 1:
            dic["axis"].flat[k].set_ylim(
                [float(dic["ylim"][j][0][1:]), float(dic["ylim"][j][1][:-1])]
            )
            ylabels = np.linspace(
                float(dic["ylim"][j][0][1:]),
                float(dic["ylim"][j][1][:-1]),
                int(dic["ylnum"][j]),
            )
        else:
            dic["axis"].flat[k].set_ylim([min_v, max_v])
            ylabels = np.linspace(
                min_v,
                max_v,
                int(dic["ylnum"][j]),
            )
        if dic["xlog"][j] == "1":
            dic["axis"].flat[k].set_xscale("log")
        else:
            if tunit != "Dates":
                if dic["xformat"][0]:
                    func = "f'{x:" + dic["xformat"][j] + "}'"
                    dic["axis"].flat[k].set_xticks([float(eval(func)) for x in xlabels])
                    dic["axis"].flat[k].set_xticklabels([eval(func) for x in xlabels])
                else:
                    dic["axis"].flat[k].set_xticks(xlabels)
        if dic["ylog"][j] == "1":
            dic["axis"].flat[k].set_yscale("log")
        else:
            if dic["yformat"][0]:
                func = "f'{y:" + dic["yformat"][j] + "}'"
                dic["axis"].flat[k].set_yticks([float(eval(func)) for y in ylabels])
                dic["axis"].flat[k].set_yticklabels([eval(func) for y in ylabels])
            else:
                dic["axis"].flat[k].set_yticks(ylabels)
        if dic["loc"][j] != "empty":
            dic["axis"].flat[k].legend(loc=dic["loc"][j])
        if dic["titles"][j] != "0":
            dic["axis"].flat[k].set_title(dic["titles"][j])
        if dic["delax"] == 1 and k + int(dic["subfigs"][1]) < len(dic["vrs"]):
            dic["axis"].flat[k].tick_params(
                axis="x", which="both", bottom=False, labelbottom=False
            )
        if len(dic["vrs"]) == len(dic["names"][0]) and not dic["subfigs"][0]:
            dic["fig"].savefig(
                f"{dic['output']}/{dic['save'][j] if dic['save'][j] else quan}.png",
                bbox_inches="tight",
                dpi=int(dic["dpi"][j]),
            )
            sys.exit()
        elif (
            not dic["subfigs"][0] and len(dic["vrs"]) != len(dic["names"][0])
        ) or j == len(dic["vrs"]) - 1:
            if (
                len(dic["loc"]) == j + 2
                and j != 0
                and len(dic["axis"].flat) - len(dic["vrs"]) > 0
            ):
                for jj, qua in enumerate(dic["vrs"][: dic["numc"]]):
                    for i, name in enumerate(dic["names"][jj]):
                        time, var, tunit, vunit = read_summary(
                            dic, name, qua, dic["tunits"][jj], float(dic["avar"][jj])
                        )
                        label = name
                        if len(name.split("/")) > 1:
                            label = name.split("/")[-2] + "/" + name.split("/")[-1]
                        if dic["labels"][0][0]:
                            label = dic["labels"][jj][i]
                        dic["axis"].flat[-1].step(
                            time,
                            var,
                            color=dic["colors"][jj][i],
                            ls=dic["linestyle"][jj][i],
                            label=label,
                            lw=float(dic["lw"][jj][i]),
                        )
                dic["axis"].flat[-1].axis("off")
                dic["axis"].flat[-1].legend(loc=dic["loc"][-1])
                for line in dic["axis"].flat[-1].get_lines():
                    line.remove()
                for l in range(len(dic["axis"].flat) - len(dic["vrs"]) - 1):
                    dic["fig"].delaxes(dic["axis"].flat[-2 - l])
            else:
                for l in range(len(dic["axis"].flat) - len(dic["vrs"])):
                    dic["fig"].delaxes(dic["axis"].flat[-1 - l])
            quan = quan.replace(" / ", "_over_")
            dic["fig"].savefig(
                f"{dic['output']}/{dic['save'][j] if dic['save'][j] else quan}.png",
                bbox_inches="tight",
                dpi=int(dic["dpi"][j]),
            )
    plt.close()


def prepare_maps(dic, n):
    """
    Get the spatial coordinates

    Args:
        dic (dict): Global dictionary\n
        n (int): Number of deck

    Returns:
        dic (dict): Modified global dictionary

    """
    if len(dic["deck"].split("/")) > 1:
        dic["deckn"] = (dic["deck"].split("/")[-1]).lower()
    else:
        dic["deckn"] = dic["deck"].lower()
    dic["xc"], dic["yc"], dic["abssum"] = [], [], 0.0
    get_readers(dic)
    ini_slides(dic, n)
    if dic["slide"][n][0][0] > -1:
        handle_slide_x(dic, n)
    elif dic["slide"][n][1][0] > -1:
        handle_slide_y(dic, n)
    else:
        handle_slide_z(dic, n)
    if int(dic["rotate"][n]) != 0 or dic["translate"][n] != ["[0", "0]"]:
        rotate_grid(dic, n)


def make_maps(dic):
    """
    Method to create the 2d maps using pcolormesh

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["fig"], dic["axis"] = [], []
    dic["skip"] = 0
    if (
        dic["subfigs"][0]
        and len(dic["vrs"]) > 1
        and len(dic["restart"]) == 1
        and len(dic["names"][0]) == 1
    ):
        dic["skip"] = 1
    if dic["subfigs"][0]:
        dic["fig"], dic["axis"] = plt.subplots(
            int(dic["subfigs"][0]), int(dic["subfigs"][1])
        )
        dic["sub0"] = int(dic["subfigs"][0])
        dic["sub1"] = int(dic["subfigs"][1])
    else:
        dic["fig"], dic["axis"] = plt.subplots(1, 1, layout="compressed")
        dic["sub0"] = 1
        dic["sub1"] = 1
    dic["original_loc"], dic["cb"] = [], []
    dic["minc"], dic["maxc"] = [1e20], [-1e20]
    if dic["subfigs"][0] and dic["mode"] == "gif" and len(dic["names"][0]) > 1:
        find_min_max(dic)
        dic["fig"], dic["axis"] = plt.subplots(
            int(dic["subfigs"][0]), int(dic["subfigs"][1]), layout="compressed"
        )
        dic["axis"] = np.array([dic["axis"]])
        for _ in range(len(dic["axis"].flat)):
            dic["original_loc"].append(dic["axis"].flat[0].get_axes_locator())
            dic["cb"].append("")
        for l in range(len(dic["axis"].flat) - len(dic["names"][0])):
            dic["fig"].delaxes(dic["axis"].flat[-1 - l])
        im_ani = animation.FuncAnimation(
            dic["fig"],
            mapit,
            fargs=(dic, 0),
            frames=len(dic["restart"]),
            interval=dic["interval"],
            blit=False,
            repeat=False,
        )
        if dic["loop"] == 0:
            im_ani.save(
                f"{dic['output']}/{dic['vrs'][0]}.gif", extra_args=["-loop", "-1"]
            )
        else:
            im_ani.save(f"{dic['output']}/{dic['vrs'][0]}.gif")
    elif dic["subfigs"][0] and dic["mode"] == "gif" and len(dic["vrs"]) > 1:
        find_min_max(dic)
        if len(dic["restart"]) > 1:
            dic["fig"], dic["axis"] = plt.subplots(
                int(dic["subfigs"][0]), int(dic["subfigs"][1])
            )
        dic["axis"] = np.array([dic["axis"]])
        plt.tight_layout(pad=1.7)
        dic["deck"] = dic["names"][0][0]
        dic["ndeck"] = 0
        prepare_maps(dic, 0)
        for _ in range(len(dic["axis"].flat)):
            dic["original_loc"].append(dic["axis"].flat[0].get_axes_locator())
            dic["cb"].append("")
        for l in range(len(dic["axis"].flat) - len(dic["vrs"])):
            dic["fig"].delaxes(dic["axis"].flat[-1 - l])
        im_ani = animation.FuncAnimation(
            dic["fig"],
            mapit,
            fargs=(dic, 0),
            frames=len(dic["restart"]),
            interval=dic["interval"],
            blit=False,
            repeat=False,
        )
        if dic["loop"] == 0:
            im_ani.save(
                f"{dic['output']}/{dic['deckn']}.gif", extra_args=["-loop", "-1"]
            )
        else:
            im_ani.save(f"{dic['output']}/{dic['deckn']}.gif")
    else:
        find_min_max(dic)
        dic["deck"] = dic["names"][0][0]
        dic["ndeck"] = 0
        prepare_maps(dic, 0)
        for n, var in enumerate(dic["vrs"]):
            if len(dic["restart"]) > 1:
                if dic["subfigs"][0]:
                    dic["fig"], dic["axis"] = plt.subplots(
                        int(dic["subfigs"][0]),
                        int(dic["subfigs"][1]),
                    )
                else:
                    dic["fig"], dic["axis"] = plt.subplots(1, 1)
            if not dic["subfigs"][0]:
                dic["fig"], dic["axis"] = plt.subplots(1, 1, layout="tight")
            dic["axis"] = np.array([dic["axis"]])
            for _ in range(len(dic["axis"].flat)):
                dic["original_loc"].append(dic["axis"].flat[0].get_axes_locator())
                dic["cb"].append("")
            if len(dic["restart"]) > 1:
                for l in range(len(dic["axis"].flat) - len(dic["restart"])):
                    dic["fig"].delaxes(dic["axis"].flat[-1 - l])
            if dic["mode"] == "gif" and len(dic["restart"]) > 1:
                for l in range(len(dic["axis"].flat) - len(dic["restart"])):
                    dic["fig"].delaxes(dic["axis"].flat[-1 - l])
                im_ani = animation.FuncAnimation(
                    dic["fig"],
                    mapit,
                    fargs=(dic, n),
                    frames=len(dic["restart"]),
                    interval=dic["interval"],
                    blit=False,
                    repeat=False,
                )
                if dic["loop"] == 0:
                    im_ani.save(
                        f"{dic['output']}/{dic['deckn']}_{var}.gif",
                        extra_args=["-loop", "-1"],
                    )
                else:
                    im_ani.save(f"{dic['output']}/{dic['deckn']}_{var}.gif")
            else:
                if len(dic["names"][0]) > 1:
                    for l in range(len(dic["axis"].flat) - len(dic["names"][0])):
                        dic["fig"].delaxes(dic["axis"].flat[-1 - l])
                for t, _ in enumerate(dic["restart"]):
                    if not dic["subfigs"][0]:
                        dic["fig"], dic["axis"] = plt.subplots(1, 1)
                        dic["axis"] = np.array([dic["axis"]])
                    mapit(t, dic, n)


def find_min_max(dic):
    """
    Method to find the min and max for the colorbars

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["deckd"] = ""
    if dic["diff"]:
        if len(dic["diff"].split("/")) > 1:
            dic["deckd"] = (dic["diff"].split("/")[-1]).lower()
        else:
            dic["deckd"] = dic["diff"].lower()
        dic["deck"] = dic["diff"]
        dic["ndeck"] = 0
        var = dic["vrs"][0]
        dic["diffa"] = []
        for t, _ in enumerate(dic["restart"]):
            prepare_maps(dic, 1)
            _, quan = get_quantity(dic, var.upper(), 0, dic["restart"][t])
            dic[var + "a"] = np.ones(dic["mx"] * dic["my"]) * np.nan
            if dic["slide"][1][0][0] > -1:
                map_yzcoords(dic, var, quan, 1)
            elif dic["slide"][1][1][0] > -1:
                map_xzcoords(dic, var, quan, 1)
            else:
                map_xycoords(dic, var, quan, 1)
            dic["diffa"].append(dic[var + "a"])
    if len(dic["vrs"]) == len(dic["names"][0]) and len(dic["names"][0]) > 1:
        for m, var in enumerate(dic["vrs"]):
            dic["minc"].append(dic["minc"][-1])
            dic["maxc"].append(dic["maxc"][-1])
            for t, _ in enumerate(dic["restart"]):
                dic["deck"] = dic["names"][0][m]
                dic["ndeck"] = m
                prepare_maps(dic, m)
                _, quan = get_quantity(dic, var.upper(), m, dic["restart"][t])
                dic[var + "a"] = np.ones(dic["mx"] * dic["my"]) * np.nan
                if dic["slide"][m][0][0] > -1:
                    map_yzcoords(dic, var, quan, m)
                elif dic["slide"][m][1][0] > -1:
                    map_xzcoords(dic, var, quan, m)
                else:
                    map_xycoords(dic, var, quan, m)
                if dic["diff"]:
                    dic[var + "a"] -= dic["diffa"][t]
                if int(dic["log"][m]) == 1:
                    dic[var + "a"][dic[var + "a"] <= 0] = np.nan
                dic["minc"][-2] = min(
                    dic["minc"][-2], dic[var + "a"][~np.isnan(dic[var + "a"])].min()
                )
                dic["maxc"][-2] = max(
                    dic["maxc"][-2], dic[var + "a"][~np.isnan(dic[var + "a"])].max()
                )
    else:
        for m, var in enumerate(dic["vrs"]):
            dic["minc"].append(dic["minc"][-1])
            dic["maxc"].append(dic["maxc"][-1])
            for n, deck in enumerate(dic["names"][0]):
                for t, _ in enumerate(dic["restart"]):
                    dic["deck"] = deck
                    dic["ndeck"] = n
                    prepare_maps(dic, n)
                    _, quan = get_quantity(dic, var.upper(), m, dic["restart"][t])
                    dic[var + "a"] = np.ones(dic["mx"] * dic["my"]) * np.nan
                    if dic["slide"][n][0][0] > -1:
                        map_yzcoords(dic, var, quan, n)
                    elif dic["slide"][n][1][0] > -1:
                        map_xzcoords(dic, var, quan, n)
                    else:
                        map_xycoords(dic, var, quan, n)
                    if dic["diff"]:
                        dic[var + "a"] -= dic["diffa"][t]
                    if int(dic["log"][m]) == 1:
                        dic[var + "a"][dic[var + "a"] <= 0] = np.nan
                    dic["minc"][-2] = min(
                        dic["minc"][-2], dic[var + "a"][~np.isnan(dic[var + "a"])].min()
                    )
                    dic["maxc"][-2] = max(
                        dic["maxc"][-2], dic[var + "a"][~np.isnan(dic[var + "a"])].max()
                    )
    if dic["mask"]:
        var = dic["mask"]
        dic["maska"] = []
        for n, deck in enumerate(dic["names"][0]):
            dic["deck"] = deck
            dic["ndeck"] = n
            prepare_maps(dic, n)
            _, quan = get_quantity(dic, var.upper(), 0, 0)
            dic[var + "a"] = np.ones(dic["mx"] * dic["my"]) * np.nan
            if dic["slide"][n][0][0] > -1:
                map_yzcoords(dic, var, quan, n)
            elif dic["slide"][n][1][0] > -1:
                map_xzcoords(dic, var, quan, n)
            else:
                map_xycoords(dic, var, quan, n)
            dic["maska"].append(dic[var + "a"])


def mapit(t, dic, n):
    """
    Method to coordinate the gebneration of axis

    Args:
        t (int): Number of subplot\n
        dic (dict): Global dictionary\n
        n (int): Number of variable

    Returns:
        dic (dict): Modified global dictionary

    """
    k = t
    if not dic["subfigs"][0]:
        k = 0
    elif len(dic["restart"]) == 1:
        k = n
    if dic["subfigs"][0] and len(dic["names"][0]) > 1:
        if len(dic["vrs"]) > 1:
            dic["maxc"] = [max(dic["maxc"])] * len(dic["maxc"])
            dic["minc"] = [min(dic["minc"])] * len(dic["minc"])
            for nn, deck in enumerate(dic["names"][0]):
                dic["deck"] = deck
                dic["ndeck"] = nn
                prepare_maps(dic, nn)
                mapits(dic, t, nn, nn)
        else:
            for nn, deck in enumerate(dic["names"][0]):
                dic["deck"] = deck
                dic["ndeck"] = nn
                prepare_maps(dic, nn)
                mapits(dic, t, 0, nn)
    elif dic["subfigs"][0] and len(dic["vrs"]) > 1 and dic["skip"] == 0:
        for nn, _ in enumerate(dic["vrs"]):
            mapits(dic, t, nn, nn)
    else:
        mapits(dic, t, n, k)


def mapits(dic, t, n, k):
    """
    Generate the spatial maps

    Args:
        dic (dict): Global dictionary\n
        t (int): Number of restart\n
        n (int): Number of variable\n
        k (int): Number of subplot

    Returns:
        dic (dict): Modified global dictionary

    """
    var = dic["vrs"][n]
    unit, quan = get_quantity(dic, var.upper(), n, dic["restart"][t])
    dic[var + "a"] = np.ones(dic["mx"] * dic["my"]) * np.nan
    n_s = 0
    if dic["subfigs"][0] and len(dic["names"][0]) > 1:
        n_s = k
    if dic["slide"][n_s][0][0] > -1:
        map_yzcoords(dic, var, quan, k)
    elif dic["slide"][n_s][1][0] > -1:
        map_xzcoords(dic, var, quan, k)
    else:
        map_xycoords(dic, var, quan, k)
    maps = np.ones([dic["my"], dic["mx"]]) * np.nan
    if dic["diff"]:
        for i in np.arange(0, dic["my"]):
            maps[i, :] = (
                dic[var + "a"][i * (dic["mx"]) : (i + 1) * (dic["mx"])]
                - dic["diffa"][t][i * (dic["mx"]) : (i + 1) * (dic["mx"])]
            )
        dic["abssum"] = sum(abs(maps[~np.isnan(maps)]))
    else:
        for i in np.arange(0, dic["my"]):
            maps[i, :] = dic[var + "a"][i * (dic["mx"]) : (i + 1) * (dic["mx"])]
    if dic["mask"]:
        maxv = max(dic["maska"][k][~np.isnan(dic["maska"][k])])
        for i in np.arange(0, dic["my"]):
            maps[i, :] = [
                (
                    (-dic["maxc"][n] * (maxv - val) / (maxv - 1))
                    if act < dic["maskthr"]
                    else act
                )
                for val, act in zip(
                    dic["maska"][k][i * (dic["mx"]) : (i + 1) * (dic["mx"])],
                    dic[var + "a"][i * (dic["mx"]) : (i + 1) * (dic["mx"])],
                )
            ]
    ntick = 3
    ncolor = var + " " + unit
    if var.lower() != "wells" and var.lower() != "grid" and var.lower() != "faults":
        if len(dic["names"][0]) > 1 and dic["subfigs"][0]:
            minc = dic["minc"][n]
            maxc = dic["maxc"][n]
        elif len(dic["vrs"]) > 1 and dic["subfigs"][0]:
            minc = dic["minc"][n]
            maxc = dic["maxc"][n]
        elif (
            len(dic["restart"]) > 1 and dic["subfigs"][0] and len(dic["names"][0]) == 1
        ):
            minc = dic["minc"][n]
            maxc = dic["maxc"][n]
        elif dic["mode"] == "gif" and not dic["subfigs"][0] or int(dic["log"][n]) == 1:
            minc = dic["minc"][n]
            maxc = dic["maxc"][n]
        elif dic["global"] == 0:
            minc = maps[~np.isnan(maps)].min()
            maxc = maps[~np.isnan(maps)].max()
        else:
            minc = quan[~np.isnan(quan)].min()
            maxc = quan[~np.isnan(quan)].max()
        if dic["bounds"][n][0]:
            minc = float(dic["bounds"][n][0][1:])
            maxc = float(dic["bounds"][n][1][:-1])
        elif dic["diff"] and int(dic["log"][n]) == 0:
            minmax = max(abs(maxc), abs(minc))
            minc = -minmax
            maxc = minmax
        if maxc == minc:
            ntick = 1
        elif (
            "num" in var.lower()
            and dic["cmaps"][n] in dic["cmdisc"]
            and dic["discrete"]
        ):
            ntick = int(maxc - minc + 1)
        if dic["mask"]:
            minc = -maxc
    elif var.lower() == "faults":
        minc = 1
        maxc = dic["nfaults"]
    else:
        minc = 1
        maxc = dic["nwells"]
    nlc = ntick
    if dic["cnum"][n] and ntick > 1:
        ntick = int(dic["cnum"][n])
        nlc = 2
    if var.lower() in ["faults"]:
        nlc = dic["nfaults"]
    if dic["clabel"]:
        ncolor = dic["clabel"]
    cmap = matplotlib.colormaps.get_cmap(dic["cmaps"][n])
    if dic["ncolor"] != "w":
        cmap.set_bad(color=dic["ncolor"])
    shc = 0
    # minc = 0.
    if (
        ("num" in var.lower() and dic["cmaps"][n] in dic["cmdisc"] and dic["discrete"])
        or var.lower() in ["faults"]
        and dic["cmaps"][n] != "nipy_spectral"
    ):
        if maxc == minc:
            shc = 2
        from_list = matplotlib.colors.LinearSegmentedColormap.from_list
        cmap = from_list(
            None,
            matplotlib.colormaps[dic["cmaps"][n]](range(int(minc), nlc + shc)),
            nlc,
        )
        shc = 0.5
    if var.lower() == "grid" and var.lower() != "wells":
        imag = (
            dic["axis"]
            .flat[k]
            .pcolormesh(
                dic["xc"],
                dic["yc"],
                maps,
                facecolors="none",
                edgecolors="black",
                lw=0.001,
            )
        )
    elif int(dic["log"][n]) == 0:
        imag = (
            dic["axis"]
            .flat[k]
            .pcolormesh(
                dic["xc"],
                dic["yc"],
                maps,
                shading="flat",
                cmap=cmap,
            )
        )
    else:
        imag = (
            dic["axis"]
            .flat[k]
            .pcolormesh(
                dic["xc"],
                dic["yc"],
                maps,
                shading="flat",
                cmap=cmap,
                norm=colors.LogNorm(vmin=minc, vmax=maxc),
            )
        )
    if (
        dic["subfigs"][0]
        and dic["mode"] == "gif"
        and len(dic["vrs"]) > 1
        and dic["cb"][k] != ""
    ):
        dic["cb"][k].remove()
        dic["axis"].flat[k].set_axes_locator(dic["original_loc"][k])
    if (
        dic["subfigs"][0]
        and dic["mode"] == "gif"
        and len(dic["names"][0]) > 1
        and dic["cb"][k] != ""
    ):
        dic["cb"][k].remove()
        dic["axis"].flat[k].set_axes_locator(dic["original_loc"][k])
    if not dic["subfigs"][0] and dic["cb"][k] != "" and dic["mode"] == "gif":
        dic["cb"][k].remove()
        dic["axis"].flat[k].set_axes_locator(dic["original_loc"][k])
    divider = make_axes_locatable(dic["axis"].flat[k])
    if dic["mask"]:
        vect = np.linspace(
            0,
            maxc,
            ntick,
            endpoint=True,
        )
    else:
        vect = np.linspace(
            minc,
            maxc,
            ntick,
            endpoint=True,
        )
    func = "lambda x, _: f'{x:" + dic["cformat"][n] + "}'"
    if (
        var.lower() != "wells"
        and var.lower() != "faults"
        and var.lower() != "grid"
        and dic["rm"][2] == 0
    ):
        if int(dic["log"][n]) == 0:
            if (
                len(dic["restart"]) > 1
                and dic["subfigs"][0]
                and len(dic["names"][0]) == 1
            ):
                dic["cb"][0] = dic["fig"].colorbar(
                    imag,
                    cax=dic["fig"].add_axes(dic["cbsfax"]),
                    ticks=vect,
                    label=ncolor,
                    format=eval(func),
                    shrink=0.2,
                    location="top",
                )
            elif not dic["subfigs"][0] or len(dic["names"][0]) == 1:
                dic["cb"][k] = dic["fig"].colorbar(
                    imag,
                    cax=divider.append_axes("right", size="2%", pad=0.05),
                    orientation="vertical",
                    ticks=vect,
                    label=ncolor,
                    format=eval(func),
                )
            elif k == 0:
                dic["cb"][0] = dic["fig"].colorbar(
                    imag,
                    cax=dic["fig"].add_axes(dic["cbsfax"]),
                    ticks=vect,
                    label=ncolor,
                    format=eval(func),
                    shrink=0.2,
                    location="top",
                )
        else:
            if dic["clogthks"]:

                class MF(LogFormatter):
                    def set_locs(self, locs=None):
                        self._sublabels = set(dic["clogthks"])

            if dic["subfigs"][0]:
                if dic["clogthks"]:
                    dic["cb"][k] = dic["fig"].colorbar(
                        imag,
                        cax=dic["fig"].add_axes(dic["cbsfax"]),
                        label=ncolor,
                        shrink=0.2,
                        location="top",
                        ticks=dic["clogthks"],
                        format=MF(),
                    )
                else:
                    dic["cb"][k] = dic["fig"].colorbar(
                        imag,
                        cax=dic["fig"].add_axes(dic["cbsfax"]),
                        label=ncolor,
                        shrink=0.2,
                        location="top",
                    )
            else:
                if dic["clogthks"]:
                    dic["cb"][k] = dic["fig"].colorbar(
                        imag,
                        cax=divider.append_axes("right", size="5%", pad=0.05),
                        orientation="vertical",
                        label=ncolor,
                        ticks=dic["clogthks"],
                        format=MF(),
                    )
                else:
                    dic["cb"][k] = dic["fig"].colorbar(
                        imag,
                        cax=divider.append_axes("right", size="5%", pad=0.05),
                        orientation="vertical",
                        label=ncolor,
                    )
    else:
        handle_well_or_grid_or_fault(dic, imag, divider, vect, n, var.lower())
    if dic["rm"][2] == 0:
        imag.set_clim(
            minc - shc,
            maxc + shc,
        )
    handle_axis(dic, var, n, t, k, n_s, unit)
    if dic["xlabel"][n] and dic["rm"][1] == 0:
        dic["axis"].flat[k].set_xlabel(dic["xlabel"][n])
    elif (
        dic["rm"][1] == 0
        and len(dic["vrs"]) == 1
        and (k + dic["sub1"] >= len(dic["names"][0]) or not dic["subfigs"][0])
    ):
        if len(dic["restart"]) > 1 and dic["subfigs"][0] and len(dic["names"][0]) == 1:
            if k + dic["sub1"] >= len(dic["restart"]):
                dic["axis"].flat[k].set_xlabel(f"{dic['xmeaning']+dic['xunit']}")
        else:
            dic["axis"].flat[k].set_xlabel(f"{dic['xmeaning']+dic['xunit']}")
    elif (
        dic["rm"][1] == 0
        and len(dic["names"][0]) == 1
        and (k + dic["sub1"] >= len(dic["vrs"]) or not dic["subfigs"][0])
    ):
        dic["axis"].flat[k].set_xlabel(f"{dic['xmeaning']+dic['xunit']}")
    elif (
        dic["rm"][1] == 0
        and len(dic["names"][0]) == len(dic["vrs"])
        and len(dic["vrs"]) > 1
        and (k + dic["sub1"] >= len(dic["vrs"]) or not dic["subfigs"][0])
    ):
        dic["axis"].flat[k].set_xlabel(f"{dic['xmeaning']+dic['xunit']}")
    if dic["ylabel"][n] and dic["rm"][0] == 0:
        dic["axis"].flat[k].set_ylabel(dic["ylabel"][n])
    elif dic["rm"][0] == 0 and (k % dic["sub1"] == 0 or not dic["subfigs"][0]):
        dic["axis"].flat[k].set_ylabel(f"{dic['ymeaning']+dic['yunit']}")
    if dic["rm"][2] == 1:
        dic["fig"].delaxes(dic["fig"].axes[1])
    if dic["rm"][1] == 1 or (
        k + dic["sub1"] < len(dic["names"][0])
        and dic["subfigs"][0]
        and len(dic["vrs"]) == 1
        and dic["delax"] == 1
    ):
        dic["axis"].flat[k].tick_params(
            axis="x", which="both", bottom=False, labelbottom=False
        )
    elif dic["rm"][1] == 1 or (
        k + dic["sub1"] < len(dic["vrs"])
        and dic["subfigs"][0]
        and len(dic["names"][0]) == 1
        and dic["delax"] == 1
    ):
        dic["axis"].flat[k].tick_params(
            axis="x", which="both", bottom=False, labelbottom=False
        )
    elif (
        k + dic["sub1"] < len(dic["restart"])
        and len(dic["restart"]) > 1
        and dic["subfigs"][0]
        and len(dic["names"][0]) == 1
        and dic["delax"] == 1
    ):
        dic["axis"].flat[k].tick_params(
            axis="x", which="both", bottom=False, labelbottom=False
        )
    if dic["rm"][0] == 1 or (
        k % dic["sub1"] > 0 and dic["subfigs"][0] and dic["delax"] == 1
    ):
        dic["axis"].flat[k].tick_params(
            axis="y", which="both", left=False, labelleft=False
        )
    # if dic["mode"] != "gif":
    #    plt.tight_layout(pad=0)
    if dic["mode"] != "gif":
        if dic["subfigs"][0]:
            if t == len(dic["restart"]) - 1 and len(dic["restart"]) > 1:
                dic["fig"].set_facecolor(dic["fc"])
                name = f"{dic['deckn']}_{var}_{dic['nslide']}_t{dic['restart'][t]}"
                name = name.replace(" / ", "_over_")
                dic["fig"].savefig(
                    f"{dic['output']}/{dic['save'][n] if dic['save'][n] else name}.png",
                    bbox_inches="tight",
                    dpi=int(dic["dpi"][0]),
                )
            elif n == len(dic["vrs"]) - 1 and len(dic["vrs"]) > 1:
                dic["fig"].set_facecolor(dic["fc"])
                name = f"{dic['deckn']}_{var}_{dic['nslide']}_t{dic['restart'][t]}"
                name = name.replace(" / ", "_over_")
                dic["fig"].savefig(
                    f"{dic['output']}/{dic['save'][n] if dic['save'][n] else name}.png",
                    bbox_inches="tight",
                    dpi=int(dic["dpi"][0]),
                )
            else:
                if len(dic["restart"]) == 1:
                    if k == max(len(dic["vrs"]) - 1, len(dic["names"][0]) - 1):
                        dic["fig"].set_facecolor(dic["fc"])
                        name = (
                            f"{dic['deckn']}_{var}_{dic['nslide']}_t{dic['restart'][t]}"
                        )
                        name = name.replace(" / ", "_over_")
                        dic["fig"].savefig(
                            f"{dic['output']}/{dic['save'][n] if dic['save'][n] else name}.png",
                            bbox_inches="tight",
                            dpi=int(dic["dpi"][0]),
                        )
                elif len(dic["names"][0]) == 1:
                    if t == len(dic["restart"]) - 1:
                        dic["fig"].set_facecolor(dic["fc"])
                        name = (
                            f"{dic['deckn']}_{var}_{dic['nslide']}_t{dic['restart'][t]}"
                        )
                        name = name.replace(" / ", "_over_")
                        dic["fig"].savefig(
                            f"{dic['output']}/{dic['save'][n] if dic['save'][n] else name}.png",
                            bbox_inches="tight",
                            dpi=int(dic["dpi"][0]),
                        )
                else:
                    dic["fig"].set_facecolor(dic["fc"])
                    name = f"{dic['deckn']}_{var}_{dic['nslide']}_t{dic['restart'][t]}"
                    name = name.replace(" / ", "_over_")
                    dic["fig"].savefig(
                        f"{dic['output']}/{dic['save'][n] if dic['save'][n] else name}.png",
                        bbox_inches="tight",
                        dpi=int(dic["dpi"][0]),
                    )
        else:
            dic["fig"].set_facecolor(dic["fc"])
            name = f"{dic['deckn']}_{var}_{dic['nslide']}_t{dic['restart'][t]}"
            name = name.replace(" / ", "_over_")
            dic["fig"].savefig(
                f"{dic['output']}/{dic['save'][n] if dic['save'][n] else name}.png",
                bbox_inches="tight",
                dpi=int(dic["dpi"][0]),
            )


def handle_axis(dic, name, n, t, k, n_s, unit):
    """
    Method to handle the figure axis

    Args:
        dic (dict): Global dictionary\n
        name (str): Property to plot

    Returns:
        dic (dict): Modified global dictionary

    """
    namet = name
    if dic["tunits"][0] == "dates":
        if dic["use"] == "opm":
            print(
                "For 2D spatial mapsIt is not possible to use -tunits dates"
                " and -u opm. Try with -u resdata or different -tunits."
            )
            sys.exit()
        time = f", {dic['unrst'].dates[dic['restart'][t]].date()}"
    else:
        tskl, tunit = initialize_time(dic["tunits"][0])
        tunit = tunit[5:]
        time = f", {tskl*dic['tnrst'][dic['restart'][t]]:.0f} {tunit}"
    if dic["scale"] == 1:
        dic["axis"].flat[k].axis("scaled")
    extra = ""
    if name == "porv":
        extra = f", sum={sum(dic[name]):.3e}"
    elif name in dic["mass"] and dic["diff"]:
        extra = f", |sum|={dic['abssum']:.3e} {unit}"
    elif name in dic["mass"]:
        extra = f", sum={sum(dic[name + 'a'][~np.isnan(dic[name + 'a'])]):.3e} {unit}"
    elif dic["diff"]:
        extra = f", |sum|={dic['abssum']:.3e}"
    elif dic["faults"] or dic["wells"]:
        time = ""
        namet = f"Total no. {name} = {dic[f'n{name}']-1}, "
    elif "num" in name and dic["cmaps"][n] in dic["cmdisc"] and dic["discrete"]:
        time = ""
        namet = ""
    if (
        dic["faults"]
        or dic["wells"]
        or ("num" in name and dic["cmaps"][n] in dic["cmdisc"] and dic["discrete"])
    ):
        tslide = dic["tslide"][2:]
    else:
        tslide = dic["tslide"]
    if dic["subfigs"][0] and len(dic["names"][0]) > 1 and dic["titles"][k] == "0":
        dic["axis"].flat[k].set_title(dic["deckn"])
        if k == 0 and dic["suptitle"] != "0":
            dic["fig"].suptitle(f"{time[1:]}")
    elif dic["subfigs"][0] and len(dic["vrs"]) > 1 and dic["titles"][k] == "0":
        if k == 0 and dic["suptitle"] != "0":
            dic["fig"].suptitle(f"{dic['deckn']}{time}")
    elif dic["mode"] == "gif" and len(dic["vrs"]) == 1 and dic["titles"][k] == "0":
        if dic["diff"]:
            dic["axis"].flat[k].set_title(f"{dic['deckn']}-{dic['deckd']}{time}")
        else:
            dic["axis"].flat[k].set_title(f"{dic['deckn']}{time}")
    elif (
        len(dic["restart"]) > 1
        and dic["subfigs"][0]
        and len(dic["names"][0]) == 1
        and dic["titles"][k] == "0"
    ):
        dic["axis"].flat[k].set_title(f"{dic['tnrst'][dic['restart'][t]]} days")
        if k == 0 and dic["suptitle"] != "0":
            if dic["diff"]:
                dic["fig"].suptitle(f"{dic['deckn']}-{dic['deckd']}")
            else:
                dic["fig"].suptitle(f"{dic['deckn']}")
    elif dic["rm"][3] == 0 and dic["titles"][k] == "0":
        if dic["diff"]:
            dic["axis"].flat[k].set_title(
                f"{dic['deckn']}-{dic['deckd']}" + tslide + dic["dtitle"] + extra + time
            )
        else:
            dic["axis"].flat[k].set_title(namet + tslide + dic["dtitle"] + extra + time)
    elif dic["subfigs"][0] and len(dic["names"][0]) > 1:
        if k == 0 and dic["suptitle"] != "0":
            dic["fig"].suptitle(f"{dic['tnrst'][dic['restart'][t]]} days")
    if name == "grid" and dic["rm"][3] == 0 and dic["titles"][k] == "0":
        dic["axis"].flat[k].set_title(
            f"Grid = [{dic['nx']},{dic['ny']},{dic['nz']}], "
            + f"Total no. active cells = {max(dic['actind'])+1}"
        )
    if dic["titles"][k] != "0" and dic["rm"][3] == 0:
        dic["axis"].flat[k].set_title(dic["titles"][k])
    if dic["slide"][n_s][2][0] == -2 and not dic["axis"].flat[k].yaxis_inverted():
        dic["axis"].flat[k].invert_yaxis()
    if len(dic["xlim"][n]) > 1 and dic["rm"][1] == 0:
        dic["axis"].flat[k].set_xlim(
            [float(dic["xlim"][n][0][1:]), float(dic["xlim"][n][1][:-1])]
        )
        xlabels = np.linspace(
            float(dic["xlim"][n][0][1:]) * dic["xskl"],
            float(dic["xlim"][n][1][:-1]) * dic["xskl"],
            int(dic["xlnum"][n]),
        )
    else:
        xlabels = np.linspace(
            min(min(dic["xc"])) * dic["xskl"],
            max(max(dic["xc"])) * dic["xskl"],
            int(dic["xlnum"][n]),
        )
    if dic["xformat"][n] and dic["rm"][1] == 0:
        func = "f'{x:" + dic["xformat"][n] + "}'"
        dic["axis"].flat[k].set_xticks(
            [float(eval(func)) / dic["xskl"] for x in xlabels]
        )
        dic["axis"].flat[k].set_xticklabels([eval(func) for x in xlabels])
    elif dic["rm"][1] == 0:
        dic["axis"].flat[k].set_xticks(xlabels / dic["xskl"])
        if dic["xskl"] != 1:
            dic["axis"].flat[k].set_xticklabels(xlabels)
    if len(dic["ylim"][n]) > 1 and dic["rm"][0] == 0:
        dic["axis"].flat[k].set_ylim(
            [float(dic["ylim"][n][0][1:]), float(dic["ylim"][n][1][:-1])]
        )
        ylabels = np.linspace(
            float(dic["ylim"][n][0][1:]) * dic["yskl"],
            float(dic["ylim"][n][1][:-1]) * dic["yskl"],
            int(dic["ylnum"][n]),
        )
    else:
        ylabels = np.linspace(
            min(min(dic["yc"])) * dic["yskl"],
            max(max(dic["yc"])) * dic["yskl"],
            int(dic["ylnum"][n]),
        )
    if dic["yformat"][n] and dic["rm"][0] == 0:
        func = "f'{y:" + dic["yformat"][n] + "}'"
        dic["axis"].flat[k].set_yticks(
            [float(eval(func)) / dic["yskl"] for y in ylabels]
        )
        dic["axis"].flat[k].set_yticklabels([eval(func) for y in ylabels])
    elif dic["rm"][0] == 0:
        dic["axis"].flat[k].set_yticks(ylabels / dic["yskl"])
        if dic["yskl"] != 1:
            dic["axis"].flat[k].set_yticklabels(ylabels)


def handle_well_or_grid_or_fault(dic, imag, divider, vect, n, var):
    """
    Method to create the 2d maps using pcolormesh

    Args:
        dic (dict): Global dictionary\n
        imag (class): Actual plot object\n
        divider (class): Object for the color bar axis\n
        vect (array): Floats for the labels in the color bar

    Returns:
        plt (class): Modified plotting object\n

    """
    dic["fig"].colorbar(
        imag,
        cax=divider.append_axes("right", size="0%", pad=0.05),
        orientation="vertical",
        ticks=vect,
        format=lambda x, _: "",
    )
    if var in ["faults", "wells"]:
        cmap = matplotlib.colormaps[dic["cmaps"][n]]
        colour = cmap(np.linspace(0, 1, dic[f"n{var}"]))
        # shi = 1
        if dic[f"n{var}"] < 70:
            for i, wells in enumerate(dic[f"l{var}"]):
                well = dic[var][dic[f"l{var}"].index(wells)]
                if any(well):
                    plt.text(
                        0,
                        i + 1,
                        f"{wells}",
                        c=colour[i],
                        fontweight="bold",
                    )
                    # shi += 1
                    # if well[0][2] != well[0][3]:
                    #     plt.text(
                    #         0,
                    #         i,
                    #         f"{wells}-({well[0][0]+1},{well[0][1]+1},
                    # {well[0][2]+1}-{well[0][3]+1})",
                    #         c=colour[i],
                    #         fontweight="bold",
                    #     )
                    # else:
                    #     plt.text(
                    #         0,
                    #         i,
                    #         f"{wells}-({well[0][0]+1},
                    # {well[0][1]+1},{well[0][2]+1})",
                    #         c=colour[i],
                    #         fontweight="bold",
                    #     )
        else:
            for i, wells in zip(
                [0, len(dic[var]) - 1], [dic[f"l{var}"][0], dic[f"l{var}"][-1]]
            ):
                well = dic[var][dic[f"l{var}"].index(wells)]
                if well:
                    plt.text(
                        0,
                        i + 1,
                        f"{wells}",
                        c=colour[i],
                        fontweight="bold",
                    )
                    # if well[2] != well[3]:
                    #     plt.text(
                    #         0,
                    #         i,
                    #         f"{wells}-({well[0][0]+1},{well[0][1]+1},
                    # {well[0][2]+1}-{well[0][3]+1})",
                    #         c=colour[i],
                    #         fontweight="bold",
                    #     )
                    # else:
                    #     plt.text(
                    #         0,
                    #         i,
                    #         f"{wells}-({well[0][0]+1},
                    # {well[0][1]+1},{well[0][2]+1})",
                    #         c=colour[i],
                    #         fontweight="bold",
                    #     )
