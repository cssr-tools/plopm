# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions to read the OPM Flow simulator type output files.
"""

import csv
import sys
import datetime
import numpy as np

GAS_DEN_REF = 1.86843
WAT_DEN_REF = 998.108


def get_yzcoords_resdata(dic):
    """
    Handle the coordinates from the OPM Grid to the 2D yz-mesh using resdata

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["mesh"] = dic["egrid"].export_corners(dic["egrid"].export_index())
    s_l = dic["slide"][0]
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


def get_yzcoords_opm(dic):
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
                dic["egrid"].xyz_from_ijk(dic["slide"][0], 0, dic["nz"] - j - 1)[c][p]
            )
        for i in range(dic["ny"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [1, 1, 2, 2], [0, 2, 0, 2]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(
                        dic["slide"][0], i + 1, dic["nz"] - j - 1
                    )[c][p]
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, c, p in zip(["x", "x", "y", "y"], [1, 1, 2, 2], [4, 6, 4, 6]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(dic["slide"][0], 0, dic["nz"] - j - 1)[c][p]
            )
        for i in range(dic["ny"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [1, 1, 2, 2], [4, 6, 4, 6]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(
                        dic["slide"][0], i + 1, dic["nz"] - j - 1
                    )[c][p]
                )


def get_xzcoords_resdata(dic):
    """
    Handle the coordinates from the OPM Grid to the 2D xz-mesh using resdata

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["mesh"] = dic["egrid"].export_corners(dic["egrid"].export_index())
    s_l = dic["slide"][1] * dic["nx"]
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


def get_xzcoords_opm(dic):
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
                dic["egrid"].xyz_from_ijk(0, dic["slide"][1], dic["nz"] - j - 1)[c][p]
            )
        for i in range(dic["nx"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 2, 2], [0, 1, 0, 1]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(
                        i + 1, dic["slide"][1], dic["nz"] - j - 1
                    )[c][p]
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 2, 2], [4, 5, 4, 5]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(0, dic["slide"][1], dic["nz"] - j - 1)[c][p]
            )
        for i in range(dic["nx"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 2, 2], [4, 5, 4, 5]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(
                        1 + i, dic["slide"][1], dic["nz"] - j - 1
                    )[c][p]
                )


def get_xycoords_resdata(dic):
    """
    Handle the coordinates from the OPM Grid to the 2D xy-mesh using resdata

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["mesh"] = dic["egrid"].export_corners(dic["egrid"].export_index())
    s_l = dic["slide"][2] * dic["nx"] * dic["ny"]
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


def get_xycoords_opm(dic):
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
                dic["egrid"].xyz_from_ijk(0, j, dic["slide"][2])[c][p]
            )
        for i in range(dic["nx"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 1, 1], [0, 1, 0, 1]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(i + 1, j, dic["slide"][2])[c][p]
                )
        dic["xc"].append([])
        dic["yc"].append([])
        for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 1, 1], [2, 3, 2, 3]):
            dic[f"{k}c"][-1].append(
                dic["egrid"].xyz_from_ijk(0, j, dic["slide"][2])[c][p]
            )
        for i in range(dic["nx"] - 1):
            for k, c, p in zip(["x", "x", "y", "y"], [0, 0, 1, 1], [2, 3, 2, 3]):
                dic[f"{k}c"][-1].append(
                    dic["egrid"].xyz_from_ijk(i + 1, j, dic["slide"][2])[c][p]
                )


def get_kws_resdata(dic):
    """
    Get the static properties from the INIT file using ResdataFile

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["porv"] = np.array(dic["init"].iget_kw("PORV")[0])
    dic["porva"] = np.ones(dic["mx"] * dic["my"]) * np.nan
    dic["pv"] = np.array([porv for porv in dic["porv"] if porv > 0])
    dic["actind"] = np.cumsum([1 if porv > 0 else 0 for porv in dic["porv"]]) - 1
    for name in dic["props"]:
        if dic["init"].has_kw(name.upper()):
            dic[name] = np.array(dic["init"].iget_kw(name.upper())[0])
        elif dic["unrst"][0].has_kw(name.upper()):
            if len(dic["names"]) == 1:
                dic[name] = np.array(
                    dic["unrst"][0].iget_kw(name.upper())[dic["restart"] - 1]
                )
            else:
                dic[name] = np.array(
                    dic["unrst"][0].iget_kw(name.upper())[dic["restart"] - 1]
                ) - np.array(dic["unrst"][1].iget_kw(name.upper())[dic["restart"] - 1])
            ntot = len(dic["unrst"][0].iget_kw(name.upper()))
            dic["dtitle"] = (
                f", rst {ntot if dic['restart']==0 else dic['restart']} out of {ntot}"
            )
        elif dic["summary"][0].has_key(name.upper()):
            for i, _ in enumerate(dic["names"]):
                dic["vsum"].append(dic["summary"][i][name.upper()].values)
                if dic["times"] == "dates":
                    dic["time"].append(dic["summary"][i].dates)
                else:
                    dic["time"].append(dic["summary"][i]["TIME"].values * dic["tskl"])
            return
        elif name.lower() in dic["mass"] + dic["smass"]:
            handle_mass_resdata(dic, name)
        else:
            print(f"Unknow -v variable ({name}).")
            sys.exit()
        dic[name + "a"] = np.ones(dic["mx"] * dic["my"]) * np.nan


def handle_mass_resdata(dic, name):
    """
    Mass using resdata.

    Args:
        dic (dict): Global dictionary\n
        name (str): Name of the variable for the mass spatial map

    Returns:
        dic (dict): Modified global dictionary

    """
    if name.lower() in dic["mass"]:
        if len(dic["names"]) == 1:
            dic[name] = handle_mass(dic, name, 0, dic["restart"])
        else:
            dic[name] = handle_mass(dic, name, 0, dic["restart"]) - handle_mass(
                dic, name, 1, dic["restart"]
            )
        ntot = len(dic["unrst"][0]["SGAS"])
        dic["dtitle"] = (
            f", rst {ntot if dic['restart']==0 else dic['restart']} out of {ntot},"
            + f" total sum={sum(dic[name]):.2E}"
        )
        dic[name] *= dic["skl"]
    else:
        for i, _ in enumerate(dic["names"]):
            dic["vsum"].append(
                dic["summary"][i][name[:-1].upper()].values * GAS_DEN_REF * dic["skl"]
            )
            if dic["times"] == "dates":
                dic["time"].append(dic["summary"][i].dates)
            else:
                dic["time"].append(dic["summary"][i]["TIME"].values * dic["tskl"])


def handle_mass(dic, name, i, nrst):
    """
    Compute the mass (intensive quantities).

    Args:
        dic (dict): Global dictionary\n
        name (str): Name of the variable for the mass spatial map\n
        i (int): Number of the geological model\n
        nrst (int): Number of restart step

    Returns:
        mass (array): Floats with the computed mass

    """
    if dic["use"] == "resdata":
        sgas = abs(np.array(dic["unrst"][i]["SGAS"][nrst - 1]))
        rhog = np.array(dic["unrst"][i]["GAS_DEN"][nrst - 1])
        rhow = np.array(dic["unrst"][i]["WAT_DEN"][nrst - 1])
        if dic["unrst"][i].has_kw("RSW"):
            rsw = np.array(dic["unrst"][i]["RSW"][nrst - 1])
        else:
            rsw = 0.0 * sgas
        if dic["unrst"][i].has_kw("RVW"):
            rvw = np.array(dic["unrst"][i]["RVW"][nrst - 1])
        else:
            rvw = 0.0 * sgas
    else:
        nrst = nrst - 1 if nrst > 0 else dic["unrst"][0].count("SGAS") - 1
        sgas = abs(np.array(dic["unrst"][i]["SGAS", nrst]))
        rhog = np.array(dic["unrst"][i]["GAS_DEN", nrst])
        rhow = np.array(dic["unrst"][i]["WAT_DEN", nrst])
        if dic["unrst"][i].count("RSW"):
            rsw = np.array(dic["unrst"][i]["RSW", nrst])
        else:
            rsw = 0.0 * sgas
        if dic["unrst"][i].count("RVW"):
            rvw = np.array(dic["unrst"][i]["RVW", nrst])
        else:
            rvw = 0.0 * sgas
    co2_g = sgas * rhog * dic["pv"]
    co2_d = rsw * rhow * (1.0 - sgas) * dic["pv"] * GAS_DEN_REF / WAT_DEN_REF
    h2o_l = (1 - sgas) * rhow * dic["pv"]
    h2o_v = rvw * rhog * sgas * dic["pv"] * WAT_DEN_REF / GAS_DEN_REF
    return type_of_mass(name, co2_g, co2_d, h2o_l, h2o_v)


def type_of_mass(name, co2_g, co2_d, h2o_l, h2o_v):
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
    return co2_g + co2_d


def get_kws_opm(dic):
    """
    Get the static properties from the INIT file using Opm

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["porv"] = np.array(dic["init"]["PORV"])
    dic["porva"] = np.ones(dic["mx"] * dic["my"]) * np.nan
    dic["pv"] = np.array([porv for porv in dic["porv"] if porv > 0])
    dic["actind"] = np.cumsum([1 if porv > 0 else 0 for porv in dic["porv"]]) - 1
    for name in dic["props"]:
        if dic["init"].count(name.upper()):
            dic[name] = np.array(dic["init"][name.upper()])
        elif dic["unrst"][0].count(name.upper()):
            nrst = (
                dic["restart"] - 1
                if dic["restart"] > 0
                else dic["unrst"][0].count(name.upper()) - 1
            )
            if len(dic["names"]) == 1:
                dic[name] = np.array(dic["unrst"][0][name.upper(), nrst])
            else:
                dic[name] = np.array(dic["unrst"][0][name.upper(), nrst]) - np.array(
                    dic["unrst"][1][name.upper(), nrst]
                )
            ntot = dic["unrst"][0].count(name.upper())
            dic["dtitle"] = (
                f", rst {ntot if dic['restart']==0 else dic['restart']} out of {ntot}"
            )
        elif name.upper() in dic["summary"][0].keys():
            for i, _ in enumerate(dic["names"]):
                dic["vsum"].append(dic["summary"][i][name.upper()])
                if dic["times"] == "dates":
                    smsp_dates = 86400 * dic["summary"][i]["TIME"]
                    smsp_dates = [
                        dic["summary"][i].start_date
                        + datetime.timedelta(seconds=seconds)
                        for seconds in smsp_dates
                    ]
                    dic["time"].append(smsp_dates)
                else:
                    dic["time"].append(dic["summary"][i]["TIME"] * dic["tskl"])
            return
        elif name.lower() in dic["mass"] + dic["smass"]:
            handle_mass_opm(dic, name)
        else:
            print(f"Unknow -v variable ({name}).")
            sys.exit()
        dic[name + "a"] = np.ones(dic["mx"] * dic["my"]) * np.nan


def handle_mass_opm(dic, name):
    """
    Mass using opm.

    Args:
        dic (dict): Global dictionary\n
        name (str): Name of the variable for the mass spatial map

    Returns:
        dic (dict): Modified global dictionary

    """
    if name.lower() in dic["mass"]:
        if len(dic["names"]) == 1:
            dic[name] = handle_mass(dic, name, 0, dic["restart"])
        else:
            dic[name] = handle_mass(dic, name, 0, dic["restart"]) - handle_mass(
                dic, name, 1, dic["restart"]
            )
        ntot = dic["unrst"][0].count("SGAS")
        dic["dtitle"] = (
            f", rst {ntot if dic['restart']==0 else dic['restart']} out of {ntot},"
            + f" total sum={sum(dic[name]):.2E}"
        )
        dic[name] *= dic["skl"]
    else:
        for i, _ in enumerate(dic["names"]):
            dic["vsum"].append(
                dic["summary"][i][name[:-1].upper()] * GAS_DEN_REF * dic["skl"]
            )
            if dic["times"] == "dates":
                smsp_dates = 86400 * dic["summary"][i]["TIME"]
                smsp_dates = [
                    dic["summary"][i].start_date + datetime.timedelta(seconds=seconds)
                    for seconds in smsp_dates
                ]
                dic["time"].append(smsp_dates)
            else:
                dic["time"].append(dic["summary"][i]["TIME"] * dic["tskl"])


def get_wells(dic):
    """
    Using the input deck (.DATA) to read the i,j well locations

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["wellsa"] = np.ones((dic["mx"]) * (dic["my"])) * np.nan
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
