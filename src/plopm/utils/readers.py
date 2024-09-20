# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0911,R0912,R0913,R0915

"""
Utiliy functions to read the OPM Flow simulator type output files.
"""

import os
import csv
import sys
import datetime
import numpy as np
from plopm.utils.initialization import initialize_mass

try:
    from opm.io.ecl import EclFile as OpmFile
    from opm.io.ecl import EGrid as OpmGrid
    from opm.io.ecl import ESmry as OpmSummary
except ImportError:
    pass
try:
    from resdata.resfile import ResdataFile
    from resdata.summary import Summary
    from resdata.grid import Grid
except ImportError:
    pass

GAS_DEN_REF = 1.86843
WAT_DEN_REF = 998.108


def get_yzcoords_resdata(dic, m):
    """
    Handle the coordinates from the OPM Grid to the 2D yz-mesh using resdata

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["mesh"] = dic["egrid"].export_corners(dic["egrid"].export_index())
    s_l = dic["slide"][m][0]
    for j in range(dic["nz"]):
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [1, 7, 2, 8]):
            dic[f"{k}c"][-1].append(
                dic["mesh"][(dic["nz"] - j - 1) * dic["nx"] * dic["ny"] + s_l][n]
            )
        for i in range(dic["ny"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [1, 7, 2, 8]):
                dic[f"{k}c"][-1].append(
                    dic["mesh"][
                        (i + 1) * dic["nx"]
                        + (dic["nz"] - j - 1) * dic["nx"] * dic["ny"]
                        + s_l
                    ][n]
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [13, 19, 14, 20]):
            dic[f"{k}c"][-1].append(
                dic["mesh"][(dic["nz"] - j - 1) * dic["nx"] * dic["ny"] + s_l][n]
            )
        for i in range(dic["ny"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [13, 19, 14, 20]):
                dic[f"{k}c"][-1].append(
                    dic["mesh"][
                        (i + 1) * dic["nx"]
                        + (dic["nz"] - j - 1) * dic["nx"] * dic["ny"]
                        + s_l
                    ][n]
                )


def get_yzcoords_opm(dic, n):
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
        for k, c, p in zip(["x", "x", "y", "y"], [1, 1, 2, 2], [0, 2, 0, 2]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(dic["slide"][n][0], 0, dic["nz"] - j - 1)[c][
                    p
                ]
            )
        for i in range(dic["ny"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [1, 1, 2, 2], [0, 2, 0, 2]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(
                        dic["slide"][n][0], i + 1, dic["nz"] - j - 1
                    )[c][p]
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, c, p in zip(["x", "x", "y", "y"], [1, 1, 2, 2], [4, 6, 4, 6]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(dic["slide"][n][0], 0, dic["nz"] - j - 1)[c][
                    p
                ]
            )
        for i in range(dic["ny"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [1, 1, 2, 2], [4, 6, 4, 6]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(
                        dic["slide"][n][0], i + 1, dic["nz"] - j - 1
                    )[c][p]
                )


def get_xzcoords_resdata(dic, m):
    """
    Handle the coordinates from the OPM Grid to the 2D xz-mesh using resdata

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["mesh"] = dic["egrid"].export_corners(dic["egrid"].export_index())
    s_l = dic["slide"][m][1] * dic["nx"]
    for j in range(dic["nz"]):
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [0, 3, 2, 5]):
            dic[f"{k}c"][-1].append(
                dic["mesh"][(dic["nz"] - j - 1) * dic["nx"] * dic["ny"] + s_l][n]
            )
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [0, 3, 2, 5]):
                dic[f"{k}c"][-1].append(
                    dic["mesh"][
                        1 + i + (dic["nz"] - j - 1) * dic["nx"] * dic["ny"] + s_l
                    ][n]
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [12, 15, 14, 17]):
            dic[f"{k}c"][-1].append(
                dic["mesh"][(dic["nz"] - j - 1) * dic["nx"] * dic["ny"] + s_l][n]
            )
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [12, 15, 14, 17]):
                dic[f"{k}c"][-1].append(
                    dic["mesh"][
                        1 + i + (dic["nz"] - j - 1) * dic["nx"] * dic["ny"] + s_l
                    ][n]
                )


def get_xzcoords_opm(dic, n):
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
        for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 2, 2], [0, 1, 0, 1]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(0, dic["slide"][n][1], dic["nz"] - j - 1)[c][
                    p
                ]
            )
        for i in range(dic["nx"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 2, 2], [0, 1, 0, 1]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(
                        i + 1, dic["slide"][n][1], dic["nz"] - j - 1
                    )[c][p]
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 2, 2], [4, 5, 4, 5]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(0, dic["slide"][n][1], dic["nz"] - j - 1)[c][
                    p
                ]
            )
        for i in range(dic["nx"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 2, 2], [4, 5, 4, 5]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(
                        1 + i, dic["slide"][n][1], dic["nz"] - j - 1
                    )[c][p]
                )


def get_xycoords_resdata(dic, m):
    """
    Handle the coordinates from the OPM Grid to the 2D xy-mesh using resdata

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["mesh"] = dic["egrid"].export_corners(dic["egrid"].export_index())
    s_l = dic["slide"][m][2] * dic["nx"] * dic["ny"]
    for j in range(dic["ny"]):
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [0, 3, 1, 4]):
            dic[f"{k}c"][-1].append(dic["mesh"][j * dic["nx"] + s_l][n])
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [0, 3, 1, 4]):
                dic[f"{k}c"][-1].append(dic["mesh"][1 + i + j * dic["nx"] + s_l][n])
        dic["xc"].append([])
        dic["yc"].append([])
        for k, n in zip(["x", "x", "y", "y"], [6, 9, 7, 10]):
            dic[f"{k}c"][-1].append(dic["mesh"][j * dic["nx"] + s_l][n])
        for i in range(dic["nx"] - 1):
            for k, n in zip(["x", "x", "y", "y"], [6, 9, 7, 10]):
                dic[f"{k}c"][-1].append(dic["mesh"][1 + i + j * dic["nx"] + s_l][n])


def get_xycoords_opm(dic, n):
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
                dic["egrid"].xyz_from_ijk(0, j, dic["slide"][n][2])[c][p]
            )
        for i in range(dic["nx"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 1, 1], [0, 1, 0, 1]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(i + 1, j, dic["slide"][n][2])[c][p]
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 1, 1], [2, 3, 2, 3]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(0, j, dic["slide"][n][2])[c][p]
            )
        for i in range(dic["nx"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 1, 1], [2, 3, 2, 3]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(i + 1, j, dic["slide"][n][2])[c][p]
                )


def read_summary(dic, case, quan, tunit, qskl):
    """
    Handle the summary vectors

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    vunit = ""
    tskl, tunit = initialize_time(tunit)
    quans = quan.split(" ")
    if dic["use"] == "resdata":
        summary = Summary(f"{case}.SMSPEC")
        if quans[0].upper() in dic["smass"]:
            var = summary[quans[0][:-1].upper()].values
        else:
            var = summary[quans[0].upper()].values
        if len(quans) > 1:
            for i, val in enumerate(quans[2::2]):
                if val.upper() in summary.keys():
                    quan1 = summary[val.upper()].values
                else:
                    quan1 = float(val)
                var = operate(var, quan1, i, quans[1::2])
        if tunit == "Dates":
            time = summary.dates
        else:
            time = summary["TIME"].values * tskl
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


def get_readers(dic):
    """
    Load the opm/resdata methods

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for ext in ["init", "unrst"]:
        if os.path.isfile(f"{dic['deck']}.{ext.upper()}"):
            dic[ext] = []
            if dic["use"] == "resdata":
                dic[ext] = ResdataFile(f"{dic['deck']}.{ext.upper()}")
            else:
                dic[ext] = OpmFile(f"{dic['deck']}.{ext.upper()}")
    if os.path.isfile(f"{dic['deck']}.EGRID") and dic["mode"] != "vtk":
        dic["egrid"] = []
        if dic["use"] == "resdata":
            dic["egrid"] = Grid(f"{dic['deck']}.EGRID")
        else:
            dic["egrid"] = OpmGrid(f"{dic['deck']}.EGRID")
    if not "init" in dic.keys() and not "unrst" in dic.keys():
        print(f"Unable to find {dic['deck']} with .EGRID or .INIT.")
        sys.exit()
    dic["tnrst"] = []
    dic["ntot"] = 1
    if dic["use"] == "resdata":
        dic["porv"] = np.array(dic["init"]["PORV"][0])
        dic["nxyz"] = len(dic["porv"])
        dic["pv"] = np.array([porv for porv in dic["porv"] if porv > 0])
        dic["actind"] = np.cumsum([1 if porv > 0 else 0 for porv in dic["porv"]]) - 1
        if "unrst" in dic.keys():
            dic["ntot"] = len(dic["unrst"].iget_kw("PRESSURE"))
            for ntm in range(dic["ntot"]):
                dic["tnrst"].append(dic["unrst"]["DOUBHEAD"][ntm][0])
        if "egrid" in dic.keys():
            dic["nx"] = dic["egrid"].nx
            dic["ny"] = dic["egrid"].ny
            dic["nz"] = dic["egrid"].nz
    else:
        dic["porv"] = np.array(dic["init"]["PORV"])
        dic["nxyz"] = len(dic["porv"])
        dic["pv"] = np.array([porv for porv in dic["porv"] if porv > 0])
        dic["actind"] = np.cumsum([1 if porv > 0 else 0 for porv in dic["porv"]]) - 1
        if "unrst" in dic.keys():
            dic["ntot"] = dic["unrst"].count("PRESSURE")
            for ntm in range(dic["ntot"]):
                dic["tnrst"].append(dic["unrst"]["DOUBHEAD", ntm][0])
        if "egrid" in dic.keys():
            dic["nx"] = dic["egrid"].dimension[0]
            dic["ny"] = dic["egrid"].dimension[1]
            dic["nz"] = dic["egrid"].dimension[2]
    if not dic["tnrst"]:
        dic["tnrst"] = [0] * len(dic["restart"])
    if dic["restart"][0] == -1:
        dic["restart"] = [dic["ntot"] - 1]


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
        unit = r" [m$^3$]"
    elif name.lower() in ["permx", "permy", "permz"]:
        unit = " [mD]"
    elif name.lower() in ["pressure"]:
        unit = " [bar]"
    elif name.lower() in ["fgip", "fgit"]:
        unit = " [sm$^3$]"
    else:
        unit = " [-]"
    return unit


def get_quantity(dic, name, n, nrst):
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
    if dic["use"] == "resdata":
        if dic["init"].has_kw(names[0]):
            quan = np.array(dic["init"][names[0]][0]) * 1.0
            if names[0].lower() == "porv":
                quan = dic["pv"]
        elif names[0].lower() == "grid":
            quan = np.array(dic["init"]["SATNUM"][0]) * 0
        elif names[0].lower() == "wells":
            quan = np.array(dic["init"]["SATNUM"][0]) * 0
            dic["wells"] = []
            get_wells(dic)
        elif "index" in names[0].lower():
            quan = np.array(dic["init"]["SATNUM"][0]) * 0
        elif dic["unrst"].has_kw(names[0]):
            quan = np.array(dic["unrst"][names[0]][nrst]) * 1.0
        elif names[0].lower() in dic["mass"] + dic["xmass"]:
            quan = handle_mass(dic, names[0].lower(), nrst) * skl
            if names[0].lower() in dic["mass"]:
                unit = initialize_mass(skl)
        else:
            print(f"Unknow -v variable ({names[0]}).")
            sys.exit()
        if len(names) > 1:
            for j, val in enumerate(names[2::2]):
                if dic["init"].has_kw(val):
                    quan1 = np.array(dic["init"][val][0]) * 1.0
                elif dic["unrst"].has_kw(val):
                    quan1 = np.array(dic["unrst"][val][nrst]) * 1.0
                elif val.lower() in dic["mass"] + dic["xmass"]:
                    quan1 = handle_mass(dic, val.lower(), nrst) * skl
                else:
                    quan1 = float(val)
                quan = operate(quan, quan1, j, names[1::2])
    else:
        if dic["init"].count(names[0]):
            quan = dic["init"][names[0]]
            if names[0].lower() == "porv":
                quan = dic["pv"]
        elif names[0].lower() == "grid":
            quan = np.array(dic["init"]["SATNUM"]) * 0
        elif names[0].lower() == "wells":
            quan = np.array(dic["init"]["SATNUM"]) * 0
            dic["wells"] = []
            get_wells(dic)
        elif "index" in names[0].lower():
            quan = np.array(dic["init"]["SATNUM"]) * 0
        elif dic["unrst"].count(names[0]):
            quan = dic["unrst"][names[0], nrst]
        elif names[0].lower() in dic["mass"] + dic["xmass"]:
            quan = handle_mass(dic, names[0].lower(), nrst) * skl
            if names[0].lower() in dic["mass"]:
                unit = initialize_mass(skl)
        else:
            print(f"Unknow -v variable ({names[0]}).")
            sys.exit()
        if len(names) > 1:
            for j, val in enumerate(names[2::2]):
                if dic["init"].count(val):
                    quan1 = dic["init"][val]
                elif dic["unrst"].count(val):
                    quan1 = dic["unrst"][val, nrst]
                elif val.lower() in dic["mass"] + dic["xmass"]:
                    quan1 = handle_mass(dic, val.lower(), nrst) * skl
                else:
                    quan1 = float(val)
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
    if dic["use"] == "resdata":
        sgas = np.array(dic["unrst"]["SGAS"][nrst])
        rhog = np.array(dic["unrst"]["GAS_DEN"][nrst])
        rhow = np.array(dic["unrst"]["WAT_DEN"][nrst])
        if dic["unrst"].has_kw("RSW"):
            rsw = np.array(dic["unrst"]["RSW"][nrst])
        else:
            rsw = 0.0 * sgas
        if dic["unrst"].has_kw("RVW"):
            rvw = np.array(dic["unrst"]["RVW"][nrst])
        else:
            rvw = 0.0 * sgas
    else:
        sgas = np.array(dic["unrst"]["SGAS", nrst])
        rhog = np.array(dic["unrst"]["GAS_DEN", nrst])
        rhow = np.array(dic["unrst"]["WAT_DEN", nrst])
        if dic["unrst"].count("RSW"):
            rsw = np.array(dic["unrst"]["RSW", nrst])
        else:
            rsw = 0.0 * sgas
        if dic["unrst"].count("RVW"):
            rvw = np.array(dic["unrst"]["RVW", nrst])
        else:
            rvw = 0.0 * sgas
    x_l_co2 = np.divide(rsw, rsw + WAT_DEN_REF / GAS_DEN_REF)
    x_g_h2o = np.divide(rvw, rvw + GAS_DEN_REF / WAT_DEN_REF)
    co2_g = (1 - x_g_h2o) * sgas * rhog * dic["pv"]
    co2_d = x_l_co2 * (1.0 - sgas) * rhow * dic["pv"]
    h2o_l = (1 - x_l_co2) * (1 - sgas) * rhow * dic["pv"]
    h2o_v = x_g_h2o * sgas * rhog * dic["pv"]
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


def get_wells(dic):
    """
    Using the input deck (.DATA) to read the i,j well locations

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["wellsa"] = np.ones((dic["mx"]) * (dic["my"])) * np.nan
    dic["grida"] = np.ones((dic["mx"]) * (dic["my"])) * np.nan
    wells, sources = False, False
    with open(f"{dic['name']}.DATA", "r", encoding="utf8") as file:
        for row in csv.reader(file):
            nrwo = str(row)[2:-2]
            if wells:
                if len(nrwo.split()) < 2:
                    break
                dic["wells"].append(
                    [
                        int(nrwo.split()[1]) - 1,
                        int(nrwo.split()[2]) - 1,
                        int(nrwo.split()[3]) - 1,
                        int(nrwo.split()[4]) - 1,
                    ]
                )
            if sources:
                if len(nrwo.split()) < 2:
                    break
                dic["wells"].append(
                    [
                        int(nrwo.split()[0]) - 1,
                        int(nrwo.split()[1]) - 1,
                        int(nrwo.split()[2]) - 1,
                        int(nrwo.split()[2]) - 1,
                    ]
                )
            if nrwo == "COMPDAT":
                wells = True
            if nrwo == "SOURCE":
                sources = True
