# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0302,R1702,W0123,W1401,R0912,R0914,R0915

"""Postprocessing visualization tool for OPM Flow geological models"""

import argparse
import re
import shlex
import shutil
import subprocess

from plopm.utils.initialization import (
    ini_cfg,
    ini_properties,
    ini_summary,
    is_summary,
)
from plopm.utils.write_oned import make_plots
from plopm.utils.write_twod import make_maps
from plopm.utils.write_vtk import make_vtks


def main(argv=None) -> None:
    """Main function for the plopm executable"""
    cmdargs = load_parser(argv)
    check_cmdargs(cmdargs)
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
        help="Select aggregation method for the 2D and 1D proyections (min, max, sum, "
        "mean, pvmean, harmonic, arithmetic, first, last)",
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
        choices=["s", "m", "h", "d", "w", "y", "dates", "empty", "tstep"],
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
        help="Set position of fig.add_axes([left, bottom, width, height])'; "
        "set to 'empty' to remove it",
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
    parser.add_argument(
        "-step",
        "--step",
        type=str.strip,
        choices=["0", "1"],
        default="0",
        help="Use ax.step instead of ax.plot",
    )
    return vars(parser.parse_known_args(argv)[0])


def check_cmdargs(cmdargs: dict[str, str]) -> None:
    """Validate command-line arguments and incompatible operations.

    Parameters
    ----------
    cmdargs
        Parsed arguments returned by :func:`load_parser`.

    Raises
    ------
    SystemExit
        If an argument is invalid or an incompatible combination is requested.
    """

    def fail(message: str) -> None:
        print(message)
        raise SystemExit(1)

    def parse_number(option: str, value: str) -> float:
        try:
            number = float(value)
        except ValueError:
            fail(f"Invalid value '{option} {value}', expected a number.")
        return number

    def parse_number_list(
        option: str,
        value: str,
        expected_length: int | None = None,
    ) -> list:
        entries = value.split(",")
        if expected_length is not None and len(entries) != expected_length:
            fail(
                f"Invalid value '{option} {value}', expected {expected_length} "
                "numbers separated by commas."
            )
        try:
            numbers = [float(entry) for entry in entries]
        except ValueError:
            fail(
                f"Invalid value '{option} {value}', expected numbers separated "
                "by commas."
            )
        return numbers

    mode = cmdargs["mode"]
    vtk_mode = mode == "vtk"
    gif_mode = mode == "gif"
    number = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
    positive_integer = r"[1-9]\d*"
    non_negative_integer = r"\d+"

    if not cmdargs["input"]:
        fail("Invalid value for '-i', the input cannot be empty.")
    if not cmdargs["output"]:
        fail("Invalid value for '-o', the output folder cannot be empty.")
    if not cmdargs["variable"]:
        fail("Invalid value for '-v', the variable cannot be empty.")

    positive_number_options = [
        ("-f", "size"),
        ("-dpi", "dpi"),
        ("-xlnum", "xlnum"),
        ("-ylnum", "ylnum"),
        ("-maskthr", "maskthr"),
        ("-interval", "interval"),
    ]
    for option, name in positive_number_options:
        value = parse_number(option, cmdargs[name])
        if value <= 0:
            fail(
                f"Invalid value '{option} {cmdargs[name]}', expected a positive "
                "number."
            )

    number_options = [
        ("-stress", "stress"),
        ("-rotate", "rotate"),
    ]
    for option, name in number_options:
        parse_number(option, cmdargs[name])
    parse_number_list("-a", cmdargs["adjust"])

    optional_number_options = [
        ("-vmin", "vmin"),
        ("-vmax", "vmax"),
    ]
    for option, name in optional_number_options:
        if cmdargs[name]:
            parse_number(option, cmdargs[name])

    if (
        cmdargs["vmin"]
        and cmdargs["vmax"]
        and float(cmdargs["vmin"]) > float(cmdargs["vmax"])
    ):
        fail(
            f"Invalid values '-vmin {cmdargs['vmin']}' and "
            f"'-vmax {cmdargs['vmax']}', the minimum threshold must not "
            "be greater than the maximum threshold."
        )

    colorbar_tick_numbers = cmdargs["cnum"]
    if colorbar_tick_numbers:
        cnum_entries = colorbar_tick_numbers.split(",")
        if any(not re.fullmatch(positive_integer, entry) for entry in cnum_entries):
            fail(
                f"Invalid value '-cnum {colorbar_tick_numbers}', expected "
                "positive integers separated by commas."
            )

    boolean_options = [
        ("-xlog", "xlog"),
        ("-ylog", "ylog"),
        ("-log", "log"),
        ("-dual", "dual"),
        ("-loop", "loop"),
    ]
    for option, name in boolean_options:
        values = cmdargs[name].split(",")
        if any(value not in ["0", "1"] for value in values):
            fail(
                f"Invalid value '{option} {cmdargs[name]}', expected values "
                "containing only 0 or 1, separated by commas."
            )

    dimensions = parse_number_list(
        "-d",
        cmdargs["dimensions"],
        2,
    )
    if any(value <= 0 for value in dimensions):
        fail(
            f"Invalid value '-d {cmdargs['dimensions']}', figure dimensions "
            "must be positive."
        )

    translation = cmdargs["translate"]
    if not re.fullmatch(
        rf"\[\s*{number}\s*,\s*{number}\s*\]",
        translation,
    ):
        fail(
            f"Invalid value '-translate {translation}', expected two numbers "
            "enclosed by brackets, e.g., '-translate [10,-5]'."
        )

    interval_pattern = re.compile(rf"\[\s*({number})\s*,\s*({number})\s*\]")
    for option, name in [
        ("-b", "bounds"),
        ("-x", "xlim"),
        ("-y", "ylim"),
    ]:
        valu = cmdargs[name]
        if not valu:
            continue
        for interval_value in valu.split():
            if not interval_pattern.fullmatch(interval_value):
                fail(
                    f"Invalid value '{option} {interval_value}', expected two "
                    "numeric bounds enclosed by brackets, e.g., '[0,10]'."
                )

    aggregation_methods = cmdargs["how"]
    if aggregation_methods:
        valid_aggregation_methods = [
            "min",
            "max",
            "sum",
            "mean",
            "pvmean",
            "harmonic",
            "arithmetic",
            "first",
            "last",
        ]
        method_entries = aggregation_methods.split(",")
        if any(method not in valid_aggregation_methods for method in method_entries):
            fail(
                f"Invalid value '-how {aggregation_methods}', valid methods are "
                f"{', '.join(valid_aggregation_methods)}."
            )

    slide = cmdargs["slide"]
    slides = slide.split()
    slide_entry_pattern = re.compile(
        rf"(?:{positive_integer}|" rf"{positive_integer}:{positive_integer}|:)?"
    )
    if not slides:
        fail("Invalid value for '-s', the slide selection cannot be empty.")

    slide_entries = []
    for selection in slides:
        entries = selection.split(",")
        if len(entries) != 3 or any(
            not slide_entry_pattern.fullmatch(entry) for entry in entries
        ):
            fail(
                f"Invalid value '-s {selection}', expected three i,j,k entries "
                "separated by commas, using positive indices, ':', or ranges."
            )
        if all(not entry for entry in entries):
            fail(
                f"Invalid value '-s {selection}', at least one slide entry must "
                "be provided."
            )
        colon_entries = 0
        for entry in entries:
            if ":" not in entry:
                continue
            colon_entries += 1
            if entry != ":":
                start, end = (int(index) for index in entry.split(":"))
                if start > end:
                    fail(
                        f"Invalid range '{entry}' in '-s {selection}', the end "
                        "must not be smaller than the start."
                    )
        if colon_entries > 1:
            fail(
                f"Invalid value '-s {selection}', only one slide direction can "
                "contain ':' or an index range."
            )
        slide_entries.append(entries)

    restart = cmdargs["restart"]
    restart_pattern = re.compile(
        rf"(?:-1|"
        rf"{non_negative_integer}(?:,{non_negative_integer})*|"
        rf"{non_negative_integer}:{non_negative_integer}"
        rf"(?::{positive_integer})?)"
    )
    if not restart_pattern.fullmatch(restart):
        fail(
            f"Invalid value '-r {restart}', expected '-1', non-negative "
            "restart indices separated by commas, or 'start:end[:step]'."
        )

    if ":" in restart:
        restart_range = [int(value) for value in restart.split(":")]
        if restart_range[0] > restart_range[1]:
            fail(
                f"Invalid range '-r {restart}', the end must not be smaller "
                "than the start."
            )

    list_options = [
        ("-c", "colors"),
        ("-e", "linestyle"),
    ]
    for option, name in list_options:
        valu = cmdargs[name]
        if valu and any(not entry for entry in valu.split(",")):
            fail(f"Invalid value '{option} {valu}', entries cannot be empty.")

    line_widths = cmdargs["lw"]
    if line_widths:
        width_values = parse_number_list("-lw", line_widths)
        if any(width <= 0 for width in width_values):
            fail(f"Invalid value '-lw {line_widths}', line widths must be " "positive.")

    remove = cmdargs["remove"]
    remove_entries = remove.split(",")
    if len(remove_entries) != 4 or any(
        entry not in ["0", "1"] for entry in remove_entries
    ):
        fail(
            f"Invalid value '-remove {remove}', expected four values "
            "containing only 0 or 1."
        )

    subfigs = cmdargs["subfigs"]
    if subfigs:
        subfig_entries = subfigs.split(",")
        if len(subfig_entries) != 2 or any(
            not re.fullmatch(positive_integer, entry) for entry in subfig_entries
        ):
            fail(
                f"Invalid value '-subfigs {subfigs}', expected two positive "
                "integers separated by a comma, e.g., '-subfigs 2,2'."
            )

    colorbar_axis = cmdargs["cbsfax"]
    if colorbar_axis != "empty":
        colorbar_axis_values = parse_number_list(
            "-cbsfax",
            colorbar_axis,
            4,
        )
        if colorbar_axis_values[0] < 0 or colorbar_axis_values[1] < 0:
            fail(
                f"Invalid value '-cbsfax {colorbar_axis}', the left and bottom "
                "positions cannot be negative."
            )
        if colorbar_axis_values[2] <= 0 or colorbar_axis_values[3] <= 0:
            fail(
                f"Invalid value '-cbsfax {colorbar_axis}', width and height "
                "must be positive."
            )

    grid = cmdargs["grid"]
    if grid:
        grid_entries = grid.split(",")
        if len(grid_entries) != 2 or not grid_entries[0] or not grid_entries[1]:
            fail(
                f"Invalid value '-grid {grid}', expected a color and line "
                "width separated by a comma."
            )
        if parse_number("-grid", grid_entries[1]) < 0:
            fail(f"Invalid value '-grid {grid}', the line width cannot be " "negative.")

    csv_columns = cmdargs["csv"]
    if csv_columns:
        csv_specifications = csv_columns.split(";")
        for specification in csv_specifications:
            if not specification:
                continue
            column_entries = specification.split(",")
            if len(column_entries) not in [2, 3] or any(
                not re.fullmatch(positive_integer, entry) for entry in column_entries
            ):
                fail(
                    f"Invalid value '-csv {csv_columns}', each non-empty "
                    "specification must contain two column indices for a time "
                    "series or three column indices for a spatial map."
                )
            if len(set(column_entries)) != len(column_entries):
                fail(
                    f"Invalid value '-csv {csv_columns}', column indices within "
                    "each specification must be different."
                )

    histogram = cmdargs["histogram"]
    if histogram:
        histogram_specifications = histogram.split()
        for specification in histogram_specifications:
            histogram_entries = specification.split(",")
            if len(histogram_entries) not in [1, 2]:
                fail(
                    f"Invalid value '-histogram {specification}', expected "
                    "'bins', 'bins,norm', or 'bins,lognorm'."
                )
            if not re.fullmatch(
                positive_integer,
                histogram_entries[0],
            ):
                fail(
                    f"Invalid value '-histogram {specification}', the number "
                    "of bins must be a positive integer."
                )
            if len(histogram_entries) == 2 and histogram_entries[1] not in [
                "norm",
                "lognorm",
            ]:
                fail(
                    f"Invalid value '-histogram {specification}', supported "
                    "distributions are 'norm' and 'lognorm'."
                )

    band_properties = cmdargs["bandprop"]
    if band_properties:
        band_entries = band_properties.split(",")
        if len(band_entries) % 2 != 0 or any(not color for color in band_entries[::2]):
            fail(
                f"Invalid value '-bandprop {band_properties}', expected "
                "color and alpha pairs."
            )
        try:
            alpha_values = [float(alpha) for alpha in band_entries[1::2]]
        except ValueError:
            alpha_values = []
        if not alpha_values or any(alpha < 0 or alpha > 1 for alpha in alpha_values):
            fail(
                f"Invalid value '-bandprop {band_properties}', alpha values "
                "must be between 0 and 1."
            )
        if cmdargs["ensemble"] not in ["1", "3"]:
            fail(
                "Invalid combination, '-bandprop' can only be used with "
                "'-ensemble 1' or '-ensemble 3'."
            )

    log_values = cmdargs["log"].split(",")
    if any(value not in ["0", "1"] for value in log_values):
        fail(
            f"Invalid value '-log {cmdargs['log']}', expected values containing "
            "only 0 or 1, separated by commas."
        )

    if cmdargs["clogthks"] and "1" not in log_values:
        fail(
            "Invalid combination, '-clogthks' requires at least one logarithmic "
            "color scale enabled with '-log'."
        )

    if cmdargs["maskthr"] != "1e-3" and not cmdargs["mask"]:
        fail(
            "Invalid combination, '-maskthr' can only be changed when '-mask' "
            "is used."
        )

    if (
        cmdargs["distance"]
        and "sensor" in cmdargs["distance"]
        and any(
            any(not re.fullmatch(positive_integer, entry) for entry in entries)
            for entries in slide_entries
        )
    ):
        fail(
            "Invalid combination, a sensor distance requires each location "
            "provided with '-s' to contain three positive indices."
        )

    vtk_names = cmdargs["vtknames"]
    if vtk_names:
        vtk_name_entries = vtk_names.split(",")
        if any(not name for name in vtk_name_entries):
            fail(
                f"Invalid value '-vtknames {vtk_names}', VTK variable names "
                "cannot be empty."
            )

    valid_vtk_formats = [
        "Float64",
        "Float32",
        "Float16",
        "Int64",
        "UInt64",
        "Int32",
        "UInt32",
        "Int16",
        "UInt16",
        "Int8",
        "UInt8",
    ]
    vtk_formats = cmdargs["vtkformat"].split(",")
    if any(vtk_format not in valid_vtk_formats for vtk_format in vtk_formats):
        fail(
            f"Invalid value '-vtkformat {cmdargs['vtkformat']}', valid "
            f"formats are {', '.join(valid_vtk_formats)}."
        )

    vtk_options = {
        "-p": ("path", "flow"),
        "-vtkformat": ("vtkformat", "Float64"),
        "-vtknames": ("vtknames", ""),
    }
    if not vtk_mode:
        invalid_options = [
            option
            for option, (name, default) in vtk_options.items()
            if cmdargs[name] != default
        ]
        if invalid_options:
            fail(
                f"Invalid option for '-m {mode}', the following options can "
                f"only be used with '-m vtk': {', '.join(invalid_options)}."
            )
    else:
        try:
            flow_arguments = shlex.split(cmdargs["path"])
        except ValueError:
            flow_arguments = []

        if not flow_arguments:
            fail(f"Invalid OPM Flow command '-p {cmdargs['path']}'.")

        try:
            flow_result = subprocess.run(
                [*flow_arguments, "-h"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                check=False,
            )
        except OSError:
            flow_result = None

        if flow_result is None or flow_result.returncode != 0:
            fail(
                f"The OPM Flow executable '-p {cmdargs['path']}' is not "
                "available or not working."
            )

    if not gif_mode:
        gif_options = {
            "-interval": ("interval", "1000"),
            "-loop": ("loop", "0"),
        }
        invalid_options = [
            option
            for option, (name, default) in gif_options.items()
            if cmdargs[name] != default
        ]
        if invalid_options:
            fail(
                f"Invalid option for '-m {mode}', the following options can "
                f"only be used with '-m gif': {', '.join(invalid_options)}."
            )
