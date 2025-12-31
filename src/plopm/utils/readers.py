# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0911,R0912,R0913,R0915,R0917,R1702,R0914,C0302,E1102

"""
Utiliy functions to read the OPM Flow simulator type output files.
"""

import os
import csv
import sys
import datetime
import numpy as np
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import EGrid as OpmGrid
from opm.io.ecl import ERst as OpmRestart
from opm.io.ecl import ESmry as OpmSummary
from alive_progress import alive_bar
from plopm.utils.initialization import initialize_mass, initialize_spatial

GAS_DEN_REF = 1.86843
WAT_DEN_REF = 998.108


def get_yzcoords(dic, n):
    """
    Handle the coordinates from the OPM Grid to the 2D yz-mesh using opm

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for j in range(dic["nz"]):
        dic["xc"].append([])
        dic["yc"].append([])
        for k, c, p in zip(["x", "x", "y", "y"], [1, 1, 2, 2], [4, 6, 4, 6]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(
                    dic["slide"][n][0][0], 0, dic["nz"] - j - 1, True
                )[c][p]
            )
        for i in range(dic["ny"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [1, 1, 2, 2], [4, 6, 4, 6]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(
                        dic["slide"][n][0][0], i + 1, dic["nz"] - j - 1, True
                    )[c][p]
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, c, p in zip(["x", "x", "y", "y"], [1, 1, 2, 2], [0, 2, 0, 2]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(
                    dic["slide"][n][0][0], 0, dic["nz"] - j - 1, True
                )[c][p]
            )
        for i in range(dic["ny"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [1, 1, 2, 2], [0, 2, 0, 2]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(
                        dic["slide"][n][0][0], i + 1, dic["nz"] - j - 1, True
                    )[c][p]
                )


def get_xzcoords(dic, n):
    """
    Handle the coordinates from the OPM Grid to the 2D xz-mesh using opm

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for j in range(dic["nz"]):
        dic["xc"].append([])
        dic["yc"].append([])
        for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 2, 2], [4, 5, 4, 5]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(
                    0, dic["slide"][n][1][0], dic["nz"] - j - 1, True
                )[c][p]
            )
        for i in range(dic["nx"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 2, 2], [4, 5, 4, 5]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(
                        i + 1, dic["slide"][n][1][0], dic["nz"] - j - 1, True
                    )[c][p]
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 2, 2], [0, 1, 0, 1]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(
                    0, dic["slide"][n][1][0], dic["nz"] - j - 1, True
                )[c][p]
            )
        for i in range(dic["nx"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 2, 2], [0, 1, 0, 1]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(
                        1 + i, dic["slide"][n][1][0], dic["nz"] - j - 1, True
                    )[c][p]
                )


def get_xycoords(dic, n):
    """
    Handle the coordinates from the OPM Grid to the 2D xy-mesh using opm

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for j in range(dic["ny"]):
        dic["xc"].append([])
        dic["yc"].append([])
        for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 1, 1], [0, 1, 0, 1]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(0, j, dic["slide"][n][2][0], True)[c][p]
            )
        for i in range(dic["nx"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 1, 1], [0, 1, 0, 1]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(i + 1, j, dic["slide"][n][2][0], True)[c][
                        p
                    ]
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 1, 1], [2, 3, 2, 3]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(0, j, dic["slide"][n][2][0], True)[c][p]
            )
        for i in range(dic["nx"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 1, 1], [2, 3, 2, 3]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(i + 1, j, dic["slide"][n][2][0], True)[c][
                        p
                    ]
                )


def get_histogram(dic, quans, nrst):
    """
    Get the required variables from the histogram

    Args:
        dic (dict): Global dictionary

    Returns:
        var (array): Vector with the variable values\n
        time (array): Vector with the x axis values

    """
    act = dic["porv"] > 0 if quans[0].upper() != "PORV" else dic["porv"] > -1
    var = np.nan * np.ones(dic["nxyz"], dtype=float)
    if dic["init"].count(quans[0].upper()):
        var[act] = 1.0 * dic["init"][quans[0].upper(), 0]
    elif dic["unrst"].count(quans[0].upper(), nrst):
        var[act] = 1.0 * dic["unrst"][quans[0].upper(), nrst]
    elif quans[0].lower() in dic["mass"] + dic["xmass"]:
        var[act] = handle_mass(dic, quans[0].lower(), nrst)
    elif quans[0].lower() in dic["caprock"]:
        var[act], _ = handle_caprock(dic, quans[0].lower(), nrst)
    else:
        print(f"Unknow -v variable ({quans[0]}).")
        sys.exit()
    if len(quans) > 1:
        for j, val in enumerate(quans[2::2]):
            if (val[0]).isdigit() and not val[-1].isdigit():
                quan1 = 1.0 * dic["unrst"][val[1:].upper(), int(val[0])]
            elif (val[0]).isdigit() and val[-1].isdigit():
                quan1 = float(val)
            elif dic["init"].count(val.upper()):
                quan1 = 1.0 * dic["init"][val.upper(), 0]
            elif dic["unrst"].count(val.upper(), nrst):
                quan1 = 1.0 * dic["unrst"][val.upper(), nrst]
            elif val.lower() in dic["mass"] + dic["xmass"]:
                quan1 = handle_mass(dic, val.lower(), nrst)
            elif val.lower() in dic["caprock"]:
                quan1 = handle_caprock(dic, val.lower(), nrst)
            else:
                print(f"Unknow -v variable ({val}).")
                sys.exit()
            var[act] = operate(var[act], quan1, j, quans[1::2])
    return var


def compute_distance(dic, quans, n):
    """
    Get the required variables from the simulation files

    Args:
        dic (dict): Global dictionary

    Returns:
        var (array): Vector with the variable values\n
        time (array): Vector with the x axis values

    """
    xyz = np.zeros((dic["nxyz"], 3), dtype=float)
    act = dic["porv"] > 0
    time = np.array(dic["tnrst"])
    distance = np.nan * np.ones(dic["ntot"])
    m = 0
    for k in range(dic["nz"]):
        for j in range(dic["ny"]):
            for i in range(dic["nx"]):
                xyz[m, :] = np.mean(dic["egrid"].xyz_from_ijk(i, j, k, True), axis=1)
                m += 1
    if dic["distance"][1] == "sensor":
        ind = (
            dic["slide"][n][0]
            + dic["slide"][n][1] * dic["nx"]
            + dic["slide"][n][2] * dic["nx"] * dic["ny"]
        )
        points = [xyz[ind, :]]
        print(
            f"Computing the {dic['distance'][0]} distance to the sensor "
            f"[{points[0][0]:.2E},{points[0][1]:.2E},{points[0][2]:.2E}] m"
        )
    else:
        points = []
        for k in range(dic["nz"]):
            if dic["ny"] > 1:
                for i in range(dic["nx"]):
                    ind = i + j * dic["nx"] + k * dic["nx"] * dic["ny"]
                    if act[ind]:
                        points.append(xyz[ind])
                    ind = i + (dic["ny"] - 1) * dic["nx"] + k * dic["nx"] * dic["ny"]
                    if act[ind]:
                        points.append(xyz[ind])
            if dic["nx"] > 1:
                for j in range(dic["ny"]):
                    ind = j * dic["nx"] + k * dic["nx"] * dic["ny"]
                    if act[ind]:
                        points.append(xyz[ind])
                    ind = dic["nx"] - 1 + j * dic["nx"] + k * dic["nx"] * dic["ny"]
                    if act[ind]:
                        points.append(xyz[ind])
        print(f"Computing the {dic['distance'][0]} distance to the boundaries")
    with alive_bar(dic["ntot"] * len(points)) as bar_animation:
        for nrst in dic["unrst"].report_steps:
            xyzt = np.copy(xyz)
            var = np.nan * np.ones(dic["nxyz"], dtype=float)
            if dic["unrst"].count(quans[0].upper(), nrst):
                var[act] = 1.0 * dic["unrst"][quans[0].upper(), nrst]
            elif quans[0].lower() in dic["mass"] + dic["xmass"]:
                var[act] = handle_mass(dic, quans[0].lower(), nrst)
            else:
                print(f"Unknow -v variable ({quans[0]}).")
                sys.exit()
            if len(quans) > 1:
                for j, val in enumerate(quans[2::2]):
                    if (val[0]).isdigit() and not val[-1].isdigit():
                        quan1 = 1.0 * dic["unrst"][val[1:].upper(), int(val[0])]
                    elif (val[0]).isdigit() and val[-1].isdigit():
                        quan1 = float(val)
                    elif dic["init"].count(val.upper()):
                        quan1 = 1.0 * dic["init"][val.upper(), 0]
                    elif dic["unrst"].count(val.upper(), nrst):
                        quan1 = 1.0 * dic["unrst"][val.upper(), nrst]
                    elif val.lower() in dic["mass"] + dic["xmass"]:
                        quan1 = handle_mass(dic, val.lower(), nrst)
                    else:
                        print(f"Unknow -v variable ({val}).")
                        sys.exit()
                    var[act] = operate(var[act], quan1, j, quans[1::2])
            xyzt[var != 1] = np.nan
            temp = np.nan * np.ones(len(points))
            for i, point in enumerate(points):
                bar_animation()
                if dic["distance"][0].lower() == "min":
                    temp[i] = np.nanmin(np.linalg.norm(xyzt - point, axis=1))
                else:
                    temp[i] = np.nanmax(np.linalg.norm(xyzt - point, axis=1))
            if dic["distance"][0].lower() == "min":
                distance[nrst] = np.nanmin(temp)
            else:
                distance[nrst] = np.nanmax(temp)
    return distance[~np.isnan(distance)], time[~np.isnan(distance)]


def project(var, oper, porv):
    """
    Applied the requested projection

    Args:
        var (array): Floats with the current values\n
        oper (str): Input operator\n
        porv (array): Pore volumes of the cells

    Returns:
        var (array): Modified values after applying the projection

    """
    if oper == "min":
        var = np.min(var)
    elif oper == "max":
        var = np.max(var)
    elif oper == "sum":
        var = np.sum(var)
    elif oper == "mean":
        var = np.mean(var)
    elif oper == "pvmean":
        var = np.mean(var * porv) / np.sum(porv)
    else:
        print(f"Unknow/unsupported projection ({oper}).")
        sys.exit()
    return var


def do_read_variables(dic, quans, n, ntot):
    """
    Get the required variables from the simulation files

    Args:
        dic (dict): Global dictionary

    Returns:
        var (array): Vector with the variable values\n
        time (array): Vector with the x axis values

    """
    m = dic["slide"][n].index(-1) if -1 in dic["slide"][n] else -1
    if m == 0:
        xsize = dic["nx"]
    elif m == 1:
        xsize = dic["ny"]
    elif m == 2:
        xsize = dic["nz"]
    else:
        xsize = 1
    if len(ntot) > 1:
        tsize = len(ntot)
        time = np.array(dic["tnrst"])
        var = 0.0 * np.ones(tsize)
    else:
        time = np.array(range(xsize), dtype=float)
        var = 0.0 * np.ones(xsize)
    for o, nrst in enumerate(ntot):
        temp = np.ones(xsize, dtype=float)
        porv = np.ones(xsize, dtype=float)
        for i in range(xsize):
            if dic["layer"]:
                if m == 0:
                    ind = dic["egrid"].active_index(
                        i, dic["slide"][n][1], dic["slide"][n][2]
                    )
                elif m == 1:
                    ind = dic["egrid"].active_index(
                        dic["slide"][n][0], i, dic["slide"][n][2]
                    )
                else:
                    ind = dic["egrid"].active_index(
                        dic["slide"][n][0], dic["slide"][n][1], i
                    )
            else:
                ind = dic["egrid"].active_index(
                    dic["slide"][n][0], dic["slide"][n][1], dic["slide"][n][2]
                )
            l = i + o
            if dic["unrst"].count(quans[0].upper(), nrst):
                temp[i] = 1.0 * dic["unrst"][quans[0].upper(), nrst][ind]
            elif quans[0].lower() in dic["mass"] + dic["xmass"]:
                temp[i] = handle_mass(dic, quans[0].lower(), nrst)[ind]
            elif quans[0].lower() in dic["caprock"]:
                temp[i], _ = handle_caprock(dic, quans[0].lower(), nrst)[ind]
            else:
                print(f"Unknow -v variable ({quans[0]}).")
                sys.exit()
            if dic["unrst"].count("RPORV", nrst):
                porv[i] = dic["unrst"]["RPORV", nrst][ind]
            else:
                porv[i] = dic["pv"][ind]
            if len(quans) > 1:
                for j, val in enumerate(quans[2::2]):
                    if (val[0]).isdigit() and not val[-1].isdigit():
                        quan1 = 1.0 * dic["unrst"][val[1:].upper(), int(val[0])][ind]
                    elif (val[0]).isdigit() and val[-1].isdigit():
                        quan1 = float(val)
                    elif dic["init"].count(val.upper()):
                        quan1 = 1.0 * dic["init"][val.upper(), 0][ind]
                    elif dic["unrst"].count(val.upper(), nrst):
                        quan1 = 1.0 * dic["unrst"][val.upper(), nrst][ind]
                    elif val.lower() in dic["mass"] + dic["xmass"]:
                        quan1 = handle_mass(dic, val.lower(), nrst)[ind]
                    elif val.lower() in dic["caprock"]:
                        quan1, _ = handle_caprock(dic, val.lower(), nrst)[ind]
                    else:
                        print(f"Unknow -v variable ({val}).")
                        sys.exit()
                    temp[i] = operate(temp[i], quan1, j, quans[1::2])
        if dic["how"][0]:
            var[o] = project(temp, dic["how"][0], porv)
        elif dic["layer"]:
            var = temp
        else:
            if xsize == 1:
                var[l] = temp[0]
            else:
                var[l] = temp
    if dic["layer"] and not dic["how"][0]:
        if m == 0:
            for i in range(dic["nx"]):
                time[i] = np.mean(
                    dic["egrid"].xyz_from_ijk(
                        i, dic["slide"][n][1], dic["slide"][n][2], True
                    ),
                    axis=1,
                )[0]
        elif m == 1:
            for j in range(dic["ny"]):
                time[j] = np.mean(
                    dic["egrid"].xyz_from_ijk(
                        dic["slide"][n][0], j, dic["slide"][n][2], True
                    ),
                    axis=1,
                )[1]
        else:
            for k in range(dic["nz"]):
                time[k] = np.mean(
                    dic["egrid"].xyz_from_ijk(
                        dic["slide"][n][0], dic["slide"][n][1], k, True
                    ),
                    axis=1,
                )[2]
    return var, time


def read_summary(dic, case, quan, tunit, qskl, n):
    """
    Handle the summary vectors

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    time, vunit = np.array([0, 1]), ""
    tskl, tunit = initialize_time(tunit)
    quans = quan.split(" ")
    if dic["csvs"][n][0]:
        csvv = np.genfromtxt(
            f"{case}.csv",
            delimiter=",",
            skip_header=1,
        )
        time = (
            tskl
            * np.array([csvv[i][dic["csvs"][n][0] - 1] for i in range(csvv.shape[0])])
            / 86400.0
        )
        var = np.array([csvv[i][dic["csvs"][n][1] - 1] for i in range(csvv.shape[0])])
    elif dic["distance"][0]:
        xskl, xunit = initialize_spatial(dic["xunits"])
        dic["deck"] = case
        get_readers(dic)
        var, time = compute_distance(dic, quans, n)
        vunit = f" ({dic['distance'][0]} distance to {dic['distance'][1]} in {xunit})"
        var *= xskl
    elif dic["histogram"][0]:
        dic["deck"] = case
        get_readers(dic)
        var = get_histogram(dic, quans, dic["restart"][0])
        tunit = ""
    elif dic["sensor"] or dic["how"][0]:
        dic["deck"] = case
        get_readers(dic)
        var, time = do_read_variables(dic, quans, n, dic["unrst"].report_steps)
        time *= tskl
        if tunit == "Dates":
            time = []
            for i in range(len(dic["unrst"])):
                x = dic["unrst"]["INTEHEAD", i]
                time.append(datetime.datetime(x[66], x[65], x[64], 0, 0))
    elif dic["layer"]:
        xskl, tunit = initialize_spatial(dic["xunits"])
        dic["deck"] = case
        get_readers(dic)
        tmp = dic["restart"][n] if n < len(dic["restart"]) else dic["restart"][0]
        var, time = do_read_variables(dic, quans, n, [tmp])
        time *= xskl
    elif quans[0].lower()[:3] in ["krw", "krg"] or quans[0].lower()[:4] in [
        "krog",
        "krow",
        "pcow",
        "pcog",
        "pcwg",
    ]:
        snu = 1
        hyst = False
        if quans[0].lower()[-1] == "h":
            hyst = True
            quans[0] = quans[0][:-1]
        if len(quans[0].lower()) == 3:
            what = quans[0].lower()[:3]
        elif quans[0].lower() in ["krow", "krog", "pcow", "pcog", "pcwg"]:
            what = quans[0].lower()[:4]
        elif quans[0].lower()[:3] in ["krw", "krg"]:
            what = quans[0].lower()[:3]
            snu = int(quans[0][3:])
        else:
            what = quans[0].lower()[:4]
            snu = int(quans[0][4:])
        if not os.path.isfile(f"{case}.INIT"):
            print(f"Saturation functions required {case}.INIT")
            sys.exit()
        dic["init"] = OpmFile(f"{case}.INIT")
        tabdim = [dic["init"]["TABDIMS"]]
        table = [np.array(dic["init"]["TAB"])]
        nswe = tabdim[0][24]
        nsnum = tabdim[0][25]
        vunit = ""
        tskl = 1
        if what == "krg":
            tunit = "s$_g$ [-]"
            sht = tabdim[0][23] - 1
            time = np.array(table[0][sht + (snu - 1) * nswe : sht + snu * nswe])
            time = np.array([val for val in time if val <= 1.0])
            n_v = len(time)
            var = table[0][
                sht + nswe * nsnum + (snu - 1) * nswe : sht + nswe * nsnum + snu * nswe
            ][:n_v]
            if hyst:
                timeh = np.array(
                    table[0][
                        sht
                        + (int(nsnum / 2) + snu - 1) * nswe : sht
                        + (int(nsnum / 2) + snu) * nswe
                    ]
                )
                timeh = np.array([val for val in timeh if val <= 1.0])
                n_v = len(timeh)
                var = np.append(
                    var,
                    np.flip(
                        table[0][
                            sht
                            + nswe * nsnum
                            + (int(nsnum / 2) + snu - 1) * nswe : sht
                            + nswe * nsnum
                            + (int(nsnum / 2) + snu) * nswe
                        ][:n_v]
                    ),
                )
                time = np.append(time, np.flip(timeh))
        elif what == "krow":
            nswe = tabdim[0][21]
            tunit = "s$_w$ [-]"
            sht = tabdim[0][26] - 1
            time = np.array(table[0][sht + (snu - 1) * nswe : sht + snu * nswe])
            time = np.array([val for val in time if val <= 1.0])
            n_v = len(time)
            if tabdim[0][22] == 2:
                sht += nswe
            var = np.flip(
                table[0][
                    sht
                    + nswe * nsnum
                    + (snu - 1) * nswe : sht
                    + nswe * nsnum
                    + snu * nswe
                ][:n_v]
            )
            if hyst:
                timeh = np.array(
                    table[0][
                        sht
                        + (int(nsnum / 2) + snu - 1) * nswe : sht
                        + (int(nsnum / 2) + snu) * nswe
                    ]
                )
                timeh = np.array([val for val in timeh if val <= 1.0])
                n_v = len(timeh)
                sht += nswe
                var = np.append(
                    var,
                    table[0][
                        sht
                        + nswe * nsnum
                        + (int(nsnum / 2) + snu - 1) * nswe : sht
                        + nswe * nsnum
                        + (int(nsnum / 2) + snu) * nswe
                    ][:n_v],
                )
                time = np.append(time, np.flip(timeh))
        elif what == "krw":
            nswe = tabdim[0][21]
            tunit = "s$_w$ [-]"
            sht = tabdim[0][20] - 1
            time = np.array(table[0][sht + (snu - 1) * nswe : sht + snu * nswe])
            time = np.array([val for val in time if val <= 1.0])
            n_v = len(time)
            if tabdim[0][22] == 2:
                sht += nswe
            var = table[0][
                sht + nswe * nsnum + (snu - 1) * nswe : sht + nswe * nsnum + snu * nswe
            ][:n_v]
            if hyst:
                timeh = np.array(
                    table[0][
                        sht
                        + (int(nsnum / 2) + snu - 1) * nswe : sht
                        + (int(nsnum / 2) + snu) * nswe
                    ]
                )
                timeh = np.array([val for val in timeh if val <= 1.0])
                n_v = len(timeh)
                var = np.append(
                    var,
                    np.flip(
                        table[0][
                            sht
                            + nswe * nsnum
                            + (int(nsnum / 2) + snu - 1) * nswe : sht
                            + nswe * nsnum
                            + (int(nsnum / 2) + snu) * nswe
                        ][:n_v]
                    ),
                )
                time = np.append(time, np.flip(timeh))
        elif what == "pcow":
            nswe = tabdim[0][21]
            tunit = "s$_w$ [-]"
            sht = tabdim[0][20] - 1
            time = np.array(table[0][sht + (snu - 1) * nswe : sht + snu * nswe])
            time = np.array([val for val in time if val <= 1.0])
            n_v = len(time)
            var = table[0][
                sht
                + 2 * nswe * nsnum
                + (snu - 1) * nswe : sht
                + 2 * nswe * nsnum
                + snu * nswe
            ][:n_v]
            if hyst:
                timeh = np.array(
                    table[0][
                        sht
                        + (int(nsnum / 2) + snu - 1) * nswe : sht
                        + (int(nsnum / 2) + snu) * nswe
                    ]
                )
                timeh = np.array([val for val in timeh if val <= 1.0])
                n_v = len(timeh)
                sht += nswe
                var = np.append(
                    var,
                    np.flip(
                        table[0][
                            sht
                            + 2 * nswe * nsnum
                            + (int(nsnum / 2) + snu - 1) * nswe : sht
                            + 2 * nswe * nsnum
                            + (int(nsnum / 2) + snu) * nswe
                        ][:n_v]
                    ),
                )
                time = np.append(time, np.flip(timeh))
        else:
            tunit = "s$_g$ [-]"
            sht = tabdim[0][23] - 1
            time = np.array(table[0][sht + (snu - 1) * nswe : sht + snu * nswe])
            time = np.array([val for val in time if val <= 1.0])
            n_v = len(time)
            var = table[0][
                sht
                + 2 * nswe * nsnum
                + (snu - 1) * nswe : sht
                + 2 * nswe * nsnum
                + snu * nswe
            ][:n_v]
            if hyst:
                timeh = np.array(
                    table[0][
                        sht
                        + (int(nsnum / 2) + snu - 1) * nswe : sht
                        + (int(nsnum / 2) + snu) * nswe
                    ]
                )
                timeh = np.array([val for val in timeh if val <= 1.0])
                n_v = len(timeh)
                var = np.append(
                    var,
                    np.flip(
                        table[0][
                            sht
                            + 2 * nswe * nsnum
                            + (int(nsnum / 2) + snu - 1) * nswe : sht
                            + 2 * nswe * nsnum
                            + (int(nsnum / 2) + snu) * nswe
                        ][:n_v]
                    ),
                )
                time = np.append(time, np.flip(timeh))
    elif quan.lower()[:6] == "pcfact":
        time = []
        var = []
        found = False
        snu = 1
        vec = quans[0].upper()
        snu = int(quans[0][6:])
        vec = quans[0].upper()[:6]
        file = where_at(case, vec)
        count = 0
        with open(file, "r", encoding="utf8") as file:
            for row in csv.reader(file, delimiter=" "):
                if len(row) > 0:
                    if row[0] == vec:
                        found = True
                    if count == snu:
                        break
                    if (
                        len(row) > 1
                        and row[0].strip() != "--"
                        and found
                        and count == snu - 1
                    ):
                        time.append(float(row[0]))
                        var.append(float(row[1]))
                        if len(row) > 2:
                            if row[2].strip() == "/":
                                break
                    if found:
                        if row[0] == "/":
                            count += 1
                        elif len(row) > 2:
                            if row[2].strip() == "/":
                                count += 1
        if not var:
            print(f"No {quans[0]} found.")
            sys.exit()
        var = np.array(var)
        time = np.array(time)
    else:
        summary = OpmSummary(f"{case}.SMSPEC")
        if quans[0].upper() in dic["smass"]:
            var = summary[quans[0][:-1].upper()]
        else:
            var = summary[quans[0].upper()]
        if len(quans) > 1:
            for i, val in enumerate(quans[2::2]):
                if val.upper() in summary.keys():
                    quan1 = summary[val.upper()]
                else:
                    quan1 = float(val)
                var = operate(var, quan1, i, quans[1::2])
        if tunit == "Dates":
            smsp_dates = 86400 * summary["TIME"]
            smsp_dates = [
                summary.start_date + datetime.timedelta(seconds=seconds)
                for seconds in smsp_dates
            ]
            time = smsp_dates
        else:
            time = summary["TIME"] * tskl
    if quans[0].lower() in ["fgip", "fgit"]:
        vunit = " [sm$^3$]"
    elif quans[0].upper() in dic["smass"]:
        var *= GAS_DEN_REF
        vunit = initialize_mass(qskl)
    elif quans[0].lower() in ["time"]:
        vunit = " [d]"
    return time, var * qskl, tunit, vunit


def where_at(case, vec):
    """
    Using the input deck (.DATA) to read the i,j fault locations

    Args:
        case (str): Name of the deck\n
        vec (str): Keyword

    Returns:
        file (str): Name of the file where the vec at.

    """
    include = False
    path = ""
    if len(case.split("/")) > 1:
        path = "/".join(case.split("/")[:-1]) + "/"
    case = case + ".DATA"
    includes = []
    with open(case, "r", encoding="utf8") as file:
        for row in csv.reader(file):
            if len(row) > 0:
                if row[0] == vec:
                    return case
                if row[0] == "INCLUDE":
                    include = True
                    continue
                if include:
                    name = (row[0].split("/")[0]).strip(" ")
                    if "'" in name:
                        name = name[1:-1]
                    if os.path.isfile(path + name):
                        includes.append(path + name)
                        include = False
                        continue
    for include in includes:
        with open(include, "r", encoding="utf8") as file:
            for row in csv.reader(file):
                if len(row) > 0:
                    if row[0] == vec:
                        return include
    print(f"No {vec} found (only looking in {case} and INCLUDE files).")
    sys.exit()


def operate(var, quan1, i, oper):
    """
    Applied the requested operation

    Args:
        var (array): Floats with the current values\n
        quan1 (array): Value(s) to operate\n
        i (int): Index of the operator\n
        oper (list): Input operators

    Returns:
        var (array): Modified values after applying the operator

    """
    if oper[i] == "+":
        var += quan1
    elif oper[i] == "-":
        var -= quan1
    elif oper[i] == "*":
        var *= quan1
    elif oper[i] == "/":
        var /= quan1
    elif oper[i] == "==":
        var[~np.isnan(var)] = [
            1 if val == quan1 else np.nan for val in var[~np.isnan(var)]
        ]
    elif oper[i] == ">=":
        var[~np.isnan(var)] = [
            1 if val >= quan1 else np.nan for val in var[~np.isnan(var)]
        ]
    elif oper[i] == "<=":
        var[~np.isnan(var)] = [
            1 if val <= quan1 else np.nan for val in var[~np.isnan(var)]
        ]
    elif oper[i] == "<":
        var[~np.isnan(var)] = [
            1 if val < quan1 else np.nan for val in var[~np.isnan(var)]
        ]
    elif oper[i] == ">":
        var[~np.isnan(var)] = [
            1 if val > quan1 else np.nan for val in var[~np.isnan(var)]
        ]
    elif oper[i] == "!=":
        var[~np.isnan(var)] = [
            1 if val != quan1 else np.nan for val in var[~np.isnan(var)]
        ]
    else:
        print(f"Unknow operation ({oper[i]}).")
        sys.exit()
    return var


def initialize_time(times):
    """
    Handle the time units for the x axis in the summary

    Args:
        times (str): Type for the time to plot

    Returns:
        scale (float): Scale for the times\n
        unit (str): Units for the x label

    """
    scale, unit = 1.0 * 86400, "Time [seconds]"
    if times == "s":
        scale, unit = 1.0 * 86400, "Time [seconds]"
    if times == "m":
        scale, unit = 1.0 * 86400 / 60, "Time [minutes]"
    if times == "h":
        scale, unit = 1.0 * 86400 / 3600, "Time [hours]"
    if times == "d":
        scale, unit = 1.0 * 86400 / 86400, "Time [days]"
    if times == "w":
        scale, unit = 1.0 * 86400 / 604800, "Time [weeks]"
    if times == "y":
        scale, unit = 1.0 * 86400 / 31557600, "Time [years]"
    if times == "dates":
        scale, unit = 1, "Dates"
    return scale, unit


def get_csvs(dic, n):
    """
    Read the csv quantities

    Args:
        dic (dict): Global dictionary\n
        n (int): Number of deck

    Returns:
        dic (dict): Modified global dictionary

    """
    csvv = np.genfromtxt(
        f"{dic['deck']}.csv",
        delimiter=",",
        skip_header=1,
    )
    x = csvv[-1][dic["csvs"][n][0] - 1] + csvv[0][dic["csvs"][n][0] - 1]
    y = csvv[-1][dic["csvs"][n][1] - 1] + csvv[0][dic["csvs"][n][1] - 1]
    dic["mx"] = round(x / (2.0 * csvv[0][dic["csvs"][n][0] - 1]))
    dic["my"] = round(y / (2.0 * csvv[0][dic["csvs"][n][1] - 1]))
    dic["xmx"] = np.linspace(0, x, dic["mx"] + 1)
    dic["ymy"] = np.linspace(0, y, dic["my"] + 1)
    dic["xc"], dic["yc"] = np.meshgrid(dic["xmx"], dic["ymy"][::-1])
    dic["xc"], dic["yc"] = dic["xc"].tolist(), dic["yc"].tolist()
    dic["xmeaning"], dic["ymeaning"] = "x", "y"
    dic["nslide"] = "csv"


def handle_filter(porvs, quan1, oper, value):
    """
    Applied the requested filter

    Args:
        dic (dict): Global dictionary\n

    Returns:
        var (array): Modified values after applying the operator

    """
    if oper == "==":
        porvs = [porv if val == value else 0 for porv, val in zip(porvs, quan1)]
    elif oper == ">=":
        porvs = [porv if val >= value else 0 for porv, val in zip(porvs, quan1)]
    elif oper == "<=":
        porvs = [porv if val <= value else 0 for porv, val in zip(porvs, quan1)]
    elif oper == "<":
        porvs = [porv if val < value else 0 for porv, val in zip(porvs, quan1)]
    elif oper == ">":
        porvs = [porv if val > value else 0 for porv, val in zip(porvs, quan1)]
    elif oper == "!=":
        porvs = [porv if val != value else 0 for porv, val in zip(porvs, quan1)]
    else:
        print(f"Unknow filter ({oper}).")
        sys.exit()
    return porvs


def get_readers(dic, n=0):
    """
    Load the opm parsing methods

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for ext in ["init", "unrst"]:
        if os.path.isfile(f"{dic['deck']}.{ext.upper()}"):
            dic[ext] = []
            if ext == "init":
                dic[ext] = OpmFile(f"{dic['deck']}.{ext.upper()}")
            else:
                dic[ext] = OpmRestart(f"{dic['deck']}.{ext.upper()}")
    if os.path.isfile(f"{dic['deck']}.EGRID") and dic["mode"] != "vtk":
        dic["egrid"] = []
        dic["egrid"] = OpmGrid(f"{dic['deck']}.EGRID")
    if not "init" in dic.keys() and not "unrst" in dic.keys():
        print(f"Unable to find {dic['deck']} with .EGRID or .INIT.")
        sys.exit()
    dic["tnrst"] = []
    dic["ntot"] = 1
    dic["porv"] = np.array(dic["init"]["PORV"])
    dic["dx"] = np.array(dic["init"]["DX"])
    dic["dy"] = np.array(dic["init"]["DY"])
    dic["dz"] = np.array(dic["init"]["DZ"])
    dic["nxyz"] = len(dic["porv"])
    dic["pv"] = np.array([porv for porv in dic["porv"] if porv > 0])
    dic["actind"] = np.cumsum([1 if porv > 0 else 0 for porv in dic["porv"]]) - 1
    if dic["filter"][n]:
        porv0 = np.array(dic["init"]["PORV"])
        for value in dic["filter"][n].split("&"):
            filte = (value.strip()).split(" ")
            quan1 = filte[0].upper()
            if dic["init"].count(quan1):
                quan1 = np.array(dic["init"][quan1])
            else:
                continue
            dic["porv"][porv0 > 0] = handle_filter(
                dic["porv"][porv0 > 0], quan1, filte[1], float(filte[2])
            )
    if "unrst" in dic.keys():
        dic["ntot"] = len(dic["unrst"].report_steps)
        for ntm in dic["unrst"].report_steps:
            dic["tnrst"].append(dic["unrst"]["DOUBHEAD", ntm][0])
    if "egrid" in dic.keys():
        dic["nx"] = dic["egrid"].dimension[0]
        dic["ny"] = dic["egrid"].dimension[1]
        dic["nz"] = dic["egrid"].dimension[2]
    if dic["restart"][0] == -1:
        if dic["mode"] == "gif":
            dic["restart"] = dic["unrst"].report_steps
        else:
            dic["restart"] = [dic["ntot"] - 1]
    if not dic["tnrst"]:
        dic["tnrst"] = [0] * len(dic["restart"])


def get_unit(name):
    """
    Get the variable unit

    Args:
        name (str): Variable

    Returns:
        dic (dict): Modified global dictionary

    """
    if name.lower() in ["disperc", "depth", "dx", "dy", "dz"]:
        unit = " [m]"
    elif name.lower() in ["porv"]:
        unit = r" [sm$^3$]"
    elif name.lower() in ["permx", "permy", "permz"]:
        unit = " [mD]"
    elif name.lower() in ["tranx", "trany", "tranz"]:
        unit = " [cP rm$^3$/ (day bar)]"
    elif name.lower() in ["pressure", "rpr", "fpr", "fprr", "wbhp"]:
        unit = " [bar]"
    elif name.lower() in ["fgip", "fgit"]:
        unit = " [sm$^3$]"
    else:
        unit = " [-]"
    return unit


def get_quantity(dic, name, n, nrst, m):
    """
    Compute the mass (intensive quantities).

    Args:
        dic (dict): Global dictionary\n
        name (str): Name of the variable\n
        skl (float): Scaling for the mass quantity\n
        nrst (int): Number of restart step

    Returns:
        unit (str): Corresponding physical unit\n
        quan (array): Floats with the requested quantity

    """
    skl = float(dic["avar"][n])
    unit = get_unit(name)
    names = name.split(" ")
    if dic["csvs"][m][0]:
        csvv = np.genfromtxt(
            f"{dic['deck']}.csv",
            delimiter=",",
            skip_header=1,
        )
        quan = np.array([csvv[i][dic["csvs"][m][2] - 1] for i in range(csvv.shape[0])])
    else:
        if dic["init"].count(names[0]):
            quan = dic["init"][names[0]] * 1.0
            if names[0].lower() == "porv":
                quan = dic["pv"]
        elif names[0].lower() == "grid":
            quan = np.array(dic["init"]["SATNUM"]) * 0
        elif names[0].lower() == "wells":
            quan = np.array(dic["init"]["SATNUM"]) * 0
            dic["wells"] = []
            get_wells(dic, n)
        elif names[0].lower() == "faults":
            quan = np.array(dic["init"]["SATNUM"]) * 0
            dic["faults"] = []
            get_faults(dic, n)
        elif "index" in names[0].lower():
            quan = np.array(dic["init"]["SATNUM"]) * 0
        elif dic["unrst"].count(names[0], nrst):
            quan = dic["unrst"][names[0], nrst]
            if dic["unrst"].count("RPORV", nrst):
                if dic["filter"][m]:
                    porv0 = np.array(dic["init"]["PORV"])
                    for value in dic["filter"][m].split("&"):
                        filte = (value.strip()).split(" ")
                        quan1 = filte[0].upper()
                        if dic["init"].count(quan1):
                            quan1 = np.array(dic["init"][quan1])
                        elif dic["unrst"].count(quan1, nrst):
                            quan1 = np.array(dic["unrst"][quan1, nrst])
                        else:
                            print(f"Unknow filter quantity ({filte[0].upper()}).")
                            sys.exit()
                        dic["porv"][porv0 > 0] = np.array(
                            handle_filter(
                                np.array(dic["unrst"]["RPORV", nrst]),
                                quan1,
                                filte[1],
                                float(filte[2]),
                            )
                        )
                else:
                    dic["porv"][dic["porv"] > 0] = np.array(dic["unrst"]["RPORV", nrst])
        elif names[0].lower() in dic["mass"] + dic["xmass"]:
            quan = handle_mass(dic, names[0].lower(), nrst) * skl
            if names[0].lower() in dic["mass"]:
                unit = initialize_mass(skl)
        elif names[0].lower() in dic["caprock"]:
            quan, unit = handle_caprock(dic, names[0].lower(), nrst)
        else:
            print(f"Unknow -v variable ({names[0]}).")
            sys.exit()
        if len(names) > 1:
            for j, val in enumerate(names[2::2]):
                if (val[0]).isdigit() and not val[-1].isdigit():
                    quan1 = dic["unrst"][val[1:], int(val[0])]
                elif (val[0]).isdigit() and val[-1].isdigit():
                    quan1 = float(val)
                elif dic["init"].count(val):
                    quan1 = dic["init"][val]
                elif dic["unrst"].count(val, nrst):
                    quan1 = dic["unrst"][val, nrst]
                elif val.lower() in dic["mass"] + dic["xmass"]:
                    quan1 = handle_mass(dic, val.lower(), nrst) * skl
                elif val.lower() in dic["caprock"]:
                    quan1, unit = handle_caprock(dic, val.lower(), nrst)
                quan = operate(quan, quan1, j, names[1::2])
    if dic["vmin"][n]:
        quan = np.array(quan)
        quan[quan < float(dic["vmin"][n])] = np.nan
    if dic["vmax"][n]:
        quan = np.array(quan)
        quan[float(dic["vmax"][n]) < quan] = np.nan
    return unit, quan


def handle_mass(dic, name, nrst):
    """
    Compute the mass (intensive quantities).

    Args:
        dic (dict): Global dictionary\n
        name (str): Name of the variable for the mass spatial map\n
        nrst (int): Number of restart step

    Returns:
        mass (array): Floats with the computed mass

    """
    sgas = np.array(dic["unrst"]["SGAS", nrst])
    rhog = np.array(dic["unrst"]["GAS_DEN", nrst])
    rhow = np.array(dic["unrst"]["WAT_DEN", nrst])
    if dic["unrst"].count("RSW", nrst):
        rsw = np.array(dic["unrst"]["RSW", nrst])
    else:
        rsw = 0.0 * sgas
    if dic["unrst"].count("RVW", nrst):
        rvw = np.array(dic["unrst"]["RVW", nrst])
    else:
        rvw = 0.0 * sgas
    if dic["unrst"].count("RPORV", nrst):
        rpv = np.array(dic["unrst"]["RPORV", nrst])
    else:
        rpv = dic["pv"]
    x_l_co2 = np.divide(rsw, rsw + WAT_DEN_REF / GAS_DEN_REF)
    x_g_h2o = np.divide(rvw, rvw + GAS_DEN_REF / WAT_DEN_REF)
    co2_g = (1 - x_g_h2o) * sgas * rhog * rpv
    co2_d = x_l_co2 * (1.0 - sgas) * rhow * rpv
    h2o_l = (1 - x_l_co2) * (1 - sgas) * rhow * rpv
    h2o_v = x_g_h2o * sgas * rhog * rpv
    return type_of_mass(name, co2_g, co2_d, h2o_l, h2o_v, x_l_co2, x_g_h2o)


def type_of_mass(name, co2_g, co2_d, h2o_l, h2o_v, x_l_co2, x_g_h2o):
    """
    From the given variable return the associated mass

    Args:
        name (str): Name of the variable for the mass spatial map\n
        co2_g: Mass of CO2 in the gas phase\n
        co2_d: Mass of CO2 in the liquid phase\n
        h2o_l: Mass of H2O in the liquid phase\n
        h2o_v: Mass of H2O in the gas phase

    Returns:
        mass (array): Floats with the computed mass

    """
    if name == "gasm":
        return co2_g
    if name == "dism":
        return co2_d
    if name == "liqm":
        return h2o_l
    if name == "vapm":
        return h2o_v
    if name == "h2om":
        return h2o_v + h2o_l
    if name == "xco2l":
        return x_l_co2
    if name == "xh2ov":
        return x_g_h2o
    if name == "xco2v":
        return 1 - x_g_h2o
    if name == "xh2ol":
        return 1 - x_l_co2
    return co2_g + co2_d


def handle_caprock(dic, name, nrst):
    """
    Compute quantities related to the caprock integrity.

    Args:
        dic (dict): Global dictionary\n
        name (str): Name of the variable for the mass spatial map\n
        nrst (int): Number of restart step

    Returns:
        mass (array): Floats with the computed mass

    """
    dz_corr = 0.5 * np.array(dic["init"]["DZ", 0])
    if dic["unrst"].count("WAT_DEN", 0) and dic["unrst"].count("WAT_DEN", nrst):
        den0 = np.array(dic["unrst"]["WAT_DEN", 0])
        den1 = np.array(dic["unrst"]["WAT_DEN", nrst])
    else:
        den0, den1 = 1000, 1000
    pz_c0 = 9.81 * dz_corr * den0 / 1e5
    pz_c1 = 9.81 * dz_corr * den1 / 1e5
    limipres = dic["stress"] * (
        np.array(dic["init"]["DEPTH", 0]) - 0.5 * np.array(dic["init"]["DZ", 0])
    )
    overpres = limipres - (np.array(dic["unrst"]["PRESSURE", nrst]) - pz_c1)
    limipres -= np.array(dic["unrst"]["PRESSURE", 0]) - pz_c0
    objepres = np.divide(overpres, limipres)
    if name == "limipres":
        return limipres, " [Bar]"
    if name == "overpres":
        return -overpres, " [Bar]"
    return objepres, " [-]"


def get_wells(dic, n):
    """
    Using the input deck (.DATA) to read the i,j well locations

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["lwells"] = []
    dic["wellsa"] = np.ones((dic["mx"]) * (dic["my"])) * np.nan
    dic["grida"] = np.ones((dic["mx"]) * (dic["my"])) * np.nan
    wells, sources = False, False
    with open(f"{dic['name']}.DATA", "r", encoding="utf8") as file:
        for row in csv.reader(file):
            nrwo = str(row)[2:-2]
            if wells:
                if len(nrwo.split()) < 2:
                    if nrwo == "/":
                        wells = False
                    continue
                if nrwo.split()[0] == "--" or nrwo.split()[0][:2] == "--":
                    continue
                if nrwo.split()[0] not in dic["lwells"]:
                    dic["lwells"].append(str(nrwo.split()[0]))
                    dic["wells"].append([])
                dic["wells"][dic["lwells"].index(nrwo.split()[0])].append(
                    [
                        int(nrwo.split()[1]) - 1,
                        int(nrwo.split()[2]) - 1,
                        int(nrwo.split()[3]) - 1,
                        int(nrwo.split()[4]) - 1,
                    ]
                )
            if sources:
                if len(nrwo.split()) < 2:
                    if nrwo == "/":
                        wells = False
                    continue
                if nrwo.split()[0] == "--" or nrwo.split()[0][:2] == "--":
                    continue
                if nrwo.split()[0] not in dic["lwells"]:
                    dic["lwells"].append(nrwo.split()[0])
                    dic["wells"].append([])
                dic["wells"][dic["lwells"].index(nrwo.split()[0])].append(
                    [
                        int(nrwo.split()[0]) - 1,
                        int(nrwo.split()[1]) - 1,
                        int(nrwo.split()[2]) - 1,
                        int(nrwo.split()[2]) - 1,
                    ]
                )
            if len(nrwo.split()) < 1:
                if nrwo == "COMPDAT":
                    wells = True
                if nrwo == "SOURCE":
                    sources = True
            else:
                if nrwo.split()[0] == "COMPDAT":
                    wells = True
                if nrwo.split()[0] == "SOURCE":
                    sources = True
    dic["nwells"] = len(dic["lwells"]) + 1
    if dic["global"] == 0:
        if dic["slide"][n][0][0] > -1:
            for i, wells in enumerate(dic["wells"]):
                for j, well in enumerate(wells):
                    if dic["whow"] == "min":
                        count = 0
                        for sld in range(dic["slide"][n][0][0], dic["slide"][n][0][1]):
                            if well[0] == sld:
                                count = 1
                                break
                        if count == 0:
                            dic["wells"][i][j] = []
                    else:
                        for sld in range(dic["slide"][n][0][0], dic["slide"][n][0][1]):
                            if well[0] != sld:
                                dic["wells"][i][j] = []
        elif dic["slide"][n][1][0] > -1:
            for i, wells in enumerate(dic["wells"]):
                for j, well in enumerate(wells):
                    if dic["whow"] == "min":
                        count = 0
                        for sld in range(dic["slide"][n][1][0], dic["slide"][n][1][1]):
                            if well[1] == sld:
                                count = 1
                                break
                        if count == 0:
                            dic["wells"][i][j] = []
                    else:
                        for sld in range(dic["slide"][n][1][0], dic["slide"][n][1][1]):
                            if well[1] != sld:
                                dic["wells"][i][j] = []
        else:
            for i, wells in enumerate(dic["wells"]):
                for j, well in enumerate(wells):
                    if dic["whow"] == "min":
                        count = 0
                        for sld in range(dic["slide"][n][2][0], dic["slide"][n][2][1]):
                            if sld in range(well[2], well[3] + 1):
                                count = 1
                                break
                        if count == 0:
                            dic["wells"][i][j] = []
                    else:
                        for sld in range(dic["slide"][n][2][0], dic["slide"][n][2][1]):
                            if sld not in range(well[2], well[3] + 1):
                                dic["wells"][i][j] = []


def get_faults(dic, n):
    """
    Using the input deck (.DATA) to read the i,j fault locations

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["lfaults"] = []
    dic["faultsa"] = np.ones((dic["mx"]) * (dic["my"])) * np.nan
    dic["grida"] = np.ones((dic["mx"]) * (dic["my"])) * np.nan
    faults = False
    with open(f"{dic['name']}.DATA", "r", encoding="utf8") as file:
        for row in csv.reader(file):
            nrwo = str(row)[2:-2]
            if faults:
                if len(nrwo.split()) < 2:
                    if nrwo == "/" or "/" in nrwo:
                        break
                    continue
                if nrwo.split()[0] == "--" or nrwo.split()[0][:2] == "--":
                    continue
                if nrwo.split()[0] not in dic["lfaults"]:
                    dic["lfaults"].append(nrwo.split()[0])
                    dic["faults"].append([])
                dic["faults"][dic["lfaults"].index(nrwo.split()[0])].append(
                    [
                        int(nrwo.split()[1]) - 1,
                        int(nrwo.split()[3]) - 1,
                        int(nrwo.split()[5]) - 1,
                        int(nrwo.split()[6]) - 1,
                    ]
                )
            if len(nrwo.split()) < 1:
                if nrwo == "FAULTS":
                    faults = True
            else:
                if nrwo.split()[0] == "FAULTS":
                    faults = True
    dic["nfaults"] = len(dic["lfaults"]) + 1
    if dic["global"] == 0:
        if dic["slide"][n][0][0] > -1:
            for i, faults in enumerate(dic["faults"]):
                for j, fault in enumerate(faults):
                    if dic["whow"] == "min":
                        count = 0
                        for sld in range(dic["slide"][n][0][0], dic["slide"][n][0][1]):
                            if fault[0] == sld:
                                count = 1
                                break
                        if count == 0:
                            dic["faults"][i][j] = []
                    else:
                        for sld in range(dic["slide"][n][0][0], dic["slide"][n][0][1]):
                            if fault[0] != sld:
                                dic["faults"][i][j] = []
        elif dic["slide"][n][1][0] > -1:
            for i, faults in enumerate(dic["faults"]):
                for j, fault in enumerate(faults):
                    if dic["whow"] == "min":
                        count = 0
                        for sld in range(dic["slide"][n][1][0], dic["slide"][n][1][1]):
                            if fault[1] == sld:
                                count = 1
                                break
                        if count == 0:
                            dic["faults"][i][j] = []
                    else:
                        for sld in range(dic["slide"][n][1][0], dic["slide"][n][1][1]):
                            if fault[1] != sld:
                                dic["faults"][i][j] = []
        else:
            for i, faults in enumerate(dic["faults"]):
                for j, fault in enumerate(faults):
                    if dic["whow"] == "min":
                        count = 0
                        for sld in range(dic["slide"][n][2][0], dic["slide"][n][2][1]):
                            if sld in range(fault[2], fault[3] + 1):
                                count = 1
                                break
                        if count == 0:
                            dic["faults"][i][j] = []
                    else:
                        for sld in range(dic["slide"][n][2][0], dic["slide"][n][2][1]):
                            if sld not in range(fault[2], fault[3] + 1):
                                dic["faults"][i][j] = []
