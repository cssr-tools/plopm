# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy function for the grid and locations in the geological models.
"""


def map_yzcoords(dic):
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
                for name in dic["props"]:
                    dic[name + "a"][2 * j + 2 * (dic["nz"] - k - 1) * dic["mx"]] = dic[
                        name
                    ][dic["actind"][ind]]
                if "porv" in dic["props"]:
                    dic["porva"][2 * j + 2 * (dic["nz"] - k - 1) * dic["mx"]] = dic[
                        "porv"
                    ][ind]
                if len(dic["wells"]) > 0:
                    dic["wellsa"][2 * j + 2 * (dic["nz"] - k - 1) * dic["mx"]] = len(
                        dic["wells"]
                    )
                if dic["grid"] == 1:
                    dic["grida"][2 * j + 2 * (dic["nz"] - k - 1) * dic["mx"]] = 1
    for i, well in enumerate(dic["wells"]):
        for k in range(well[2], well[3] + 1):
            dic["wellsa"][2 * well[1] + 2 * (dic["nz"] - k - 1) * dic["mx"]] = i


def map_xzcoords(dic):
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
                for name in dic["props"]:
                    dic[name + "a"][2 * i + 2 * (dic["nz"] - k - 1) * dic["mx"]] = dic[
                        name
                    ][dic["actind"][ind]]
                if "porv" in dic["props"]:
                    dic["porva"][2 * i + 2 * (dic["nz"] - k - 1) * dic["mx"]] = dic[
                        "porv"
                    ][ind]
                if len(dic["wells"]) > 0:
                    dic["wellsa"][2 * i + 2 * (dic["nz"] - k - 1) * dic["mx"]] = len(
                        dic["wells"]
                    )
                if dic["grid"] == 1:
                    dic["grida"][2 * i + 2 * (dic["nz"] - k - 1) * dic["mx"]] = 1
    for i, well in enumerate(dic["wells"]):
        for k in range(well[2], well[3] + 1):
            dic["wellsa"][2 * well[0] + 2 * (dic["nz"] - k - 1) * dic["mx"]] = i


def map_xycoords(dic):
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
                for name in dic["props"]:
                    dic[name + "a"][2 * i + 2 * j * dic["mx"]] = dic[name][
                        dic["actind"][ind]
                    ]
                if "porv" in dic["props"]:
                    dic["porva"][2 * i + 2 * j * dic["mx"]] = dic["porv"][ind]
                if len(dic["wells"]) > 0:
                    dic["wellsa"][2 * i + 2 * j * dic["mx"]] = len(dic["wells"])
                if dic["grid"] == 1:
                    dic["grida"][2 * i + 2 * j * dic["mx"]] = 1
    for i, well in enumerate(dic["wells"]):
        dic["wellsa"][2 * well[0] + 2 * well[1] * dic["mx"]] = i
