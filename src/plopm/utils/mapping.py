# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy function for the grid and locations in the geological models.
"""

import numpy as np
from plopm.utils.readers import (
    get_xycoords_resdata,
    get_xycoords_opm,
    get_xzcoords_resdata,
    get_xzcoords_opm,
    get_yzcoords_resdata,
    get_yzcoords_opm,
)


def handle_slide_x(dic):
    """
    Processing the selected yz slide to obtain the grid properties

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["tslide"] = f", slide i={dic['slide'][0]+1}"
    dic["nslide"] = f"{dic['slide'][0]+1},*,*"
    for well in reversed(dic["wells"]):
        if well[0] != dic["slide"][0]:
            dic["wells"].remove(well)
    if dic["use"] == "resdata":
        get_yzcoords_resdata(dic)
    else:
        get_yzcoords_opm(dic)


def handle_slide_y(dic):
    """
    Processing the selected xz slide to obtain the grid properties

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["tslide"] = f", slide j={dic['slide'][1]+1}"
    dic["nslide"] = f"*,{dic['slide'][1]+1},*"
    for well in reversed(dic["wells"]):
        if well[1] != dic["slide"][1]:
            dic["wells"].remove(well)
    if dic["use"] == "resdata":
        get_xzcoords_resdata(dic)
    else:
        get_xzcoords_opm(dic)


def handle_slide_z(dic):
    """
    Processing the selected xy slide to obtain the grid properties

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["tslide"] = f", slide k={dic['slide'][2]+1}"
    dic["nslide"] = f"*,*,{dic['slide'][2]+1}"
    for well in reversed(dic["wells"]):
        if dic["slide"][2] not in range(well[2], well[3] + 1):
            dic["wells"].remove(well)
    if dic["use"] == "resdata":
        get_xycoords_resdata(dic)
    else:
        get_xycoords_opm(dic)


def rotate_grid(dic, n):
    """
    Rotate the grid if requiered.

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    grd = int(dic["rotate"][n])
    xc, yc = [], []
    length = dic["xc"][-1][-1] - dic["xc"][0][0]
    width = dic["yc"][0][-1] - dic["yc"][-1][0]
    x_dis = float(dic["translate"][n][0][1:])
    y_dis = float(dic["translate"][n][1][:-1])
    for rowx, rowy in zip(dic["xc"], dic["yc"]):
        xc.append([])
        yc.append([])
        for i, j in zip(rowx, rowy):
            xc[-1].append(
                1.5 * length
                + x_dis
                + (i - 1.5 * length) * np.cos(grd * np.pi / 180)
                - (j - 1.5 * width) * np.sin(grd * np.pi / 180)
            )
            yc[-1].append(
                1.5 * width
                + y_dis
                + (j - 1.5 * width) * np.cos(grd * np.pi / 180)
                + (i - 1.5 * length) * np.sin(grd * np.pi / 180)
            )
    dic["xc"] = xc
    dic["yc"] = yc


def map_xzcoords(dic, var, quan):
    """
    Map the properties from the simulations to the 2D slide

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for k in range(dic["nz"]):
        for i in range(dic["nx"]):
            ind = i + dic["slide"][1] * dic["nx"] + k * dic["nx"] * dic["ny"]
            if dic["porv"][ind] > 0:
                if var.lower() == "grid":
                    dic["grida"][2 * i + 2 * (dic["nz"] - k - 1) * dic["mx"]] = 1
                elif var.lower() == "wells":
                    dic["wellsa"][2 * i + 2 * (dic["nz"] - k - 1) * dic["mx"]] = len(
                        dic["wells"]
                    )
                elif var.lower() == "index_i":
                    dic["index_ia"][2 * i + 2 * (dic["nz"] - k - 1) * dic["mx"]] = i
                elif var.lower() == "index_j":
                    dic["index_ja"][2 * i + 2 * (dic["nz"] - k - 1) * dic["mx"]] = dic[
                        "slide"
                    ][1]
                elif var.lower() == "index_k":
                    dic["index_ka"][2 * i + 2 * (dic["nz"] - k - 1) * dic["mx"]] = k
                else:
                    dic[var + "a"][2 * i + 2 * (dic["nz"] - k - 1) * dic["mx"]] = quan[
                        dic["actind"][ind]
                    ]
    for i, well in enumerate(dic["wells"]):
        for k in range(well[2], well[3] + 1):
            dic["wellsa"][2 * well[0] + 2 * (dic["nz"] - k - 1) * dic["mx"]] = i


def map_yzcoords(dic, var, quan):
    """
    Map the properties from the simulations to the 2D slide

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for k in range(dic["nz"]):
        for j in range(dic["ny"]):
            ind = dic["slide"][0] + j * dic["nx"] + k * dic["nx"] * dic["ny"]
            if dic["porv"][ind] > 0:
                if var.lower() == "grid":
                    dic["grida"][2 * j + 2 * (dic["nz"] - k - 1) * dic["mx"]] = 1
                elif var.lower() == "wells":
                    dic["wellsa"][2 * j + 2 * (dic["nz"] - k - 1) * dic["mx"]] = len(
                        dic["wells"]
                    )
                elif var.lower() == "index_i":
                    dic[var + "a"][2 * j + 2 * (dic["nz"] - k - 1) * dic["mx"]] = dic[
                        "slide"
                    ][0]
                elif var.lower() == "index_j":
                    dic[var + "a"][2 * j + 2 * (dic["nz"] - k - 1) * dic["mx"]] = j
                elif var.lower() == "index_k":
                    dic[var + "a"][2 * j + 2 * (dic["nz"] - k - 1) * dic["mx"]] = k
                else:
                    dic[var + "a"][2 * j + 2 * (dic["nz"] - k - 1) * dic["mx"]] = quan[
                        dic["actind"][ind]
                    ]
    for i, well in enumerate(dic["wells"]):
        for k in range(well[2], well[3] + 1):
            dic["wellsa"][2 * well[1] + 2 * (dic["nz"] - k - 1) * dic["mx"]] = i


def map_xycoords(dic, var, quan):
    """
    Map the properties from the simulations to the 2D slide

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for j in range(dic["ny"]):
        for i in range(dic["nx"]):
            ind = i + j * dic["nx"] + dic["slide"][2] * dic["nx"] * dic["ny"]
            if dic["porv"][ind] > 0:
                if var.lower() == "grid":
                    dic["grida"][2 * i + 2 * j * dic["mx"]] = 1
                elif var.lower() == "wells":
                    dic["wellsa"][2 * i + 2 * j * dic["mx"]] = len(dic["wells"])
                elif var.lower() == "index_i":
                    dic[var + "a"][2 * i + 2 * j * dic["mx"]] = i
                elif var.lower() == "index_j":
                    dic[var + "a"][2 * i + 2 * j * dic["mx"]] = j
                elif var.lower() == "index_k":
                    dic[var + "a"][2 * i + 2 * j * dic["mx"]] = dic["slide"][2]
                else:
                    dic[var + "a"][2 * i + 2 * j * dic["mx"]] = quan[dic["actind"][ind]]
    for i, well in enumerate(dic["wells"]):
        dic["wellsa"][2 * well[0] + 2 * well[1] * dic["mx"]] = i
