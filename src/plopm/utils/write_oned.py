# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W3301,W0123,R0912,R0915,R0914,R1702,W0611,R0913,R0917,C0302,C0115,R0916,E1102

"""Utiliy functions to write the PNGs figures"""

from typing import Union
import warnings
import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from scipy.interpolate import interp1d
from scipy.stats import norm, lognorm
from plopm.utils.readers import read_oned
from plopm.config.config import ConfigPlopm


def make_plots(cfg: ConfigPlopm) -> None:
    """Plot the one dimensional variables"""

    def clean_name(name: str) -> str:
        name = name.replace(" / ", "_over_")
        name = name.replace(" ", "")
        name = name.replace(":", "-")
        return name

    def get_deck_name(name: str) -> str:
        deckn = name.split("/")[-1].lower()
        if ".inc" in deckn:
            deckn = deckn[:-4]
        return deckn

    def get_label(name: str, var_index: int, name_index: int) -> str:
        label = name
        if len(name.split("/")) > 1:
            label = name.split("/")[-2] + "/" + name.split("/")[-1]
        if cfg.labels[0][0]:
            label = cfg.labels[var_index][name_index]
        return label

    def update_limits(
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

    def set_formatted_ticks(
        axis: Axes, labels: NDArray, value_format: str, axis_name: str
    ) -> None:
        formatted_labels = [format(value, value_format) for value in labels]
        ticks = [float(label) for label in formatted_labels]
        if axis_name == "x":
            axis.set_xticks(ticks)
            axis.set_xticklabels(formatted_labels)
        else:
            axis.set_yticks(ticks)
            axis.set_yticklabels(formatted_labels)

    def save_summary_csv(deckn: str, var: NDArray, quan: str, index: int) -> None:
        text = [f"{val}\n" for val in var if not np.isnan(val)]
        name = clean_name(f"{deckn}_{quan}")
        if cfg.save[index]:
            name = cfg.save[index]
        with open(f"{cfg.output}/{name}.csv", "w", encoding="utf8") as file:
            file.write("".join(text))

    def save_summary_png(deckn: str, quan: str, index: int, fig: Figure) -> None:
        name = clean_name(f"{deckn}_{quan}")
        fig.savefig(
            f"{cfg.output}/{cfg.save[index] if cfg.save[index] else name}.png",
            bbox_inches="tight",
            dpi=int(cfg.dpi[index]),
        )

    deckn = get_deck_name(cfg.names[0][0])
    fig, _ = plt.subplots(1, 1)
    if cfg.subfigs[0]:
        plt.close()
        fig, axiss = plt.subplots(
            int(cfg.subfigs[0]), int(cfg.subfigs[1]), layout="compressed"
        )
    for j, quan in enumerate(cfg.vrs):
        k = j
        if not cfg.subfigs[0]:
            plt.close()
            fig, axiss = plt.subplots(1, 1, layout="compressed")
            axiss = np.array([axiss])
            k = 0
        axis = axiss.flat[k]
        axis.grid(int(cfg.axgrid[j]))
        if cfg.ensemble > 0:
            tunit, vunit, min_t, max_t, min_v, max_v = handle_ensemble(cfg, axiss)
        else:
            ylow = 0 if cfg.ylog[j] == "1" else -np.inf
            xlow = 0 if cfg.xlog[j] == "1" else -np.inf
            min_t, max_t, min_v, max_v = 0, 0, 0, 0
            for i, name in enumerate(cfg.names[j]):
                jj = j
                if len(cfg.vrs) == len(cfg.names[0]) and not cfg.subfigs[0]:
                    jj = i
                    quan = cfg.vrs[i]
                time, var, tunit, vunit = read_oned(
                    cfg, name, quan, cfg.tunits[jj], float(cfg.adjust[jj]), i
                )
                label = get_label(name, jj, i)
                use_line_plot = (
                    cfg.sensor
                    or cfg.layer
                    or cfg.distance[0]
                    or quan[:3] in ["krw", "krg"]
                    or quan[:4] in ["krow", "krog", "pcow", "pcog", "pcwg"]
                    or quan[:6] == "pcfact"
                )
                if use_line_plot:
                    axis.plot(
                        time,
                        var,
                        color=cfg.colors[jj][i % len(cfg.colors[jj])],
                        ls=cfg.linestyle[jj][i % len(cfg.linestyle[jj])],
                        label=label,
                        lw=float(cfg.lw[jj][i]),
                    )
                elif cfg.histogram[0]:
                    ij = i + j * len(cfg.names[j])
                    if len(cfg.vrs) == len(cfg.names[0]) and not cfg.subfigs[0]:
                        ij = i
                    hist = cfg.histogram[ij].split(",")
                    mean = np.nanmean(var)
                    std = np.nanstd(var)
                    print(f"Histogram: mean={mean:.6E}, std={std:.6E}")
                    if not cfg.labels[0][0]:
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
                                print(f"Distribution: lognorm({s:.6E}, 0, {scale:.6E})")
                                if dist_max > 0:
                                    axis.plot(
                                        xnorm,
                                        np.max(counts) * dist_pdf / dist_max,
                                        color=cfg.colors[jj][
                                            (i + k) % len(cfg.colors[jj])
                                        ],
                                    )
                else:
                    axis.step(
                        time,
                        var,
                        color=cfg.colors[jj][i % len(cfg.colors[jj])],
                        ls=cfg.linestyle[jj][i % len(cfg.linestyle[jj])],
                        label=label,
                        lw=float(cfg.lw[jj][i]),
                    )
                min_t, max_t, min_v, max_v = update_limits(
                    time, var, tunit, min_t, max_t, min_v, max_v, xlow, ylow, i == 0
                )
        axis.set_ylabel(quan + vunit)
        if not cfg.histogram[0]:
            if min_v != max_v:
                axis.set_ylim([min_v, max_v])
        else:
            axis.set_ylabel("Histogram of " + quan + vunit)
        if not cfg.delax or k + int(cfg.subfigs[1]) >= len(cfg.vrs):
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
                int(cfg.xlnum[j]),
            )
        elif tunit != "Dates" and not cfg.histogram[0]:
            if min_v != max_v:
                axis.set_xlim([min_t, max_t])
            xlabels = np.linspace(min_t, max_t, int(cfg.xlnum[j]))
        if len(cfg.ylim[0]) > 1:
            axis.set_ylim([float(cfg.ylim[j][0][1:]), float(cfg.ylim[j][1][:-1])])
            ylabels = np.linspace(
                float(cfg.ylim[j][0][1:]),
                float(cfg.ylim[j][1][:-1]),
                int(cfg.ylnum[j]),
            )
        elif not cfg.histogram[0]:
            if min_v != max_v:
                axis.set_ylim([min_v, max_v])
            ylabels = np.linspace(min_v, max_v, int(cfg.ylnum[j]))
        if cfg.xlog[j] == "1":
            axis.set_xscale("log")
        else:
            if tunit != "Dates":
                if cfg.xformat[0]:
                    set_formatted_ticks(axis, xlabels, cfg.xformat[j], "x")
                elif not cfg.histogram[0]:
                    axis.set_xticks(xlabels)
        if cfg.ylog[j] == "1":
            axis.set_yscale("log")
        else:
            if cfg.yformat[0]:
                set_formatted_ticks(axis, ylabels, cfg.yformat[j], "y")
            elif not cfg.histogram[0]:
                axis.set_yticks(ylabels)
        if cfg.loc[j] != "empty":
            axis.legend(loc=cfg.loc[j])
        if cfg.title[j] != "0" and cfg.rm[3] == 0:
            axis.set_title(cfg.title[j])
        if cfg.delax and k + int(cfg.subfigs[1]) < len(cfg.vrs):
            axis.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
        if len(cfg.vrs) == len(cfg.names[0]) and not cfg.subfigs[0]:
            if cfg.csv:
                save_summary_csv(deckn, var, quan, j)
                return
            save_summary_png(deckn, quan, j, fig)
            return
        if (not cfg.subfigs[0] and len(cfg.vrs) != len(cfg.names[0])) or j == len(
            cfg.vrs
        ) - 1:
            if len(cfg.loc) == j + 2 and j != 0 and len(axiss.flat) - len(cfg.vrs) > 0:
                for jj, qua in enumerate(cfg.vrs[: cfg.numc]):
                    for i, name in enumerate(cfg.names[jj]):
                        time, var, tunit, vunit = read_oned(
                            cfg, name, qua, cfg.tunits[jj], float(cfg.adjust[jj]), i
                        )
                        label = get_label(name, jj, i)
                        if cfg.sensor or cfg.layer or cfg.distance[0]:
                            axiss.flat[-1].plot(
                                time,
                                var,
                                color=cfg.colors[jj][i],
                                ls=cfg.linestyle[jj][i],
                                label=label,
                                lw=float(cfg.lw[jj][i]),
                            )
                        else:
                            axiss.flat[-1].step(
                                time,
                                var,
                                color=cfg.colors[jj][i],
                                ls=cfg.linestyle[jj][i],
                                label=label,
                                lw=float(cfg.lw[jj][i]),
                            )
                axiss.flat[-1].axis("off")
                axiss.flat[-1].legend(loc=cfg.loc[-1])
                for line in axiss.flat[-1].get_lines():
                    line.remove()
                for o in range(len(axiss.flat) - len(cfg.vrs) - 1):
                    fig.delaxes(axiss.flat[-2 - o])
            else:
                for o in range(len(axiss.flat) - len(cfg.vrs)):
                    fig.delaxes(axiss.flat[-1 - o])
            save_summary_png(deckn, quan, j, fig)
    plt.close()


def handle_ensemble(
    cfg: ConfigPlopm, axiss: Union[Axes, np.ndarray]
) -> tuple[str, str, float, float, float, float]:
    """Compute the mean and create the band"""
    axis = axiss if isinstance(axiss, Axes) else np.ravel(axiss)[0]
    thetime, timeeval = np.array([0]), np.array([0])
    min_v, max_v = np.inf, -np.inf
    hyst = 1
    var_name = cfg.vrs[0]
    if var_name[:3] in ["krw", "krg"] or var_name[:4] in [
        "krow",
        "krog",
        "pcow",
        "pcog",
        "pcwg",
    ]:
        if var_name[-1] == "h":
            hyst = 2
    for hyst_index in range(hyst):
        for names_index, names in enumerate(cfg.names):
            label = cfg.namens[0][names_index] + " (mean)"
            if len(label.split("/")) > 1:
                label = label.split("/")[-2] + "/" + label.split("/")[-1]
            if cfg.labels[0][0]:
                label = cfg.labels[names_index][0]
            tmp = []
            for name_index, name in enumerate(names):
                time, var, tunit, vunit = read_oned(
                    cfg,
                    name,
                    var_name,
                    cfg.tunits[0],
                    float(cfg.adjust[0]),
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
                lw=float(cfg.lw[0][names_index]),
            )
            if cfg.ensemble in [1, 3]:
                if cfg.bandprop:
                    band_properties = cfg.bandprop.split(",")
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
                ensemble_index = len(cfg.names) + names_index
                maxs = np.nansum(values + means, axis=1)
                mins = np.nansum(values - means, axis=1)
                maxs = np.where(maxs == np.max(maxs))[0][0]
                mins = np.where(mins == np.min(mins))[0][0]
                labell = names[mins] + " (lower)"
                labelu = names[maxs] + " (upper)"
                if cfg.labels[0][0]:
                    labell = cfg.labels[names_index][1]
                    labelu = cfg.labels[names_index][2]
                lower_label = labell if hyst_index == hyst - 1 else None
                upper_label = labelu if hyst_index == hyst - 1 else None
                axis.plot(
                    thetime,
                    values[mins],
                    color=cfg.colors[0][ensemble_index],
                    ls=cfg.linestyle[0][ensemble_index],
                    label=lower_label,
                    lw=float(cfg.lw[0][names_index]),
                )
                axis.plot(
                    thetime,
                    values[maxs],
                    color=cfg.colors[0][ensemble_index],
                    ls=cfg.linestyle[0][ensemble_index],
                    label=upper_label,
                    lw=float(cfg.lw[0][names_index]),
                )
                if np.any(~np.isnan(values[mins])):
                    min_v = min(min_v, np.nanmin(values[mins]))
                if np.any(~np.isnan(values[maxs])):
                    max_v = max(max_v, np.nanmax(values[maxs]))
    min_t, max_t = thetime[0], thetime[-1]
    return tunit, vunit, min_t, max_t, min_v, max_v
