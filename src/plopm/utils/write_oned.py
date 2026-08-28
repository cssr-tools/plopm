# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W3301,W0123,R0912,R0915,R0914,R1702,W0611,R0913,R0917,C0302,C0115,R0916,E1102

"""Create one-dimensional plots and tabular output from OPM results.

The module reads summary vectors, grid-derived series, and optional CSV data.
It also supports ensemble statistics, subplot layouts, and PNG or CSV output.
"""

import os
import warnings

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy.typing import NDArray
from scipy.interpolate import interp1d
from scipy.stats import lognorm, norm

from plopm.config.config import PlopmConfig
from plopm.utils.readers import read_series
from plopm.utils.terminal import cli_info_value, plopm_info


def make_plots(cfg: PlopmConfig) -> list[str]:
    """Create the requested one-dimensional plots and CSV files.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized plotting configuration.

    Returns
    -------
    list[str]
        Names of the generated files.

    """
    generated_files: list[str] = []

    deckn = _get_deck_name(cfg.cases[0][0])
    fig, _ = plt.subplots(1, 1)
    if (
        cfg.ensemble == 0
        and not cfg.subplot_grid[0]
        and len(cfg.cases[0]) < len(cfg.variables)
    ):
        cfg.cases[0] = [cfg.cases[0][0]] * len(cfg.variables)
        if len(cfg.linewidth[0]) < len(cfg.variables):
            cfg.linewidth[0] = [cfg.linewidth[0][0]] * len(cfg.variables)
            cfg.linewidth = [cfg.linewidth[0]] * len(cfg.variables)
        if len(cfg.colors[0]) < len(cfg.variables):
            cfg.colors[0] = [cfg.colors[0][0]] * len(cfg.variables)
            cfg.colors = [cfg.colors[0]] * len(cfg.variables)
        if len(cfg.linestyle[0]) < len(cfg.variables):
            cfg.linestyle[0] = [cfg.linestyle[0][0]] * len(cfg.variables)
            cfg.linestyle = [cfg.linestyle[0]] * len(cfg.variables)
    if cfg.subplot_grid[0]:
        plt.close()
        fig, axes = plt.subplots(
            int(cfg.subplot_grid[0]), int(cfg.subplot_grid[1]), layout="compressed"
        )
    for j, quan in enumerate(cfg.variables):
        k = j
        if not cfg.subplot_grid[0]:
            plt.close()
            fig, axes = plt.subplots(1, 1, layout="compressed")
            axes = np.array([axes])
            k = 0
        axis = axes.flat[k]
        axis.grid(int(cfg.axis_grid[j]))
        if cfg.ensemble > 0:
            tunit, vunit, min_t, max_t, min_v, max_v = _plot_ensemble(cfg, axes)
        else:
            ylow = 0 if cfg.ylog[j] == "1" else -np.inf
            xlow = 0 if cfg.xlog[j] == "1" else -np.inf
            min_t, max_t, min_v, max_v = 0, 0, 0, 0
            for i, name in enumerate(cfg.cases[j]):
                jj = j
                if len(cfg.variables) == len(cfg.cases[0]) and not cfg.subplot_grid[0]:
                    jj = i
                    quan = cfg.variables[i]
                time, var, tunit, vunit = read_series(
                    cfg, name, quan, cfg.time_units[jj], float(cfg.scale_factor[jj]), i
                )
                label = _get_label(cfg, name, jj, i)
                if cfg.step_plot:
                    axis.step(
                        time,
                        var,
                        color=cfg.colors[jj][i % len(cfg.colors[jj])],
                        ls=cfg.linestyle[jj][i % len(cfg.linestyle[jj])],
                        label=label,
                        lw=float(cfg.linewidth[jj][i]),
                    )
                elif cfg.histogram[0]:
                    ij = i + j * len(cfg.cases[j])
                    if (
                        len(cfg.variables) == len(cfg.cases[0])
                        and not cfg.subplot_grid[0]
                    ):
                        ij = i
                    hist = cfg.histogram[ij].split(",")
                    mean = np.nanmean(var)
                    std = np.nanstd(var)
                    plopm_info(
                        f"histogram: {cli_info_value(f'mean={mean:.6E}')}, "
                        f"{cli_info_value(f'std={std:.6E}')}"
                    )
                    if not cfg.legend_labels[0][0]:
                        label += f" (mean={mean:.3E}, std={std:.3E})"
                    counts, bins, _ = axis.hist(
                        var,
                        int(hist[0]),
                        color=cfg.colors[jj][(i + k) % len(cfg.colors[jj])],
                        label=label,
                    )
                    if len(hist) > 1:
                        xnorm = np.linspace(bins[0], bins[-1], 1000)
                        if hist[1] == "norm":
                            norm_pdf = norm.pdf(xnorm, mean, std)
                            norm_max = np.max(norm_pdf)
                            if norm_max > 0:
                                axis.plot(
                                    xnorm,
                                    np.max(counts) * norm_pdf / norm_max,
                                    color=cfg.colors[jj][(i + k) % len(cfg.colors[jj])],
                                )
                        elif hist[1] == "lognorm":
                            if mean > 0:
                                a = 1 + (std / mean) ** 2
                                s = np.sqrt(np.log(a))
                                scale = mean / np.sqrt(a)
                                dist = lognorm(s, 0, scale)
                                dist_pdf = dist.pdf(xnorm)
                                dist_max = np.max(dist_pdf)
                                plopm_info(
                                    f"distribution: "
                                    f"{cli_info_value(f'lognorm({s:.6E}, 0, {scale:.6E})')}"
                                )
                                if dist_max > 0:
                                    axis.plot(
                                        xnorm,
                                        np.max(counts) * dist_pdf / dist_max,
                                        color=cfg.colors[jj][
                                            (i + k) % len(cfg.colors[jj])
                                        ],
                                    )
                else:
                    axis.plot(
                        time,
                        var,
                        color=cfg.colors[jj][i % len(cfg.colors[jj])],
                        ls=cfg.linestyle[jj][i % len(cfg.linestyle[jj])],
                        label=label,
                        lw=float(cfg.linewidth[jj][i]),
                    )
                min_t, max_t, min_v, max_v = _update_limits(
                    time, var, tunit, min_t, max_t, min_v, max_v, xlow, ylow, i == 0
                )
        axis.set_ylabel(quan + vunit)
        if not cfg.histogram[0]:
            if min_v != max_v:
                axis.set_ylim([min_v, max_v])
        else:
            axis.set_ylabel("Histogram of " + quan + vunit)
        if not cfg.remove_duplicate_labels or k + int(cfg.subplot_grid[1]) >= len(
            cfg.variables
        ):
            axis.set_xlabel(tunit)
            if cfg.xlabel[0]:
                axis.set_xlabel(cfg.xlabel[j])
        if cfg.ylabel[0]:
            axis.set_ylabel(cfg.ylabel[j])
        xlabels = np.empty(0)
        ylabels = np.empty(0)
        if len(cfg.xlim[0]) > 1:
            axis.set_xlim([float(cfg.xlim[j][0][1:]), float(cfg.xlim[j][1][:-1])])
            xlabels = np.linspace(
                float(cfg.xlim[j][0][1:]),
                float(cfg.xlim[j][1][:-1]),
                int(cfg.xtick_count[j]),
            )
        elif tunit != "Dates" and not cfg.histogram[0]:
            if min_v != max_v:
                axis.set_xlim([min_t, max_t])
            xlabels = np.linspace(min_t, max_t, int(cfg.xtick_count[j]))
        if len(cfg.ylim[0]) > 1:
            axis.set_ylim([float(cfg.ylim[j][0][1:]), float(cfg.ylim[j][1][:-1])])
            ylabels = np.linspace(
                float(cfg.ylim[j][0][1:]),
                float(cfg.ylim[j][1][:-1]),
                int(cfg.ytick_count[j]),
            )
        elif not cfg.histogram[0]:
            if min_v != max_v:
                axis.set_ylim([min_v, max_v])
            ylabels = np.linspace(min_v, max_v, int(cfg.ytick_count[j]))
        if cfg.xlog[j] == "1":
            axis.set_xscale("log")
        else:
            if tunit != "Dates":
                if cfg.xformat[0]:
                    _set_formatted_ticks(axis, xlabels, cfg.xformat[j], "x")
                elif not cfg.histogram[0]:
                    axis.set_xticks(xlabels)
        if cfg.ylog[j] == "1":
            axis.set_yscale("log")
        else:
            if cfg.yformat[0]:
                _set_formatted_ticks(axis, ylabels, cfg.yformat[j], "y")
            elif not cfg.histogram[0]:
                axis.set_yticks(ylabels)
        if cfg.legend_location[j] != "empty":
            axis.legend(loc=cfg.legend_location[j])
        if cfg.title[j] != "0" and cfg.hide_map_elements[3] == 0:
            axis.set_title(cfg.title[j])
        if cfg.remove_duplicate_labels and k + int(cfg.subplot_grid[1]) < len(
            cfg.variables
        ):
            axis.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
        if len(cfg.variables) == len(cfg.cases[0]) and not cfg.subplot_grid[0]:
            if cfg.csv:
                generated_files.append(_save_summary_csv(cfg, deckn, var, quan, j))
                return generated_files
            generated_files.append(_save_summary_png(cfg, deckn, quan, j, fig))
            return generated_files
        if (
            not cfg.subplot_grid[0] and len(cfg.variables) != len(cfg.cases[0])
        ) or j == len(cfg.variables) - 1:
            if (
                len(cfg.legend_location) == j + 2
                and j != 0
                and len(axes.flat) - len(cfg.variables) > 0
            ):
                for jj, qua in enumerate(cfg.variables[: cfg.ncolors]):
                    for i, name in enumerate(cfg.cases[jj]):
                        time, var, tunit, vunit = read_series(
                            cfg,
                            name,
                            qua,
                            cfg.time_units[jj],
                            float(cfg.scale_factor[jj]),
                            i,
                        )
                        label = _get_label(cfg, name, jj, i)
                        if cfg.sensor or cfg.layer or cfg.distance[0]:
                            axes.flat[-1].plot(
                                time,
                                var,
                                color=cfg.colors[jj][i],
                                ls=cfg.linestyle[jj][i],
                                label=label,
                                lw=float(cfg.linewidth[jj][i]),
                            )
                        else:
                            axes.flat[-1].step(
                                time,
                                var,
                                color=cfg.colors[jj][i],
                                ls=cfg.linestyle[jj][i],
                                label=label,
                                lw=float(cfg.linewidth[jj][i]),
                            )
                axes.flat[-1].axis("off")
                axes.flat[-1].legend(loc=cfg.legend_location[-1])
                for line in axes.flat[-1].get_lines():
                    line.remove()
                for o in range(len(axes.flat) - len(cfg.variables) - 1):
                    fig.delaxes(axes.flat[-2 - o])
            else:
                for o in range(len(axes.flat) - len(cfg.variables)):
                    fig.delaxes(axes.flat[-1 - o])
            generated_files.append(_save_summary_png(cfg, deckn, quan, j, fig))
    plt.close()
    return list(dict.fromkeys(generated_files))


def _clean_name(name: str) -> str:
    """Convert a variable expression to a filename-safe stem.

    Parameters
    ----------
    name : str
        Variable expression or proposed filename stem.

    Returns
    -------
    str
        Name with operators and separators replaced.

    """
    name = name.replace(" / ", "_over_")
    name = name.replace(" ", "")
    name = name.replace(":", "-")
    return name


def _get_deck_name(name: str) -> str:
    """Get a display name from a case or include-file path.

    Parameters
    ----------
    name : str
        Case path or include filename.

    Returns
    -------
    str
        Lowercase basename without an ``.inc`` extension.

    """
    deckn = name.split("/")[-1].lower()
    if ".inc" in deckn:
        deckn = deckn[:-4]
    return deckn


def _get_label(cfg: PlopmConfig, name: str, var_index: int, name_index: int) -> str:
    """Select the legend label for a plotted series.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized configuration containing ensemble cases and plot styles.
    name : str
        Simulation-case path.
    var_index : int
        Index of the plotted variable.
    name_index : int
        Index of the case within the variable group.

    Returns
    -------
    str
        User-defined label or a label derived from the case path.

    """
    label = name
    if len(name.split("/")) > 1:
        label = name.split("/")[-2] + "/" + name.split("/")[-1]
    if cfg.legend_labels[0][0]:
        label = cfg.legend_labels[var_index][name_index]
    return label


def _update_limits(
    time: NDArray,
    var: NDArray,
    tunit: str,
    min_t: float,
    max_t: float,
    min_v: float,
    max_v: float,
    xlow: float,
    ylow: float,
    first: bool,
) -> tuple[float, float, float, float]:
    """Update the data limits from one plotted series.

    Parameters
    ----------
    time, var : np.ndarray
        Time coordinates and variable values.
    tunit : str
        Time-axis label. ``"Dates"`` selects date handling.
    min_t, max_t : float
        Current time limits.
    min_v, max_v : float
        Current variable limits.
    xlow, ylow : float
        Lower bounds used to exclude invalid logarithmic values.
    first : bool
        Whether this is the first series included in the limits.

    Returns
    -------
    tuple[float, float, float, float]
        Updated ``(min_t, max_t, min_v, max_v)`` limits.

    """
    valid_var = var[var > ylow]
    valid_time = time[time > xlow] if tunit != "Dates" else time
    if valid_var.size == 0:
        current_min_v = min_v if not first else 0
    else:
        current_min_v = np.min(valid_var)
    current_max_v = np.nanmax(var) if np.any(~np.isnan(var)) else max_v
    current_max_t = np.max(time)
    if tunit != "Dates":
        current_min_t = np.min(valid_time) if valid_time.size > 0 else min_t
    else:
        current_min_t = time[0]
    if first:
        return current_min_t, current_max_t, current_min_v, current_max_v
    return (
        min(min_t, current_min_t),
        max(max_t, current_max_t),
        min(min_v, current_min_v),
        max(max_v, current_max_v),
    )


def _set_formatted_ticks(
    axis: Axes, labels: NDArray, value_format: str, axis_name: str
) -> None:
    """Set explicitly formatted ticks on one axis.

    Parameters
    ----------
    axis : matplotlib.axes.Axes
        Axis to update.
    labels : np.ndarray
        Numeric tick locations.
    value_format : str
        Python format specification for each label.
    axis_name : {"x", "y"}
        Coordinate axis to update.

    """
    formatted_labels = [format(value, value_format) for value in labels]
    ticks = [float(label) for label in formatted_labels]
    if axis_name == "x":
        axis.set_xticks(ticks)
        axis.set_xticklabels(formatted_labels)
    else:
        axis.set_yticks(ticks)
        axis.set_yticklabels(formatted_labels)


def _save_summary_csv(
    cfg: PlopmConfig, deckn: str, var: NDArray, quan: str, index: int
) -> str:
    """Write non-NaN summary values to a CSV file.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized configuration containing ensemble cases and plot styles.
    deckn : str
        Case name used in the default filename.
    var : np.ndarray
        Values to write.
    quan : str
        Variable expression used in the default filename.
    index : int
        Plot index used to select a custom filename.

    Returns
    -------
    str
        Name of the generated CSV file.

    """
    text = [f"{val}\n" for val in var if not np.isnan(val)]
    name = _clean_name(f"{deckn}_{quan}")
    if cfg.filename[index]:
        name = cfg.filename[index]
    filename = f"{name}.csv"
    with open(
        os.path.join(cfg.output_dir, filename),
        "w",
        encoding="utf8",
    ) as file:
        file.write("".join(text))
    return filename


def _save_summary_png(
    cfg: PlopmConfig,
    deckn: str,
    quan: str,
    index: int,
    fig: Figure,
) -> str:
    """Save a summary figure as a PNG file.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized configuration containing ensemble cases and plot styles.
    deckn : str
        Case name used in the default filename.
    quan : str
        Variable expression used in the default filename.
    index : int
        Plot index used to select filename and resolution settings.
    fig : matplotlib.figure.Figure
        Figure to save.

    Returns
    -------
    str
        Name of the generated PNG file.

    """
    name = _clean_name(f"{deckn}_{quan}")
    filename = f"{cfg.filename[index] if cfg.filename[index] else name}.png"
    fig.savefig(
        os.path.join(cfg.output_dir, filename),
        bbox_inches="tight",
        dpi=int(cfg.dpi[index]),
    )
    return filename


def _plot_ensemble(
    cfg: PlopmConfig, axes: Axes | np.ndarray
) -> tuple[str, str, float, float, float, float]:
    """Plot ensemble statistics for the first requested variable.

    Each realization is interpolated to a shared coordinate array. Depending on
    ``cfg.ensemble``, the function plots the mean, a one-standard-deviation band,
    the bounding realizations, or both.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized configuration containing ensemble cases and plot styles.
    axes : matplotlib.axes.Axes or np.ndarray
        Axis, or array of axes, on which to draw the ensemble.

    Returns
    -------
    tuple[str, str, float, float, float, float]
        Time unit, value unit, and ``(min_t, max_t, min_v, max_v)`` limits.

    """
    axis = axes if isinstance(axes, Axes) else np.ravel(axes)[0]
    thetime, timeeval = np.array([0]), np.array([0])
    min_v, max_v = np.inf, -np.inf
    hyst = 1
    var_name = cfg.variables[0]
    if (
        var_name[:3] in ["krw", "krg"]
        or var_name[:4]
        in [
            "krow",
            "krog",
            "pcow",
            "pcog",
            "pcwg",
        ]
        and var_name[-1] == "h"
    ):
        hyst = 2
    for hyst_index in range(hyst):
        for names_index, names in enumerate(cfg.cases):
            label = cfg.case_labels[0][names_index] + " (mean)"
            if len(label.split("/")) > 1:
                label = label.split("/")[-2] + "/" + label.split("/")[-1]
            if cfg.legend_labels[0][0]:
                label = cfg.legend_labels[names_index][0]
            tmp = []
            for name_index, name in enumerate(names):
                time, var, tunit, vunit = read_series(
                    cfg,
                    name,
                    var_name,
                    cfg.time_units[0],
                    float(cfg.scale_factor[0]),
                    name_index,
                )
                rng = int(1.0 * len(time) / hyst)
                time = time[hyst_index * rng : (hyst_index + 1) * rng]
                var = var[hyst_index * rng : (hyst_index + 1) * rng]
                if time.size > thetime.size:
                    thetime = time.copy()
                if tunit == "Dates":
                    time = np.array([value.timestamp() for value in time], dtype=float)
                    if time.size > timeeval.size:
                        timeeval = time.copy()
                else:
                    timeeval = thetime
                tmp.append(interp1d(time, var, bounds_error=False))
            values = np.array([value(timeeval) for value in tmp])
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="Mean of empty slice")
                warnings.filterwarnings("ignore", message="Degrees of freedom <= 0")
                means = np.nanmean(values, axis=0)
                stdev = np.nanstd(values, axis=0)
            plot_label = label if hyst_index == hyst - 1 else None
            axis.plot(
                thetime,
                means,
                color=cfg.colors[0][names_index],
                ls=cfg.linestyle[0][names_index],
                label=plot_label,
                lw=float(cfg.linewidth[0][names_index]),
            )
            if cfg.ensemble in [1, 3]:
                if cfg.fill_between_style:
                    band_properties = cfg.fill_between_style.split(",")
                    color = band_properties[2 * names_index]
                    alpha = float(band_properties[2 * names_index + 1])
                else:
                    color = cfg.colors[0][names_index]
                    alpha = 0.2
                lower_band = means - stdev
                upper_band = means + stdev
                axis.fill_between(
                    thetime, lower_band, upper_band, color=color, alpha=alpha
                )
                if np.any(~np.isnan(lower_band)):
                    min_v = min(min_v, np.nanmin(lower_band))
                if np.any(~np.isnan(upper_band)):
                    max_v = max(max_v, np.nanmax(upper_band))
            if cfg.ensemble in [2, 3]:
                ensemble_index = len(cfg.cases) + names_index
                maxs = np.nansum(values + means, axis=1)
                mins = np.nansum(values - means, axis=1)
                maxs = np.where(maxs == np.max(maxs))[0][0]
                mins = np.where(mins == np.min(mins))[0][0]
                labell = names[mins] + " (lower)"
                labelu = names[maxs] + " (upper)"
                if cfg.legend_labels[0][0]:
                    labell = cfg.legend_labels[names_index][1]
                    labelu = cfg.legend_labels[names_index][2]
                lower_label = labell if hyst_index == hyst - 1 else None
                upper_label = labelu if hyst_index == hyst - 1 else None
                axis.plot(
                    thetime,
                    values[mins],
                    color=cfg.colors[0][ensemble_index],
                    ls=cfg.linestyle[0][ensemble_index],
                    label=lower_label,
                    lw=float(cfg.linewidth[0][names_index]),
                )
                axis.plot(
                    thetime,
                    values[maxs],
                    color=cfg.colors[0][ensemble_index],
                    ls=cfg.linestyle[0][ensemble_index],
                    label=upper_label,
                    lw=float(cfg.linewidth[0][names_index]),
                )
                if np.any(~np.isnan(values[mins])):
                    min_v = min(min_v, np.nanmin(values[mins]))
                if np.any(~np.isnan(values[maxs])):
                    max_v = max(max_v, np.nanmax(values[maxs]))
    min_t, max_t = thetime[0], thetime[-1]
    return tunit, vunit, min_t, max_t, min_v, max_v
