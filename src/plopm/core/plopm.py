# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1702, W0123, W1401

"""
Script to plot 2D maps of OPM Flow geological models.
"""

import argparse
import numpy as np
from plopm.utils.initialization import ini_dic, ini_properties, ini_readers
from plopm.utils.readers import (
    get_kws_resdata,
    get_kws_opm,
    get_wells,
    get_xycoords_resdata,
    get_xycoords_opm,
    get_xzcoords_resdata,
    get_xzcoords_opm,
    get_yzcoords_resdata,
    get_yzcoords_opm,
)
from plopm.utils.mapping import map_xycoords, map_xzcoords, map_yzcoords
from plopm.utils.vtk import make_vtks
from plopm.utils.write import make_summary, make_2dmaps


def plopm():
    """Main function for the plopm executable"""
    cmdargs = load_parser()
    dic = ini_dic(cmdargs)
    if dic["mode"] == "vtk":
        make_vtks(dic)
        return
    ini_properties(dic)
    ini_readers(dic)
    if dic["use"] == "resdata":
        get_kws_resdata(dic)
    else:
        get_kws_opm(dic)
    if len(dic["vsum"]) > 0:
        make_summary(dic)
        return
    if dic["well"] == 1:
        get_wells(dic)
    if dic["grid"] == 1:
        dic["grida"] = np.ones((dic["mx"]) * (dic["my"])) * np.nan
    if dic["slide"][0] > -1:
        handle_slide_x(dic)
    elif dic["slide"][1] > -1:
        handle_slide_y(dic)
    else:
        handle_slide_z(dic)
    make_2dmaps(dic)


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
    map_yzcoords(dic)


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
    map_xzcoords(dic)


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
    map_xycoords(dic)


def load_parser():
    """Argument options"""
    parser = argparse.ArgumentParser(
        description="plopm: Simplified and flexible Python tool for quick "
        "visualization of OPM Flow geological models.",
    )
    parser.add_argument(
        "-i",
        "--input",
        default="SPE11B",
        help="The base name of the input files; if more than one is given, separate "
        "them by ',' (e.g, 'SPE11B,SPE11B_TUNED') ('SPE11B' by default).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=".",
        help="The base name of the output folder ('.' by default).",
    )
    parser.add_argument(
        "-s",
        "--slide",
        default=",1,",
        help="The slide for the 2d maps of the static variables, e.g,"
        " '10,,' to plot the xz plane on all cells with i=10 (',1,' "
        " by default, i.e., the xz surface at j=1.)",
    )
    parser.add_argument(
        "-z",
        "--scale",
        default="yes",
        help="Scale the 2d maps ('yes' by default)",
    )
    parser.add_argument(
        "-f",
        "--size",
        default=14,
        help="The font size ('14' by default)",
    )
    parser.add_argument(
        "-x",
        "--xlim",
        default="",
        help="Set the lower and upper bounds in the 2D map along x ('' by default).",
    )
    parser.add_argument(
        "-y",
        "--ylim",
        default="",
        help="Set the lower and upper bounds in the 2D map along y ('' by default).",
    )
    parser.add_argument(
        "-u",
        "--use",
        default="resdata",
        help="Use resdata or opm Python libraries ('resdata' by default).",
    )
    parser.add_argument(
        "-v",
        "--variable",
        default="",
        help="Specify the name of the static vairable to plot (e.g.,'depth') ('' by "
        "default, i.e., plotting: porv, permx, permz, poro, fipnum, and satnum).",
    )
    parser.add_argument(
        "-c",
        "--colormap",
        default="",
        help="Specify the colormap (e.g., 'jet') or color(s) for the summary "
        "(e.g., 'b,r')  ('' by default, i.e., set by plopm).",
    )
    parser.add_argument(
        "-e",
        "--linsty",
        default="",
        help="Specify the linestyles separated by ';' (e.g., 'solid;:') ('' by default, "
        "i.e., set by plopm).",
    )
    parser.add_argument(
        "-n",
        "--numbers",
        default="",
        help="Specify the format for the numbers in the colormap (e.g., "
        "\"lambda x, _: f'{x:.0f}'\") ('' by default, i.e., set by plopm).",
    )
    parser.add_argument(
        "-b",
        "--bounds",
        default="",
        help="Specify the upper and lower bounds for the colormap (e.g., "
        " '[-0.1,11]') ('' by default, i.e., set by matplotlib).",
    )
    parser.add_argument(
        "-d",
        "--dimensions",
        default="8,16",
        help="Specify the dimensions  of the Figure (e.g., "
        " '5,5') ('8,16' by default).",
    )
    parser.add_argument(
        "-l",
        "--legend",
        default="",
        help="Specify the units (e.g., \"[m\\$^2\\$]\") ('' by "
        "default, i.e., set by plopm).",
    )
    parser.add_argument(
        "-t",
        "--title",
        default="",
        help="Specify the figure title (e.g., 'Final saturation map') ('' by "
        "default, i.e., set by plopm).",
    )
    parser.add_argument(
        "-r",
        "--restart",
        default="-1",
        help="Restart number to plot the dynamic variable, where 1 corresponds to "
        "the initial one ('-1' by default, i.e., the last restart file).",
    )
    parser.add_argument(
        "-w",
        "--wells",
        default=0,
        help="Plot the positions of the wells or sources ('0' by default).",
    )
    parser.add_argument(
        "-g",
        "--grid",
        default=0,
        help="Plot information about the number of cells in the x, y, and z "
        " directions and number of active grid cells ('0' by default).",
    )
    parser.add_argument(
        "-p",
        "--path",
        default="flow",
        help="Path to flow (e.g., \\home\\build\\bin\\flow')."
        " This is used to generate the grid for the vtk files ('flow' by "
        "default, make sure to write inside ' ').",
    )
    parser.add_argument(
        "-m",
        "--mode",
        default="png",
        help="Generate 'png' or 'vtk' files ('png' by default).",
    )
    return vars(parser.parse_known_args()[0])


def main():
    """Main function"""
    plopm()
