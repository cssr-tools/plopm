# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions to read the OPM Flow simulator type output files.
"""

import csv
import numpy as np


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
    else:
        dic["porv"] = np.array(dic["init"].iget_kw("PORV")[0])
    dic["porva"] = np.ones(dic["mx"] * dic["my"]) * np.nan
    dic["actind"] = np.cumsum([1 if porv > 0 else 0 for porv in dic["porv"]]) - 1


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
