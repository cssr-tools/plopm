# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0302,R1702,W0123,W1401,R0912,R0914,R0915

"""Postprocessing visualization tool for OPM Flow geological models"""

import argparse
import re
import shlex
import shutil
import subprocess
import sys

from plopm.utils.initialization import (
    ini_cfg,
    ini_properties,
    ini_summary,
    is_summary,
)
from plopm.utils.terminal import (
    PlopmHelpFormatter,
    cli_error_value,
    plopm_error,
    plopm_info,
    plopm_name,
    plopm_success,
    plopm_tip,
    warn_deprecated_options,
)
from plopm.utils.write_oned import make_plots
from plopm.utils.write_twod import make_maps
from plopm.utils.write_vtk import make_vtks


def main(argv: list[str] | None = None) -> None:
    """Main function for the plopm executable"""
    cmdargs = load_parser(argv)
    check_cmdargs(cmdargs)
    cfg = ini_cfg(cmdargs)
    if cfg.vtk:
        plopm_info("processing, please wait...")
        generated_files = make_vtks(
            cmdargs.flow_path,
            cfg.names,
            cfg.output_dir,
            cfg.filename,
            cfg.restart,
            cfg.vrs,
            cfg.vtk_format,
            cfg.vtk_names,
            cfg.gif,
            cfg.vtk,
            cfg.filter,
            cfg.scale_factor,
            cfg.mass,
            cfg.mass + cfg.xmass,
            cfg.caprock,
            cfg.stress_coefficient,
            cfg.filter,
        )
    else:
        if shutil.which("latex") is None:
            plopm_tip(
                "install LaTeX for improved fonts and text formatting; "
                f"see the {plopm_name()} documentation for installation instructions."
            )
        if is_summary(cfg):
            plopm_info("processing, please wait...")
            ini_summary(cfg)
            generated_files = make_plots(cfg)
        else:
            plopm_info("processing, please wait...")
            ini_properties(cfg)
            generated_files = make_maps(cfg)
    plopm_success(cfg.output_dir, generated_files)


def load_parser(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse plopm command-line arguments."""

    parser = argparse.ArgumentParser(
        formatter_class=PlopmHelpFormatter,
        description=(
            "plopm: Simplified and flexible Python tool for quick visualization "
            "of OPM Flow geological models. See the online documentation for "
            "examples and detailed option descriptions: "
            "https://cssr-tools.github.io/plopm/introduction.html#option-reference"
        ),
    )

    # ------------------------------------------------------------------
    # Input and data selection
    # ------------------------------------------------------------------

    inputs = parser.add_argument_group("Input and data selection")

    inputs.add_argument(
        "-i",
        "--input",
        type=str.strip,
        default="SPE11B",
        help=(
            "Base name or full path of the input. Separate multiple inputs "
            'with spaces, e.g. "SPE11B /home/user/SPE11B_TUNED"'
        ),
    )
    inputs.add_argument(
        "-v",
        "--variable",
        type=str.strip,
        default="poro,permx,permz,porv,fipnum,satnum",
        help=(
            "Variable specification(s) to plot, including standard variables, "
            "special variables, and expressions. Separate variables with commas"
        ),
    )
    inputs.add_argument(
        "-r",
        "--restart",
        type=str.strip,
        default="-1",
        help=(
            "Restart step(s): a single step, comma-separated steps, or "
            'start:end[:step], e.g. "-1", "0,3,10", or "5:505:250"'
        ),
    )
    inputs.add_argument(
        "-cc",
        "--csv-columns",
        "-csv",
        "--csv",
        type=str.strip,
        default="",
        help=(
            "CSV column indices starting at 1. Use t,value for time series or "
            "x,y,value for spatial maps; separate inputs with semicolons"
        ),
    )
    inputs.add_argument(
        "-fp",
        "--flow-path",
        "-p",
        "--path",
        type=str.strip,
        default="flow",
        help="Path or command for the Flow executable used for VTK grid generation",
    )

    # ------------------------------------------------------------------
    # Output options
    # ------------------------------------------------------------------

    output = parser.add_argument_group("Output options")

    output.add_argument(
        "-m",
        "--format",
        "--mode",
        type=str.strip,
        choices=["png", "gif", "csv", "vtk"],
        default="png",
        help="Output format",
    )
    output.add_argument(
        "-o",
        "--output-dir",
        "--output",
        type=str.strip,
        default=".",
        help="Base name or full path of the output directory",
    )
    output.add_argument(
        "-fn",
        "--filename",
        "-save",
        "--save",
        type=str.strip,
        default="",
        help="Output file name",
    )

    # ------------------------------------------------------------------
    # Spatial and temporal selection
    # ------------------------------------------------------------------

    selection = parser.add_argument_group("Spatial and temporal selection")

    selection.add_argument(
        "-s",
        "--slice",
        "--slide",
        type=str.strip,
        default=",1,",
        help=(
            "Spatial selection in i,j,k form, e.g. "
            '"10,," for a plane, ",,5:10" for a range, '
            '":,5,7" for a line, or "2,4,9" for a cell over time'
        ),
    )
    selection.add_argument(
        "-tu",
        "--time-units",
        "-tunits",
        "--tunits",
        type=str.strip,
        choices=["s", "m", "h", "d", "w", "y", "dates", "empty", "tstep"],
        default="d",
        help="Summary-plot x-axis time units",
    )
    selection.add_argument(
        "-dist",
        "--distance",
        "-distance",
        type=str.strip,
        choices=["min,sensor", "max,sensor", "min,border", "max,border", ""],
        default="",
        help="Compute the minimum or maximum distance to a sensor or lateral border",
    )

    # ------------------------------------------------------------------
    # Filtering, masking, and thresholds
    # ------------------------------------------------------------------

    filtering = parser.add_argument_group("Filtering, masking, and thresholds")

    filtering.add_argument(
        "-flt",
        "--filter",
        "-filter",
        type=str.strip,
        default="",
        help=(
            "Cell-selection conditions. Join conditions for one input with '&' "
            "and separate filters for different inputs with commas"
        ),
    )
    filtering.add_argument(
        "-vmin",
        "--min-threshold",
        "--vmin",
        type=str.strip,
        default="",
        help="Minimum threshold used to remove variable values",
    )
    filtering.add_argument(
        "-vmax",
        "--max-threshold",
        "--vmax",
        type=str.strip,
        default="",
        help="Maximum threshold used to remove variable values",
    )
    filtering.add_argument(
        "-mv",
        "--mask-variable",
        "-mask",
        "--mask",
        type=str.strip,
        default="",
        help="Static variable used as the background of a 2D map",
    )
    filtering.add_argument(
        "-mt",
        "--mask-threshold",
        "-maskthr",
        "--maskthr",
        type=str.strip,
        default="1e-3",
        help="Threshold applied to the mask variable",
    )

    # ------------------------------------------------------------------
    # Computation and data transformation
    # ------------------------------------------------------------------

    computation = parser.add_argument_group("Computation and data transformation")

    computation.add_argument(
        "-agg",
        "--aggregation",
        "-how",
        "--how",
        type=str.strip,
        default="",
        help=(
            "Aggregation or selection method for 2D slices and projections: "
            "min, max, sum, mean, pvmean, harmonic, arithmetic, first, or last"
        ),
    )
    computation.add_argument(
        "-sf",
        "--scale-factor",
        "-a",
        "--adjust",
        type=str.strip,
        default="1",
        help=(
            "Multiplicative scaling factor applied to variable values, "
            "e.g. 1e-9 to display mass in Mt"
        ),
    )
    computation.add_argument(
        "-di",
        "--difference-input",
        "-diff",
        "--diff",
        type=str.strip,
        default="",
        help="Base name or full path of the input model to subtract",
    )
    computation.add_argument(
        "-sc",
        "--stress-coefficient",
        "-stress",
        "--stress",
        type=str.strip,
        default="0.134",
        help=(
            "Stress coefficient used to compute pressure limits for "
            "limipres, overpres, and objepres"
        ),
    )
    computation.add_argument(
        "-dg",
        "--dual-grid",
        "-dual",
        "--dual",
        type=str.strip,
        default="0",
        help="Enable dual-grid processing using 0 or 1",
    )

    # ------------------------------------------------------------------
    # Plot types and statistical representation
    # ------------------------------------------------------------------

    plot_types = parser.add_argument_group("Plot types and statistical representation")

    plot_types.add_argument(
        "-hist",
        "--histogram",
        "-histogram",
        type=str.strip,
        default="",
        help=(
            "Histogram bins and optional distribution, e.g. "
            '"20", "20,norm", or "20,lognorm"'
        ),
    )
    plot_types.add_argument(
        "-ens",
        "--ensemble",
        "-ensemble",
        type=str.strip,
        choices=["0", "1", "2", "3"],
        default="0",
        help=(
            "Ensemble plotting mode: 0 disables it, 1 plots mean and error "
            "bands, 2 plots minimum, mean, and maximum, and 3 plots both"
        ),
    )
    plot_types.add_argument(
        "-fb",
        "--fill-between-style",
        "-bandprop",
        "--bandprop",
        type=str.strip,
        default="",
        help="Fill colors and alpha values for ensemble error bands",
    )
    plot_types.add_argument(
        "-sp",
        "--step-plot",
        "-step",
        "--step",
        type=str.strip,
        choices=["0", "1"],
        default="0",
        help="Use ax.step instead of ax.plot",
    )

    # ------------------------------------------------------------------
    # Figure and subplot layout
    # ------------------------------------------------------------------

    layout = parser.add_argument_group("Figure and subplot layout")

    layout.add_argument(
        "-fs",
        "--figsize",
        "-d",
        "--dimensions",
        type=str.strip,
        default="7,5",
        help='Figure width and height in inches, e.g. "8,16"',
    )
    layout.add_argument(
        "-sg",
        "--subplot-grid",
        "-subfigs",
        "--subfigs",
        type=str.strip,
        default="",
        help='Number of subplot rows and columns, e.g. "2,2"',
    )
    layout.add_argument(
        "-cbp",
        "--colorbar-position",
        "-cbsfax",
        "--cbsfax",
        type=str.strip,
        default="0.2,0.01,0.6,0.02",
        help=(
            "Global colorbar position and size as left,bottom,width,height; "
            "use 'empty' to remove it"
        ),
    )
    layout.add_argument(
        "-rdl",
        "--remove-duplicate-labels",
        "-delax",
        "--delax",
        type=str.strip,
        choices=["0", "1"],
        default="0",
        help="Remove duplicated axis labels in subplot layouts",
    )

    # ------------------------------------------------------------------
    # Titles, labels, and legends
    # ------------------------------------------------------------------

    text = parser.add_argument_group("Titles, labels, and legends")

    text.add_argument(
        "-t",
        "--title",
        type=str.strip,
        default="0",
        help="Figure title; separate titles for multiple plots with two spaces",
    )
    text.add_argument(
        "-st",
        "--suptitle",
        "-suptitle",
        type=str.strip,
        default="",
        help="Title for a group of subplots; use 0 to remove it",
    )
    text.add_argument(
        "-xl",
        "--xlabel",
        "-xlabel",
        type=str.strip,
        default="",
        help="X-axis label; separate labels for multiple plots with two spaces",
    )
    text.add_argument(
        "-yl",
        "--ylabel",
        "-ylabel",
        type=str.strip,
        default="",
        help="Y-axis label; separate labels for multiple plots with two spaces",
    )
    text.add_argument(
        "-cbl",
        "--colorbar-label",
        "-clabel",
        "--clabel",
        type=str.strip,
        default="",
        help="Colorbar label; separate labels for multiple plots with two spaces",
    )
    text.add_argument(
        "-llb",
        "--legend-labels",
        "-labels",
        "--labels",
        type=str.strip,
        default="",
        help="Summary-plot legend labels separated by two spaces",
    )
    text.add_argument(
        "-ll",
        "--legend-location",
        "-loc",
        "--loc",
        type=str.strip,
        default="best",
        help="Legend location passed to matplotlib; use 'empty' to remove it",
    )
    text.add_argument(
        "-hide",
        "--hide-map-elements",
        "-remove",
        "--remove",
        type=str.strip,
        default="0,0,0,0",
        help=(
            "Hide the left axis, bottom axis, colorbar, and title using four "
            "comma-separated values of 0 or 1"
        ),
    )

    # ------------------------------------------------------------------
    # Axes, coordinates, and formatting
    # ------------------------------------------------------------------

    axes = parser.add_argument_group("Axes, coordinates, and formatting")

    axes.add_argument(
        "-x",
        "--xlim",
        type=str.strip,
        default="",
        help='X-axis limits in display order, e.g. "[-100,200]"',
    )
    axes.add_argument(
        "-y",
        "--ylim",
        type=str.strip,
        default="",
        help='Y-axis limits in display order, e.g. "[0,300]"',
    )
    axes.add_argument(
        "-xu",
        "--xunits",
        "-xunits",
        type=str.strip,
        choices=["mm", "cm", "m", "km"],
        default="m",
        help="Spatial-map x-axis units",
    )
    axes.add_argument(
        "-yu",
        "--yunits",
        "-yunits",
        type=str.strip,
        choices=["mm", "cm", "m", "km"],
        default="m",
        help="Spatial-map y-axis units",
    )
    axes.add_argument(
        "-asp",
        "--equal-aspect",
        "-z",
        "--scale",
        type=str.strip,
        choices=["0", "1"],
        default="1",
        help="Scale the axes equally in 2D maps",
    )
    axes.add_argument(
        "-rot",
        "--rotation",
        "-rotate",
        "--rotate",
        type=str.strip,
        default="0",
        help="Grid rotation angle in degrees for 2D maps",
    )
    axes.add_argument(
        "-tr",
        "--translation",
        "-translate",
        "--translate",
        type=str.strip,
        default="[0,0]",
        help='Grid translation in the x and y directions, e.g. "[100,-50]"',
    )
    axes.add_argument(
        "-xlog",
        "--xlog",
        type=str.strip,
        default="0",
        help="Enable the logarithmic x-axis using 0 or 1",
    )
    axes.add_argument(
        "-ylog",
        "--ylog",
        type=str.strip,
        default="0",
        help="Enable the logarithmic y-axis using 0 or 1",
    )
    axes.add_argument(
        "-xf",
        "--xformat",
        "-xformat",
        type=str.strip,
        default="",
        help='X-axis number format, e.g. ".2e"',
    )
    axes.add_argument(
        "-yf",
        "--yformat",
        "-yformat",
        type=str.strip,
        default="",
        help='Y-axis number format, e.g. ".1f"',
    )
    axes.add_argument(
        "-xnt",
        "--xtick-count",
        "-xlnum",
        "--xlnum",
        type=str.strip,
        default="5",
        help="Number of x-axis ticks",
    )
    axes.add_argument(
        "-ynt",
        "--ytick-count",
        "-ylnum",
        "--ylnum",
        type=str.strip,
        default="5",
        help="Number of y-axis ticks",
    )

    # ------------------------------------------------------------------
    # Color scales and styling
    # ------------------------------------------------------------------

    styling = parser.add_argument_group("Color scales and styling")

    styling.add_argument(
        "-c",
        "--colors",
        type=str.strip,
        default="",
        help='Colormap or summary-plot colors, e.g. "jet" or "b,r"',
    )
    styling.add_argument(
        "-cl",
        "--clim",
        "-b",
        "--bounds",
        type=str.strip,
        default="",
        help='Color-scale limits in display order, e.g. "[-0.1,11]"',
    )
    styling.add_argument(
        "-clog",
        "--color-log",
        "-log",
        "--log",
        type=str.strip,
        default="0",
        help="Enable logarithmic color scaling using 0 or 1",
    )
    styling.add_argument(
        "-clt",
        "--color-log-ticks",
        "-clogthks",
        "--clogthks",
        type=str.strip,
        default="",
        help='Tick values for logarithmic color scales, e.g. "[1,10,100]"',
    )
    styling.add_argument(
        "-gr",
        "--global-range",
        "-global",
        "--global",
        type=str.strip,
        choices=["0", "1"],
        default="0",
        help="Use the current slice range or whole-model range for color scaling",
    )
    styling.add_argument(
        "-cbf",
        "--colorbar-format",
        "-cformat",
        "--cformat",
        type=str.strip,
        default="",
        help='Colorbar number format, e.g. ".2f"',
    )
    styling.add_argument(
        "-cbn",
        "--colorbar-tick-count",
        "-cnum",
        "--cnum",
        type=str.strip,
        default="",
        help="Number of colorbar ticks",
    )
    styling.add_argument(
        "-cbt",
        "--colorbar-ticks",
        "-cticks",
        "--cticks",
        type=str.strip,
        default="",
        help='Custom colorbar tick labels, e.g. "[A,B,C]"',
    )
    styling.add_argument(
        "-lw",
        "--linewidth",
        "--lw",
        type=str.strip,
        default="",
        help="Line widths separated by commas",
    )
    styling.add_argument(
        "-ls",
        "--linestyle",
        "-e",
        type=str.strip,
        default="",
        help='Line styles separated by commas, e.g. "solid,dotted"',
    )
    styling.add_argument(
        "-ag",
        "--axis-grid",
        "-axgrid",
        "--axgrid",
        type=str.strip,
        choices=["0", "1"],
        default="1",
        help="Display the summary-plot axis grid",
    )
    styling.add_argument(
        "-fc",
        "--facecolor",
        "-facecolor",
        type=str.strip,
        default="w",
        help="Color outside the spatial map",
    )
    styling.add_argument(
        "-ic",
        "--inactive-color",
        "-ncolor",
        "--ncolor",
        type=str.strip,
        default="w",
        help="Color for inactive cells in 2D maps",
    )
    styling.add_argument(
        "-ge",
        "--grid-edges",
        "-grid",
        "--grid",
        type=str.strip,
        default="",
        help="pcolormesh edge color and line width separated by a comma",
    )
    styling.add_argument(
        "-fz",
        "--fontsize",
        "-f",
        "--size",
        type=str.strip,
        default="12",
        help="Font size",
    )
    styling.add_argument(
        "-dpi",
        "--dpi",
        type=str.strip,
        default="500",
        help="Figure resolution in dots per inch",
    )

    # ------------------------------------------------------------------
    # VTK output
    # ------------------------------------------------------------------

    vtk = parser.add_argument_group("VTK output")

    vtk.add_argument(
        "-vf",
        "--vtk-format",
        "-vtkformat",
        "--vtkformat",
        type=str.strip,
        default="Float64",
        help="VTK data type for each variable, separated by commas",
    )
    vtk.add_argument(
        "-vn",
        "--vtk-names",
        "-vtknames",
        "--vtknames",
        type=str.strip,
        default="",
        help="Custom VTK variable names separated by commas",
    )

    # ------------------------------------------------------------------
    # GIF output
    # ------------------------------------------------------------------

    gif = parser.add_argument_group("GIF output")

    gif.add_argument(
        "-gi",
        "--gif-interval",
        "-interval",
        "--interval",
        type=str.strip,
        default="1000",
        help="GIF frame interval in milliseconds",
    )
    gif.add_argument(
        "-gl",
        "--gif-loop",
        "-loop",
        "--loop",
        type=str.strip,
        default="0",
        help="Loop GIF animations indefinitely using 0 or 1",
    )

    # ------------------------------------------------------------------
    # Information and diagnostics
    # ------------------------------------------------------------------

    diagnostics = parser.add_argument_group("Information and diagnostics")

    diagnostics.add_argument(
        "-lv",
        "--list-variables",
        "-printv",
        "--printv",
        type=str.strip,
        choices=["0", "1"],
        default="0",
        help="Print the available variables",
    )

    parsed_argv = sys.argv[1:] if argv is None else argv

    warn_deprecated_options(parsed_argv)

    return parser.parse_args(parsed_argv)


def check_cmdargs(cmdargs: argparse.Namespace) -> None:
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

    def parse_number(option: str, value: str) -> float:
        try:
            number = float(value)
        except ValueError:
            plopm_error(
                f"expected a number, not {cli_error_value(f'{option} {value}')}."
            )
        return number

    def parse_number_list(
        option: str,
        value: str,
        expected_length: int | None = None,
    ) -> list:
        entries = value.split(",")
        if expected_length is not None and len(entries) != expected_length:
            plopm_error(
                f"expected {expected_length} numbers separated by commas, "
                f"not {cli_error_value(f'{option} {value}')}."
            )
        try:
            numbers = [float(entry) for entry in entries]
        except ValueError:
            plopm_error(
                "expected numbers separated by commas, "
                f"not {cli_error_value(f'{option} {value}')}."
            )
        return numbers

    mode = cmdargs.format
    vtk_mode = mode == "vtk"
    gif_mode = mode == "gif"
    number = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
    positive_integer = r"[1-9]\d*"
    non_negative_integer = r"\d+"

    if not cmdargs.input:
        plopm_error(f"the input {cli_error_value('-i')} cannot be empty.")
    if not cmdargs.output_dir:
        plopm_error(f"the output folder {cli_error_value('-o')} cannot be empty.")
    if not cmdargs.variable:
        plopm_error(f"the variable {cli_error_value('-v')} cannot be empty.")

    positive_number_options = [
        ("-fz", "fontsize"),
        ("-dpi", "dpi"),
        ("-xnt", "xtick_count"),
        ("-ynt", "ytick_count"),
        ("-mt", "mask_threshold"),
        ("-gi", "gif_interval"),
    ]
    for option, name in positive_number_options:
        raw_value = getattr(cmdargs, name)
        value = parse_number(option, raw_value)
        if value <= 0:
            plopm_error(
                f"expected a positive number, not "
                f"{cli_error_value(f'{option} {raw_value}')}."
            )

    number_options = [
        ("-sc", "stress_coefficient"),
        ("-rot", "rotation"),
    ]
    for option, name in number_options:
        parse_number(option, getattr(cmdargs, name))

    parse_number_list("-sf", cmdargs.scale_factor)

    optional_number_options = [
        ("-vmin", "min_threshold"),
        ("-vmax", "max_threshold"),
    ]
    for option, name in optional_number_options:
        value = getattr(cmdargs, name)
        if value:
            parse_number(option, value)

    if (
        cmdargs.min_threshold
        and cmdargs.max_threshold
        and float(cmdargs.min_threshold) > float(cmdargs.max_threshold)
    ):
        plopm_error(
            f"the minimum threshold "
            f"{cli_error_value(f'-vmin {cmdargs.min_threshold}')} must not be "
            f"greater than the maximum threshold "
            f"{cli_error_value(f'-vmax {cmdargs.max_threshold}')}."
        )

    colorbar_tick_numbers = cmdargs.colorbar_tick_count
    if colorbar_tick_numbers:
        cnum_entries = colorbar_tick_numbers.split(",")
        if any(not re.fullmatch(positive_integer, entry) for entry in cnum_entries):
            plopm_error(
                "expected positive integers separated by commas, "
                f"not {cli_error_value(f'-cbn {colorbar_tick_numbers}')}."
            )

    boolean_options = [
        ("-xlog", "xlog"),
        ("-ylog", "ylog"),
        ("-clog", "color_log"),
        ("-dg", "dual_grid"),
        ("-gl", "gif_loop"),
    ]
    for option, name in boolean_options:
        raw_value = getattr(cmdargs, name)
        values = raw_value.split(",")
        if any(value not in ["0", "1"] for value in values):
            plopm_error(
                "expected values containing only 0 or 1, separated by commas, "
                f"not {cli_error_value(f'{option} {raw_value}')}."
            )

    dimensions = parse_number_list(
        "-fs",
        cmdargs.figsize,
        2,
    )
    if any(value <= 0 for value in dimensions):
        plopm_error(
            f"figure dimensions must be positive, not "
            f"{cli_error_value(f'-fs {cmdargs.figsize}')}."
        )

    translation = cmdargs.translation
    if not re.fullmatch(
        rf"\[\s*{number}\s*,\s*{number}\s*\]",
        translation,
    ):
        plopm_error(
            f"expected two numbers enclosed by brackets, such as "
            f"{cli_error_value('-tr [10,-5]')}, not "
            f"{cli_error_value(f'-tr {translation}')}."
        )

    interval_pattern = re.compile(rf"\[\s*({number})\s*,\s*({number})\s*\]")
    for option, name in [
        ("-cl", "clim"),
        ("-x", "xlim"),
        ("-y", "ylim"),
    ]:
        value = getattr(cmdargs, name)
        if not value:
            continue
        for interval_value in value.split():
            if not interval_pattern.fullmatch(interval_value):
                plopm_error(
                    f"expected two numeric bounds enclosed by brackets, such "
                    f"as {cli_error_value(f'{option} [0,10]')}, not "
                    f"{cli_error_value(f'{option} {interval_value}')}."
                )

    aggregation_methods = cmdargs.aggregation
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
            plopm_error(
                f"expected aggregation methods from "
                f"{', '.join(valid_aggregation_methods)}, not "
                f"{cli_error_value(f'-agg {aggregation_methods}')}."
            )

    slide = cmdargs.slice
    slides = slide.split()
    slide_entry_pattern = re.compile(
        rf"(?:{positive_integer}|" rf"{positive_integer}:{positive_integer}|:)?"
    )
    if not slides:
        plopm_error(f"the slide selection {cli_error_value('-s')} cannot be empty.")

    slide_entries: list[list[str]] = []
    for selection in slides:
        entries = selection.split(",")
        if len(entries) != 3 or any(
            not slide_entry_pattern.fullmatch(entry) for entry in entries
        ):
            plopm_error(
                f"expected three i,j,k entries separated by commas, using "
                f"positive indices, ':', or ranges, not "
                f"{cli_error_value(f'-s {selection}')}."
            )
        if all(not entry for entry in entries):
            plopm_error(
                f"at least one slide entry must be provided with "
                f"{cli_error_value(f'-s {selection}')}."
            )
        colon_entries = 0
        for entry in entries:
            if ":" not in entry:
                continue
            colon_entries += 1
            if entry != ":":
                start, end = (int(index) for index in entry.split(":"))
                if start > end:
                    plopm_error(
                        f"the end of range {cli_error_value(entry)} in "
                        f"{cli_error_value(f'-s {selection}')} must not be smaller "
                        "than the start."
                    )
        if colon_entries > 1:
            plopm_error(
                f"only one slide direction in "
                f"{cli_error_value(f'-s {selection}')} can contain ':' or an index "
                "range."
            )
        slide_entries.append(entries)

    restart = cmdargs.restart
    restart_pattern = re.compile(
        rf"(?:-1|"
        rf"{non_negative_integer}(?:,{non_negative_integer})*|"
        rf"{non_negative_integer}:{non_negative_integer}"
        rf"(?::{positive_integer})?)"
    )
    if not restart_pattern.fullmatch(restart):
        plopm_error(
            f"expected '-1', non-negative restart indices separated by "
            f"commas, or 'start:end[:step]', not "
            f"{cli_error_value(f'-r {restart}')}."
        )

    if ":" in restart:
        restart_range = [int(value) for value in restart.split(":")]
        if restart_range[0] > restart_range[1]:
            plopm_error(
                f"the end of restart range {cli_error_value(f'-r {restart}')} must "
                "not be smaller than the start."
            )

    list_options = [
        ("-c", "colors"),
        ("-ls", "linestyle"),
    ]
    for option, name in list_options:
        value = getattr(cmdargs, name)
        if value and any(not entry for entry in value.split(",")):
            plopm_error(
                f"entries in {cli_error_value(f'{option} {value}')} cannot be empty."
            )

    line_widths = cmdargs.linewidth
    if line_widths:
        width_values = parse_number_list("-lw", line_widths)
        if any(width <= 0 for width in width_values):
            plopm_error(
                f"line widths must be positive, not "
                f"{cli_error_value(f'-lw {line_widths}')}."
            )

    remove = cmdargs.hide_map_elements
    remove_entries = remove.split(",")
    if len(remove_entries) != 4 or any(
        entry not in ["0", "1"] for entry in remove_entries
    ):
        plopm_error(
            f"expected four values containing only 0 or 1, not "
            f"{cli_error_value(f'-hide {remove}')}."
        )

    subfigs = cmdargs.subplot_grid
    if subfigs:
        subfig_entries = subfigs.split(",")
        if len(subfig_entries) != 2 or any(
            not re.fullmatch(positive_integer, entry) for entry in subfig_entries
        ):
            plopm_error(
                f"expected two positive integers separated by a comma, such "
                f"as {cli_error_value('-sg 2,2')}, not "
                f"{cli_error_value(f'-sg {subfigs}')}."
            )

    colorbar_axis = cmdargs.colorbar_position
    if colorbar_axis != "empty":
        colorbar_axis_values = parse_number_list(
            "-cbp",
            colorbar_axis,
            4,
        )
        if colorbar_axis_values[0] < 0 or colorbar_axis_values[1] < 0:
            plopm_error(
                f"the left and bottom positions in "
                f"{cli_error_value(f'-cbp {colorbar_axis}')} cannot be negative."
            )
        if colorbar_axis_values[2] <= 0 or colorbar_axis_values[3] <= 0:
            plopm_error(
                f"the width and height in "
                f"{cli_error_value(f'-cbp {colorbar_axis}')} must be positive."
            )

    grid = cmdargs.grid_edges
    if grid:
        grid_entries = grid.split(",")
        if len(grid_entries) != 2 or not grid_entries[0] or not grid_entries[1]:
            plopm_error(
                f"expected a color and line width separated by a comma, not "
                f"{cli_error_value(f'-ge {grid}')}."
            )
        if parse_number("-ge", grid_entries[1]) < 0:
            plopm_error(
                f"the line width in {cli_error_value(f'-ge {grid}')} cannot be "
                "negative."
            )

    csv_columns = cmdargs.csv_columns
    if csv_columns:
        csv_specifications = csv_columns.split(";")
        for specification in csv_specifications:
            if not specification:
                continue
            column_entries = specification.split(",")
            if len(column_entries) not in [2, 3] or any(
                not re.fullmatch(positive_integer, entry) for entry in column_entries
            ):
                plopm_error(
                    f"each non-empty specification in "
                    f"{cli_error_value(f'-cc {csv_columns}')} must contain two "
                    "column indices for a time series or three column indices "
                    "for a spatial map."
                )
            if len(set(column_entries)) != len(column_entries):
                plopm_error(
                    f"column indices within each specification in "
                    f"{cli_error_value(f'-cc {csv_columns}')} must be different."
                )

    histogram = cmdargs.histogram
    if histogram:
        histogram_specifications = histogram.split()
        for specification in histogram_specifications:
            histogram_entries = specification.split(",")
            if len(histogram_entries) not in [1, 2]:
                plopm_error(
                    f"expected 'bins', 'bins,norm', or 'bins,lognorm', not "
                    f"{cli_error_value(f'-hist {specification}')}."
                )
            if not re.fullmatch(
                positive_integer,
                histogram_entries[0],
            ):
                plopm_error(
                    f"the number of bins in "
                    f"{cli_error_value(f'-hist {specification}')} must be a positive "
                    "integer."
                )
            if len(histogram_entries) == 2 and histogram_entries[1] not in [
                "norm",
                "lognorm",
            ]:
                plopm_error(
                    f"the distribution in "
                    f"{cli_error_value(f'-hist {specification}')} must be 'norm' or "
                    "'lognorm'."
                )

    band_properties = cmdargs.fill_between_style
    if band_properties:
        band_entries = band_properties.split(",")
        if len(band_entries) % 2 != 0 or any(not color for color in band_entries[::2]):
            plopm_error(
                f"expected color and alpha pairs, not "
                f"{cli_error_value(f'-fb {band_properties}')}."
            )
        try:
            alpha_values = [float(alpha) for alpha in band_entries[1::2]]
        except ValueError:
            alpha_values = []
        if not alpha_values or any(alpha < 0 or alpha > 1 for alpha in alpha_values):
            plopm_error(
                f"alpha values in {cli_error_value(f'-fb {band_properties}')} must "
                "be between 0 and 1."
            )
        if cmdargs.ensemble not in ["1", "3"]:
            plopm_error(
                f"{cli_error_value('-fb')} can only be used with "
                f"{cli_error_value('-ens 1')} or {cli_error_value('-ens 3')}."
            )

    log_values = cmdargs.color_log.split(",")

    if cmdargs.color_log_ticks and "1" not in log_values:
        plopm_error(
            f"{cli_error_value('-clt')} requires at least one logarithmic color "
            f"scale enabled with {cli_error_value('-clog')}."
        )

    if cmdargs.mask_threshold != "1e-3" and not cmdargs.mask_variable:
        plopm_error(
            f"{cli_error_value('-mt')} can only be changed when "
            f"{cli_error_value('-mv')} is used."
        )

    if (
        cmdargs.distance
        and "sensor" in cmdargs.distance
        and any(
            any(not re.fullmatch(positive_integer, entry) for entry in entries)
            for entries in slide_entries
        )
    ):
        plopm_error(
            f"a sensor distance requires each location provided with "
            f"{cli_error_value('-s')} to contain three positive indices."
        )

    vtk_names = cmdargs.vtk_names
    if vtk_names:
        vtk_name_entries = vtk_names.split(",")
        if any(not name for name in vtk_name_entries):
            plopm_error(
                f"VTK variable names in {cli_error_value(f'-vn {vtk_names}')} "
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
    vtk_formats = cmdargs.vtk_format.split(",")
    if any(vtk_format not in valid_vtk_formats for vtk_format in vtk_formats):
        plopm_error(
            f"expected VTK formats from {', '.join(valid_vtk_formats)}, not "
            f"{cli_error_value(f'-vf {cmdargs.vtk_format}')}."
        )

    vtk_options = {
        "-fp": ("flow_path", "flow"),
        "-vf": ("vtk_format", "Float64"),
        "-vn": ("vtk_names", ""),
    }
    if not vtk_mode:
        invalid_options = [
            option
            for option, (name, default) in vtk_options.items()
            if getattr(cmdargs, name) != default
        ]
        if invalid_options:
            formatted_options = ", ".join(
                cli_error_value(option) for option in invalid_options
            )
            plopm_error(
                f"{formatted_options} can only be used with "
                f"{cli_error_value('-m vtk')}, not {cli_error_value(f'-m {mode}')}."
            )
    else:
        try:
            flow_arguments = shlex.split(cmdargs.flow_path)
        except ValueError:
            flow_arguments = []

        if not flow_arguments:
            plopm_error(
                f"the OPM Flow command "
                f"{cli_error_value(f'-fp {cmdargs.flow_path}')} cannot be empty."
            )

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
            plopm_error(
                f"the OPM Flow executable "
                f"{cli_error_value(f'-fp {cmdargs.flow_path}')} is not available or "
                "not working."
            )

    if not gif_mode:
        gif_options = {
            "-gi": ("gif_interval", "1000"),
            "-gl": ("gif_loop", "0"),
        }
        invalid_options = [
            option
            for option, (name, default) in gif_options.items()
            if getattr(cmdargs, name) != default
        ]
        if invalid_options:
            formatted_options = ", ".join(
                cli_error_value(option) for option in invalid_options
            )
            plopm_error(
                f"{formatted_options} can only be used with "
                f"{cli_error_value('-m gif')}, not {cli_error_value(f'-m {mode}')}."
            )
