# SPDX-FileCopyrightText: 2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Terminal output utilities for the plopm command-line interface."""

import argparse
import os
import sys
from collections.abc import Sequence
from typing import NoReturn

DEPRECATED_OPTION_ALIASES = {
    # Input and output
    "-csv": "-cc",
    "--csv": "--csv-columns",
    "-p": "-fp",
    "--path": "--flow-path",
    "--mode": "--format",
    "--output": "--output-dir",
    "-save": "-fn",
    "--save": "--filename",
    # Spatial and temporal selection
    "--slide": "--slice",
    "-tunits": "-tu",
    "--tunits": "--time-units",
    "-distance": "-dist",
    # Filtering, masking, and thresholds
    "-filter": "-flt",
    "--vmin": "--min-threshold",
    "--vmax": "--max-threshold",
    "-mask": "-mv",
    "--mask": "--mask-variable",
    "-maskthr": "-mt",
    "--maskthr": "--mask-threshold",
    # Computation and data transformation
    "-how": "-agg",
    "--how": "--aggregation",
    "-a": "-sf",
    "--adjust": "--scale-factor",
    "-diff": "-di",
    "--diff": "--difference-input",
    "-stress": "-sc",
    "--stress": "--stress-coefficient",
    "-dual": "-dg",
    "--dual": "--dual-grid",
    # Plot types and statistical representation
    "-histogram": "-hist",
    "-ensemble": "-ens",
    "-bandprop": "-fb",
    "--bandprop": "--fill-between-style",
    "-step": "-sp",
    "--step": "--step-plot",
    # Figure and subplot layout
    "-d": "-fs",
    "--dimensions": "--figsize",
    "-subfigs": "-sg",
    "--subfigs": "--subplot-grid",
    "-cbsfax": "-cbp",
    "--cbsfax": "--colorbar-position",
    "-delax": "-rdl",
    "--delax": "--remove-duplicate-labels",
    # Titles, labels, and legends
    "-suptitle": "-st",
    "-xlabel": "-xl",
    "-ylabel": "-yl",
    "-clabel": "-cbl",
    "--clabel": "--colorbar-label",
    "-labels": "-llb",
    "--labels": "--legend-labels",
    "-loc": "-ll",
    "--loc": "--legend-location",
    "-remove": "-hide",
    "--remove": "--hide-map-elements",
    # Axes, coordinates, and formatting
    "-xunits": "-xu",
    "-yunits": "-yu",
    "-z": "-asp",
    "--scale": "--equal-aspect",
    "-rotate": "-rot",
    "--rotate": "--rotation",
    "-translate": "-tr",
    "--translate": "--translation",
    "-xformat": "-xf",
    "-yformat": "-yf",
    "-xlnum": "-xnt",
    "--xlnum": "--xtick-count",
    "-ylnum": "-ynt",
    "--ylnum": "--ytick-count",
    # Color scales and styling
    "-b": "-cl",
    "--bounds": "--clim",
    "-log": "-clog",
    "--log": "--color-log",
    "-clogthks": "-clt",
    "--clogthks": "--color-log-ticks",
    "-global": "-gr",
    "--global": "--global-range",
    "-cformat": "-cbf",
    "--cformat": "--colorbar-format",
    "-cnum": "-cbn",
    "--cnum": "--colorbar-tick-count",
    "-cticks": "-cbt",
    "--cticks": "--colorbar-ticks",
    "--lw": "--linewidth",
    "-e": "-ls",
    "-axgrid": "-ag",
    "--axgrid": "--axis-grid",
    "-facecolor": "-fc",
    "-ncolor": "-ic",
    "--ncolor": "--inactive-color",
    "-grid": "-ge",
    "--grid": "--grid-edges",
    "-f": "-fz",
    "--size": "--fontsize",
    # VTK output
    "-vtkformat": "-vf",
    "--vtkformat": "--vtk-format",
    "-vtknames": "-vn",
    "--vtknames": "--vtk-names",
    # GIF output
    "-interval": "-gi",
    "--interval": "--gif-interval",
    "-loop": "-gl",
    "--loop": "--gif-loop",
    # Information and diagnostics
    "-printv": "-lv",
    "--printv": "--list-variables",
}
ANSI_BOLD_RED = "1;31"
ANSI_BOLD_YELLOW = "1;33"
ANSI_BOLD_GREEN = "1;32"
ANSI_BOLD_BLUE = "1;34"
ANSI_BOLD_MAGENTA = "1;35"
ANSI_YELLOW = "1;33"
ANSI_GREEN = "1;32"
ANSI_CYAN = "36"
ANSI_RED = "31"
ANSI_BLUE = "1;34"


class PlopmHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """Hide deprecated aliases while preserving argparse help styling."""

    def _format_action_invocation(
        self,
        action: argparse.Action,
    ) -> str:
        if not action.option_strings:
            return super()._format_action_invocation(action)

        original_options = action.option_strings
        visible_options = [
            option
            for option in original_options
            if option not in DEPRECATED_OPTION_ALIASES
        ]

        if not visible_options:
            return super()._format_action_invocation(action)

        try:
            action.option_strings = visible_options
            return super()._format_action_invocation(action)
        finally:
            action.option_strings = original_options


def warn_deprecated_options(argv: Sequence[str]) -> None:
    """Warn once for each deprecated command-line option used."""
    reported: set[str] = set()

    for argument in argv:
        option = argument.partition("=")[0]

        if option not in DEPRECATED_OPTION_ALIASES or option in reported:
            continue

        replacement = DEPRECATED_OPTION_ALIASES[option]

        plopm_warning(
            f"option {cli_deprecated_value(option)} is deprecated and will be "
            f"removed in the next release; use {cli_current_value(replacement)} "
            "instead"
        )
        reported.add(option)


def supports_color(stream: object = sys.stderr) -> bool:
    """Return whether the output stream supports terminal colors."""
    return (
        hasattr(stream, "isatty")
        and stream.isatty()
        and os.environ.get("NO_COLOR") is None
        and os.environ.get("TERM") != "dumb"
    )


def colorize(
    text: str,
    code: str,
    stream: object = sys.stderr,
) -> str:
    """Apply an ANSI color when the stream supports terminal colors."""
    if not supports_color(stream):
        return text
    return f"\033[{code}m{text}\033[0m"


def cli_deprecated_value(value: str) -> str:
    """Format a deprecated command-line option or value."""
    return colorize(repr(value), ANSI_YELLOW)


def cli_current_value(value: str) -> str:
    """Format a command-line option or value."""
    return colorize(repr(value), ANSI_GREEN)


def cli_error_value(value: str) -> str:
    """Format an error command-line option or value."""
    return colorize(repr(value), ANSI_RED)


def cli_info_value(value: str) -> str:
    """Format an info command-line option or value."""
    return colorize(repr(value), ANSI_BLUE)


def plopm_error(message: str) -> NoReturn:
    """Display a fatal CLI error and exit with status 1."""
    label = colorize("error", ANSI_BOLD_RED)
    raise SystemExit(f"{plopm_name()}: {label}: {message}")


def plopm_warning(message: str) -> None:
    """Display a non-fatal CLI warning."""
    label = colorize("warning", ANSI_BOLD_YELLOW)
    print(f"{plopm_name()}: {label}: {message}", file=sys.stderr)


def plopm_info(message: str) -> None:
    """Display an informational CLI message."""
    label = colorize("info", ANSI_BOLD_BLUE, sys.stdout)
    print(f"{plopm_name()}: {label}: {message}")


def plopm_tip(message: str) -> None:
    """Display a helpful CLI suggestion."""
    label = colorize("tip", ANSI_BOLD_MAGENTA, sys.stdout)
    print(f"{plopm_name(sys.stdout)}: {label}: {message}")


def plopm_success(output_dir: str, filenames: list[str]) -> None:
    """Display the output directory and generated filenames."""
    label = colorize("success", ANSI_BOLD_GREEN, sys.stdout)
    if not filenames:
        plopm_error("Unreachable code executed")
    elif len(filenames) == 1:
        print(f"{plopm_name()}: {label}: {output_dir}/{filenames[0]}")
    elif len(filenames) <= 5:
        print(f"{plopm_name()}: {label}")
        print(f"       Output directory: {output_dir}")
        print(f"       Files: {', '.join(filenames)}")
    else:
        print(f"{plopm_name()}: {label}")
        print(f"       Output directory: {output_dir}")
        print(f"       Files ({len(filenames)}):")
        for filename in filenames:
            print(f"         - {filename}")


def plopm_name(stream: object = sys.stderr) -> str:
    """Return the plopm name with gradient terminal colors."""
    characters = [
        ("p", "36"),
        ("l", "36"),
        ("o", "35"),
        ("p", "36"),
        ("m", "36"),
    ]
    return "".join(
        colorize(character, color, stream) for character, color in characters
    )
