# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1702,W0123,W1401,R0915

"""Postprocessing visualization tool for OPM Flow geological models"""

import shutil
import argparse
from plopm.utils.initialization import (
    ini_cfg,
    ini_properties,
    is_summary,
    ini_summary,
)
from plopm.utils.write_vtk import make_vtks
from plopm.utils.write_oned import make_plots
from plopm.utils.write_twod import make_maps


def main(argv=None) -> None:
    """Main function for the plopm executable"""
    cmdargs = load_parser(argv)
    cfg = ini_cfg(cmdargs)
    print("\nExecuting plopm, please wait.")
    if cfg.vtk:
        make_vtks(
            cmdargs["path"],
            cfg.names,
            cfg.output,
            cfg.save,
            cfg.restart,
            cfg.vrs,
            cfg.vtkformat,
            cfg.vtknames,
            cfg.gif,
            cfg.vtk,
            cfg.filter,
            cfg.adjust,
            cfg.mass,
            cfg.mass + cfg.xmass,
            cfg.caprock,
            cfg.stress,
            cfg.filter,
        )
    else:
        if shutil.which("latex") is None:
            print(
                "\nLaTeX is recommended for the figures to show the "
                "nice fonts and given formats. You can install it by "
                "following the instructions in the plopm's "
                "documentation."
            )
        if is_summary(cfg):
            ini_summary(cfg)
            make_plots(cfg)
        else:
            ini_properties(cfg)
            make_maps(cfg)
    print(
        "\nThe execution of plopm succeeded. "
        + f"The generated files have been written to {cfg.output}\n"
    )


def load_parser(argv: list[str] | None) -> dict:
    """CLI arguments"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="plopm: Simplified and flexible Python tool for quick visualization of "
        "OPM Flow geological models. See online documentation for examples and "
        "detailed description of command flags: "
        "https://cssr-tools.github.io/plopm/introduction.html#overview",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str.strip,
        default="SPE11B",
        help="Provide input file(s) or base name(s), separated by spaces "
        'e.g. "SPE11B /home/user/SPE11B_TUNED"',
    )
    parser.add_argument(
        "-v",
        "--variable",
        type=str.strip,
        default="poro,permx,permz,porv,fipnum,satnum",
        help="Specify variable(s) to plot, including standard variables, special "
        "variables (grid, wells, faults), and expressions "
        'e.g. "pressure - 0pressure"',
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str.strip,
        default=".",
        help="Set output directory",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str.strip,
        choices=["png", "gif", "csv", "vtk"],
        default="png",
        help="Select output format",
    )
    parser.add_argument(
        "-s",
        "--slide",
        type=str.strip,
        default=",1,",
        help="Select slice or location using i,j,k format "
        'e.g. "10,," (xz plane), ",,5:10" (range), "2,4,9" (cell over time)',
    )
    parser.add_argument(
        "-r",
        "--restart",
        type=str.strip,
        default="-1",
        help="Select restart step(s): single, list, or range "
        'e.g. "-1", "0,3,10", "1:5", "5:505:250"',
    )
    parser.add_argument(
        "-c",
        "--colors",
        type=str.strip,
        default="",
        help='Set colormap or colors e.g. "jet" or "b,r"',
    )
    parser.add_argument(
        "-b",
        "--bounds",
        type=str.strip,
        default="",
        help='Set color limits e.g. "[-0.1,11]"',
    )
    parser.add_argument(
        "-d",
        "--dimensions",
        type=str.strip,
        default="7,5",
        help='Set figure size in inches e.g. "7,5"',
    )
    parser.add_argument(
        "-f",
        "--size",
        type=str.strip,
        default="12",
        help="Set font size",
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str.strip,
        default="0",
        help="Set figure title, separate subplots using double spaces",
    )
    parser.add_argument(
        "-suptitle",
        "--suptitle",
        type=str.strip,
        default="",
        help="Set title for subfigures or use 0 to remove",
    )
    parser.add_argument(
        "-clabel",
        "--clabel",
        type=str.strip,
        default="",
        help="Set colorbar label",
    )
    parser.add_argument(
        "-xlabel",
        "--xlabel",
        type=str.strip,
        default="",
        help="Set x-axis label",
    )
    parser.add_argument(
        "-ylabel",
        "--ylabel",
        type=str.strip,
        default="",
        help="Set y-axis label",
    )
    parser.add_argument(
        "-facecolor",
        "--facecolor",
        type=str.strip,
        default="w",
        help="Set background color outside plot",
    )
    parser.add_argument(
        "-dpi",
        "--dpi",
        type=str.strip,
        default="500",
        help="Set figure resolution in DPI",
    )
    parser.add_argument(
        "-x",
        "--xlim",
        type=str.strip,
        default="",
        help='Set x-axis limits e.g. "[-100,200]"',
    )
    parser.add_argument(
        "-y",
        "--ylim",
        type=str.strip,
        default="",
        help='Set y-axis limits e.g. "[-10,300]"',
    )
    parser.add_argument(
        "-z",
        "--scale",
        type=str.strip,
        choices=["0", "1"],
        default="1",
        help="Enable equal axis scaling",
    )
    parser.add_argument(
        "-xlog",
        "--xlog",
        type=str.strip,
        default="0",
        help="Enable logarithmic x-axis",
    )
    parser.add_argument(
        "-ylog",
        "--ylog",
        type=str.strip,
        default="0",
        help="Enable logarithmic y-axis",
    )
    parser.add_argument(
        "-log",
        "--log",
        type=str.strip,
        default="0",
        help="Enable logarithmic color scale",
    )
    parser.add_argument(
        "-clogthks",
        "--clogthks",
        type=str.strip,
        default="",
        help='Set custom tick values for logarithmic color scale e.g. "[1,2,3]"',
    )
    parser.add_argument(
        "-a",
        "--adjust",
        type=str.strip,
        default="1",
        help="Apply scaling factor to variable values e.g. 1e-9 for converting mass to Mt",
    )
    parser.add_argument(
        "-xformat",
        "--xformat",
        type=str.strip,
        default="",
        help='Set x-axis number format e.g. ".2e"',
    )
    parser.add_argument(
        "-yformat",
        "--yformat",
        type=str.strip,
        default="",
        help='Set y-axis number format e.g. ".1f"',
    )
    parser.add_argument(
        "-cformat",
        "--cformat",
        type=str.strip,
        default="",
        help='Set colorbar number format e.g. ".2f"',
    )
    parser.add_argument(
        "-xlnum",
        "--xlnum",
        type=str.strip,
        default="5",
        help="Set number of x-axis ticks",
    )
    parser.add_argument(
        "-ylnum",
        "--ylnum",
        type=str.strip,
        default="5",
        help="Set number of y-axis ticks",
    )
    parser.add_argument(
        "-cnum",
        "--cnum",
        type=str.strip,
        default="",
        help="Set number of colorbar ticks",
    )
    parser.add_argument(
        "-cticks",
        "--cticks",
        type=str.strip,
        default="",
        help='Set custom colorbar tick labels e.g. "[A,B,C]"',
    )
    parser.add_argument(
        "-xunits",
        "--xunits",
        type=str.strip,
        choices=["mm", "cm", "m", "km"],
        default="m",
        help="Set x-axis units",
    )
    parser.add_argument(
        "-yunits",
        "--yunits",
        type=str.strip,
        choices=["mm", "cm", "m", "km"],
        default="m",
        help="Set y-axis units",
    )
    parser.add_argument(
        "-subfigs",
        "--subfigs",
        type=str.strip,
        default="",
        help='Arrange subplots e.g. "2,2" for grid layout',
    )
    parser.add_argument(
        "-loc",
        "--loc",
        type=str.strip,
        default="best",
        help="Set legend location or use empty to remove",
    )
    parser.add_argument(
        "-labels",
        "--labels",
        type=str.strip,
        default="",
        help="Set legend labels separated by double spaces",
    )
    parser.add_argument(
        "-lw",
        "--lw",
        type=str.strip,
        default="",
        help="Set line widths separated by commas",
    )
    parser.add_argument(
        "-e",
        "--linestyle",
        type=str.strip,
        default="",
        help='Set line styles e.g. "solid,dotted"',
    )
    parser.add_argument(
        "-axgrid",
        "--axgrid",
        type=str.strip,
        choices=["0", "1"],
        default="1",
        help="Toggle axis grid display",
    )
    parser.add_argument(
        "-remove",
        "--remove",
        type=str.strip,
        default="0,0,0,0",
        help="Toggle left axis, bottom axis, colorbar, title using 0 or 1",
    )
    parser.add_argument(
        "-how",
        "--how",
        type=str.strip,
        default="",
        help="Select aggregation method such as mean, pvmean, sum, harmonic, arithmetic",
    )
    parser.add_argument(
        "-global",
        "--global",
        type=str.strip,
        choices=["0", "1"],
        default="0",
        help="Use local slice or global model range for color scaling",
    )
    parser.add_argument(
        "-filter",
        "--filter",
        type=str.strip,
        default="",
        help='Filter cells using conditions, and use "," for different input files e.g. '
        '"sgas >= 0.2 & fluxnum == 2, satnum != 5"',
    )
    parser.add_argument(
        "-vmin",
        "--vmin",
        type=str.strip,
        default="",
        help="Set minimum threshold for values",
    )
    parser.add_argument(
        "-vmax",
        "--vmax",
        type=str.strip,
        default="",
        help="Set maximum threshold for values",
    )
    parser.add_argument(
        "-mask",
        "--mask",
        type=str.strip,
        default="",
        help="Set background variable for map masking",
    )
    parser.add_argument(
        "-maskthr",
        "--maskthr",
        type=str.strip,
        default="1e-3",
        help="Set masking threshold",
    )
    parser.add_argument(
        "-ensemble",
        "--ensemble",
        type=str.strip,
        choices=["0", "1", "2", "3"],
        default="0",
        help="Configure ensemble statistics plotting mode",
    )
    parser.add_argument(
        "-bandprop",
        "--bandprop",
        type=str.strip,
        default="",
        help="Set fill_between color and alpha values",
    )
    parser.add_argument(
        "-histogram",
        "--histogram",
        type=str.strip,
        default="",
        help='Plot histogram using "bins,distribution" e.g. "20,norm"',
    )
    parser.add_argument(
        "-distance",
        "--distance",
        type=str.strip,
        choices=["min,sensor", "max,sensor", "min,border", "max,border", ""],
        default="",
        help="Compute distance relative to sensor or boundary",
    )
    parser.add_argument(
        "-stress",
        "--stress",
        type=str.strip,
        default="0.134",
        help="Set stress coefficient used to compute pressure limits for caprock "
        "integrity variables (limipres, overpres, objepres)",
    )
    parser.add_argument(
        "-rotate",
        "--rotate",
        type=str.strip,
        default="0",
        help="Rotate grid by angle in degrees",
    )
    parser.add_argument(
        "-translate",
        "--translate",
        type=str.strip,
        default="[0,0]",
        help="Translate grid in x and y directions",
    )
    parser.add_argument(
        "-csv",
        "--csv",
        type=str.strip,
        default="",
        help="Define CSV column indices starting at 1",
    )
    parser.add_argument(
        "-tunits",
        "--tunits",
        type=str.strip,
        choices=["s", "m", "h", "d", "w", "y", "dates", "empty"],
        default="d",
        help="Set time units for plots",
    )
    parser.add_argument(
        "-save",
        "--save",
        type=str.strip,
        default="",
        help="Set output filename",
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str.strip,
        default="flow",
        help="Set path to flow executable",
    )
    parser.add_argument(
        "-vtkformat",
        "--vtkformat",
        type=str.strip,
        default="Float64",
        help="Set VTK variable formats separated by commas",
    )
    parser.add_argument(
        "-vtknames",
        "--vtknames",
        type=str.strip,
        default="",
        help="Set custom names for VTK variables",
    )
    parser.add_argument(
        "-diff",
        "--diff",
        type=str.strip,
        default="",
        help="Provide input file for difference computation",
    )
    parser.add_argument(
        "-ncolor",
        "--ncolor",
        type=str.strip,
        default="w",
        help="Set color for inactive cells",
    )
    parser.add_argument(
        "-grid",
        "--grid",
        type=str.strip,
        default="",
        help="Set pcolormesh edge color and line width",
    )
    parser.add_argument(
        "-cbsfax",
        "--cbsfax",
        type=str.strip,
        default="0.40,0.01,0.2,0.02",
        help="Set position of fig.add_axes([left, bottom, width, height])",
    )
    parser.add_argument(
        "-delax",
        "--delax",
        type=str.strip,
        choices=["0", "1"],
        default="0",
        help="Remove duplicated axis labels in subplots",
    )
    parser.add_argument(
        "-printv",
        "--printv",
        type=str.strip,
        choices=["0", "1"],
        default="0",
        help="Print available variables",
    )
    parser.add_argument(
        "-dual",
        "--dual",
        type=str.strip,
        default="0",
        help="Enable dual-grid processing",
    )
    parser.add_argument(
        "-interval",
        "--interval",
        type=str.strip,
        default="1000",
        help="Set GIF frame interval in milliseconds",
    )
    parser.add_argument(
        "-loop",
        "--loop",
        type=str.strip,
        default="0",
        help="Enable infinite GIF looping",
    )
    return vars(parser.parse_known_args(argv)[0])
