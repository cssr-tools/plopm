# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W3301,W0123,R0912,R0915,R0914,R1702,W0611,R0913,R0917,C0302,C0115,R0916,E1102

"""Create two-dimensional maps and animations from OPM results.

The module prepares grid geometry, maps three-dimensional properties onto
selected slices, and writes PNG or GIF output with optional masks, differences,
well and fault overlays, and shared color limits.
"""

import datetime
import sys
from collections.abc import Iterable
from contextlib import nullcontext
from typing import Any

import colorcet  # noqa: F401  # registers colorcet colormaps with matplotlib
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from alive_progress import alive_bar
from matplotlib import animation, colors
from matplotlib.animation import FuncAnimation, writers
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.figure import Figure
from matplotlib.ticker import LogFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.axes_divider import AxesDivider
from numpy.typing import NDArray

from plopm.config.config import PlopmConfig, SimData
from plopm.utils.mapping import (
    get_xy_slice,
    get_xz_slice,
    get_yz_slice,
    map_xy,
    map_xz,
    map_yz,
    transform_grid,
)
from plopm.utils.readers import (
    get_faults,
    get_wells,
    read_case,
    read_csv_grid,
    read_quantity,
    time_unit,
)
from plopm.utils.terminal import cli_error_value, plopm_error


def make_maps(cfg: PlopmConfig) -> list[str]:
    """Create the requested spatial maps and animations.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized map configuration.

    Returns
    -------
    list[str]
        Names of the generated PNG and GIF files.

    """
    generated_files: list[str] = []
    skip = 0
    if (
        cfg.subplot_grid[0]
        and len(cfg.variables) > 1
        and len(cfg.restart) == 1
        and len(cfg.cases[0]) == 1
    ):
        skip = 1
    if cfg.subplot_grid[0]:
        fig, axis = _create_figure(int(cfg.subplot_grid[0]), int(cfg.subplot_grid[1]))
        sub1 = int(cfg.subplot_grid[1])
    else:
        fig, axis = _create_figure(1, 1, "compressed")
        sub1 = 1
    if cfg.subplot_grid[0] and cfg.gif and len(cfg.cases[0]) > 1:
        _, _, _, cmin, cmax, diffa = _get_clim(cfg)
        maska = _get_masks(cfg) if cfg.mask_variable else []
        deckd = _case_name(cfg.difference_input) if cfg.difference_input else ""
        fig, axis = _create_figure(
            int(cfg.subplot_grid[0]), int(cfg.subplot_grid[1]), "compressed"
        )
        axes = _normalize_axis(axis)
        data, xc, yc, named, slice_title, slice_name, mx, my, xname, yname = (
            _prepare_map(cfg, cfg.cases[0][0], 0)
        )
        original_loc, cb = _prepare_colorbars(axes)
        _delete_extra_axes(axes, len(cfg.cases[0]), fig)
        im_ani = animation.FuncAnimation(
            fig,
            _draw_frame,
            fargs=(
                cfg.cases[0][0],
                fig,
                axes,
                original_loc,
                cb,
                cmin,
                cmax,
                maska,
                diffa,
                named,
                deckd,
                slice_title,
                slice_name,
                cfg,
                generated_files,
                0,
                data,
                xc,
                yc,
                skip,
                sub1,
                mx,
                my,
                xname,
                yname,
            ),
            frames=len(data.steps),
            interval=cfg.gif_interval,
            blit=False,
            repeat=False,
        )
        generated_files.append(
            _save_animation(
                cfg, im_ani, cfg.filename[0] if cfg.filename[0] else cfg.variables[0]
            )
        )
    elif cfg.subplot_grid[0] and cfg.gif and len(cfg.variables) > 1:
        data, xc, yc, cmin, cmax, diffa = _get_clim(cfg)
        deckd = _case_name(cfg.difference_input) if cfg.difference_input else ""
        data, xc, yc, named, slice_title, slice_name, mx, my, xname, yname = (
            _prepare_map(cfg, cfg.cases[0][0], 0)
        )
        maska = _get_masks(cfg) if cfg.mask_variable else []
        if len(data.steps) > 1:
            fig, axis = _create_figure(
                int(cfg.subplot_grid[0]), int(cfg.subplot_grid[1])
            )
        axes = _normalize_axis(axis)
        plt.tight_layout(pad=1.7)
        original_loc, cb = _prepare_colorbars(axes)
        _delete_extra_axes(axes, len(cfg.variables), fig)
        im_ani = animation.FuncAnimation(
            fig,
            _draw_frame,
            fargs=(
                cfg.cases[0][0],
                fig,
                axes,
                original_loc,
                cb,
                cmin,
                cmax,
                maska,
                diffa,
                named,
                deckd,
                slice_title,
                slice_name,
                cfg,
                generated_files,
                0,
                data,
                xc,
                yc,
                skip,
                sub1,
                mx,
                my,
                xname,
                yname,
            ),
            frames=len(data.steps),
            interval=cfg.gif_interval,
            blit=False,
            repeat=False,
        )
        generated_files.append(
            _save_animation(cfg, im_ani, cfg.filename[0] if cfg.filename[0] else named)
        )
    else:
        _, _, _, cmin, cmax, diffa = _get_clim(cfg)
        maska = _get_masks(cfg) if cfg.mask_variable else []
        deckd = _case_name(cfg.difference_input) if cfg.difference_input else ""
        data, xc, yc, named, slice_title, slice_name, mx, my, xname, yname = (
            _prepare_map(cfg, cfg.cases[0][0], 0)
        )
        for n, var in enumerate(cfg.variables):
            if len(data.steps) > 1:
                if cfg.subplot_grid[0]:
                    fig, axis = _create_figure(
                        int(cfg.subplot_grid[0]), int(cfg.subplot_grid[1])
                    )
                else:
                    fig, axis = _create_figure(1, 1)
            if not cfg.subplot_grid[0] and not cfg.gif:
                plt.close()
                fig, axis = _create_figure(1, 1, "tight")
            axes = _normalize_axis(axis)
            original_loc, cb = _prepare_colorbars(axes)
            if len(data.steps) > 1:
                _delete_extra_axes(axes, len(data.steps), fig)
            if cfg.gif and len(data.steps) > 1:
                im_ani = animation.FuncAnimation(
                    fig,
                    _draw_frame,
                    fargs=(
                        cfg.cases[0][0],
                        fig,
                        axes,
                        original_loc,
                        cb,
                        cmin,
                        cmax,
                        maska,
                        diffa,
                        named,
                        deckd,
                        slice_title,
                        slice_name,
                        cfg,
                        generated_files,
                        n,
                        data,
                        xc,
                        yc,
                        skip,
                        sub1,
                        mx,
                        my,
                        xname,
                        yname,
                    ),
                    frames=len(data.steps),
                    interval=cfg.gif_interval,
                    blit=False,
                    repeat=False,
                )
                name = f"{cfg.filename[0] if cfg.filename[0] else named + '_' + var}"
                generated_files.append(_save_animation(cfg, im_ani, name))
            else:
                if len(cfg.cases[0]) > 1:
                    _delete_extra_axes(axes, len(cfg.cases[0]), fig)
                if len(data.steps) > 1 and len(cfg.cases[0]) == len(data.steps):
                    if not cfg.subplot_grid[0]:
                        fig, axis = _create_figure(1, 1)
                        axes = _normalize_axis(axis)
                        original_loc, cb = _prepare_colorbars(axes)
                    _draw_frame(
                        0,
                        cfg.cases[0][0],
                        fig,
                        axes,
                        original_loc,
                        cb,
                        cmin,
                        cmax,
                        maska,
                        diffa,
                        named,
                        deckd,
                        slice_title,
                        slice_name,
                        cfg,
                        generated_files,
                        n,
                        data,
                        xc,
                        yc,
                        skip,
                        sub1,
                        mx,
                        my,
                        xname,
                        yname,
                    )
                else:
                    for t, _ in enumerate(data.steps):
                        if not cfg.subplot_grid[0]:
                            plt.close()
                            fig, axis = _create_figure(1, 1)
                            axes = _normalize_axis(axis)
                            original_loc, cb = _prepare_colorbars(axes)
                        _draw_frame(
                            t,
                            cfg.cases[0][0],
                            fig,
                            axes,
                            original_loc,
                            cb,
                            cmin,
                            cmax,
                            maska,
                            diffa,
                            named,
                            deckd,
                            slice_title,
                            slice_name,
                            cfg,
                            generated_files,
                            n,
                            data,
                            xc,
                            yc,
                            skip,
                            sub1,
                            mx,
                            my,
                            xname,
                            yname,
                        )
    return list(dict.fromkeys(generated_files))


def _prepare_map(
    cfg: PlopmConfig, deck: str, n: int
) -> tuple[SimData, NDArray, NDArray, str, str, str, int, int, str, str]:
    """Prepare simulation data and coordinates for one map.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized map configuration.
    deck : str
        Simulation-case stem or CSV input path.
    n : int
        Case or map index used to select configuration values.

    Returns
    -------
    tuple
        Simulation data, coordinate meshes, case and slice labels, mesh
        dimensions, and coordinate-axis names.

    """
    if cfg.csv_columns[n][0]:
        xc, yc, mx, my, xname, yname = read_csv_grid(cfg, deck, n)
        slice_title, slice_name = "", ""
        data = SimData(steps=cfg.restart)
    else:
        data = read_case(
            deck, cfg.gif, cfg.vtk, cfg.variables, cfg.restart, cfg.filters, n
        )
        slide = cfg.slice[n]
        if slide[0][0] != -2:
            xc, yc, slice_title, slice_name, mx, my, xname, yname = get_yz_slice(
                cfg, data, n
            )
        elif slide[1][0] != -2:
            xc, yc, slice_title, slice_name, mx, my, xname, yname = get_xz_slice(
                cfg, data, n
            )
        else:
            xc, yc, slice_title, slice_name, mx, my, xname, yname = get_xy_slice(
                cfg, data, n
            )
    if int(cfg.rotation[n]) != 0 or cfg.translation[n] != ["[0", "0]"]:
        xc, yc = transform_grid(cfg, n, xc, yc)
    return (
        data,
        xc,
        yc,
        deck.rsplit("/", 1)[-1].lower(),
        slice_title,
        slice_name,
        mx,
        my,
        xname,
        yname,
    )


def _create_figure(
    rows: int = 1,
    columns: int = 1,
    layout: str | None = None,
) -> tuple[Figure, Axes]:
    """Create a Matplotlib figure and axes.

    Parameters
    ----------
    rows, columns : int, default: 1
        Number of subplot rows and columns.
    layout : str, optional
        Matplotlib layout engine.

    Returns
    -------
    tuple
        Created figure and axes.

    """
    plt.close()
    if layout:
        fig, axes = plt.subplots(rows, columns, layout=layout)
    else:
        fig, axes = plt.subplots(rows, columns)
    return fig, axes


def _normalize_axis(axes: Axes | NDArray[Any]) -> NDArray:
    """Return axes as a one-dimensional-compatible array.

    Parameters
    ----------
    axes : matplotlib.axes.Axes or np.ndarray
        Axes returned by Matplotlib.

    Returns
    -------
    np.ndarray
        Array containing the supplied axes.

    """
    if isinstance(axes, np.ndarray):
        return axes
    return np.array([axes])


def _prepare_colorbars(axes: NDArray[Any]) -> tuple[list[Any], list[str]]:
    """Initialize colorbar state for each subplot.

    Parameters
    ----------
    axes : np.ndarray
        Subplot axes.

    Returns
    -------
    tuple[list, list]
        Original axes locators and empty colorbar slots.

    """
    original_loc, cb = [], []
    for axis in axes.flat:
        original_loc.append(axis.get_axes_locator())
        cb.append("")
    return original_loc, cb


def _delete_extra_axes(axes: NDArray[Any], keep: int, fig: Figure) -> None:
    """Remove unused subplot axes.

    Parameters
    ----------
    axes : np.ndarray
        Subplot axes.
    keep : int
        Number of axes to retain.
    fig : matplotlib.figure.Figure
        Figure containing the axes.

    """
    for o in range(max(0, len(axes.flat) - keep)):
        axis_to_remove = axes.flat[-1 - o]
        if axis_to_remove in fig.axes:
            fig.delaxes(axis_to_remove)


def _save_animation(cfg: PlopmConfig, im_ani: FuncAnimation, name: str) -> str:
    """Save a Matplotlib animation as a GIF.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized map configuration.
    im_ani : matplotlib.animation.FuncAnimation
        Animation to save.
    name : str
        Output filename without extension.

    Returns
    -------
    str
        Name of the generated GIF file.

    """
    filename = f"{name}.gif"
    output_path = f"{cfg.output_dir}/{filename}"
    if cfg.gif_loop or not writers.is_available("ffmpeg"):
        im_ani.save(output_path)
    else:
        im_ani.save(output_path, extra_args=["-loop", "-1"])
    return filename


def _map_values(
    cfg: PlopmConfig,
    data: SimData,
    var: str,
    values: NDArray,
    slide_index: int,
    map_index: int,
    mx: int,
    my: int,
    use_csv: bool = False,
) -> NDArray:
    """Map quantity values onto the selected two-dimensional slice.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized map configuration.
    data : SimData
        Loaded simulation data.
    var : str
        Variable name.
    values : np.ndarray
        Values in active-cell or CSV order.
    slide_index, map_index : int
        Indices selecting the slice and its mapping settings.
    mx, my : int
        Mapped grid dimensions.
    use_csv : bool, default: False
        Whether values already use the two-dimensional CSV layout.

    Returns
    -------
    np.ndarray
        Values arranged on the selected map.

    """
    if use_csv:
        quaa = np.asarray(values).copy()
    elif cfg.slice[slide_index][0][0] != -2:
        quaa = map_yz(cfg, data, var, values, map_index, mx, my)
    elif cfg.slice[slide_index][1][0] != -2:
        quaa = map_xz(cfg, data, var, values, map_index, mx, my)
    else:
        quaa = map_xy(cfg, data, var, values, map_index, mx, my)
    return quaa


def _get_clim(
    cfg: PlopmConfig,
) -> tuple[SimData, NDArray, NDArray, list[float], list[float], list[NDArray]]:
    """Determine color limits and cached difference maps.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized map configuration.

    Returns
    -------
    tuple
        Last loaded simulation data, coordinate meshes, color minima and
        maxima, and cached difference arrays.

    """
    cmin, cmax = [float("inf")], [float("-inf")]
    diffa: list[NDArray] = []
    xc, yc = np.empty(0), np.empty(0)
    if (cfg.rst_range and cfg.png and not cfg.subplot_grid[0]) or (
        cfg.clim[0][0] and not cfg.difference_input
    ):
        return SimData(), xc, yc, cmin, cmax, diffa

    if cfg.restart[0] == -1 and cfg.gif:
        data = read_case(
            cfg.cases[0][0], cfg.gif, cfg.vtk, cfg.variables, cfg.restart, cfg.filters
        )
    else:
        data = SimData(steps=cfg.restart)
    if cfg.difference_input:
        var = cfg.variables[0]
        for t, _ in enumerate(data.steps):
            data, xc, yc, _, _, _, mx, my, _, _ = _prepare_map(
                cfg, cfg.difference_input, 1
            )
            _, values = read_quantity(
                cfg.difference_input,
                data,
                var,
                data.steps[t],
                float(cfg.scale_factor[0]),
                cfg.mass_vars,
                cfg.mass_vars + cfg.mass_fracs,
                cfg.caprock_vars,
                cfg.stress_coefficient,
                cfg.filters[0],
                cfg.gif,
                cfg.min_threshold[0],
                cfg.max_threshold[0],
                cfg.csv_columns[0],
            )
            quaa = _map_values(cfg, data, var, values, 1, 1, mx, my)
            diffa.append(quaa.copy())
    if len(cfg.variables) == len(cfg.cases[0]) and len(cfg.cases[0]) > 1:
        for m, var in enumerate(cfg.variables):
            cmin.append(cmin[-1])
            cmax.append(cmax[-1])
            for t, _ in enumerate(data.steps):
                data, xc, yc, _, _, _, mx, my, _, _ = _prepare_map(
                    cfg, cfg.cases[0][m], m
                )
                _, values = read_quantity(
                    cfg.cases[0][m],
                    data,
                    var,
                    data.steps[t],
                    float(cfg.scale_factor[m]),
                    cfg.mass_vars,
                    cfg.mass_vars + cfg.mass_fracs,
                    cfg.caprock_vars,
                    cfg.stress_coefficient,
                    cfg.filters[0],
                    cfg.gif,
                    cfg.min_threshold[m],
                    cfg.max_threshold[m],
                    cfg.csv_columns[0],
                )
                quaa = _map_values(cfg, data, var, values, m, m, mx, my)
                _apply_diff_and_log(cfg, diffa, quaa, m, t)
                _update_color_range(quaa, cmin, cmax)
    else:
        for m, var in enumerate(cfg.variables):
            cmin.append(cmin[-1])
            cmax.append(cmax[-1])
            for n, deck in enumerate(cfg.cases[0]):
                for t, _ in enumerate(data.steps):
                    data, xc, yc, _, _, _, mx, my, _, _ = _prepare_map(cfg, deck, n)
                    _, values = read_quantity(
                        deck,
                        data,
                        var,
                        data.steps[t],
                        float(cfg.scale_factor[m]),
                        cfg.mass_vars,
                        cfg.mass_vars + cfg.mass_fracs,
                        cfg.caprock_vars,
                        cfg.stress_coefficient,
                        cfg.filters[n],
                        cfg.gif,
                        cfg.min_threshold[m],
                        cfg.max_threshold[m],
                        cfg.csv_columns[n],
                    )
                    quaa = _map_values(
                        cfg, data, var, values, n, n, mx, my, cfg.csv_columns[n][0]
                    )
                    _apply_diff_and_log(cfg, diffa, quaa, m, t)
                    _update_color_range(quaa, cmin, cmax)
    return data, xc, yc, cmin, cmax, diffa


def _apply_diff_and_log(
    cfg: PlopmConfig,
    diffa: list[NDArray],
    quaa: NDArray,
    var_index: int,
    restart_index: int,
) -> None:
    """Apply difference and logarithmic transformations in place.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized map configuration.
    diffa : list[np.ndarray]
        Mapped difference values.
    quaa : np.ndarray
        Mapped values to transform.
    var_index : int
        Variable index.
    restart_index : int
        Restart-step index used to select a cached difference map.

    """
    if cfg.difference_input:
        quaa -= diffa[restart_index]
    if int(cfg.color_log[var_index]) == 1:
        quaa[quaa <= 0] = np.nan


def _update_color_range(quaa: NDArray, cmin: list[float], cmax: list[float]) -> None:
    """Update the current finite color range.

    Parameters
    ----------
    quaa : np.ndarray
        Mapped values included in the color range.
    cmin : list[float]
        Color minima.
    cmax : list[float]
        Color minima.

    """
    if np.any(~np.isnan(quaa)):
        cmin[-2] = min(cmin[-2], np.nanmin(quaa))
        cmax[-2] = max(cmax[-2], np.nanmax(quaa))


def _get_masks(cfg: PlopmConfig) -> list[NDArray]:
    """Read and map masks for all configured cases.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized map configuration.

    Returns
    -------
    list[np.ndarray]
        Mapped mask arrays.

    """
    maska = []
    var = cfg.mask_variable
    for n, deck in enumerate(cfg.cases[0]):
        data, _, _, _, _, _, mx, my, _, _ = _prepare_map(cfg, deck, n)
        _, values = read_quantity(
            deck,
            data,
            var,
            0,
            float(cfg.scale_factor[0]),
            cfg.mass_vars,
            cfg.mass_vars + cfg.mass_fracs,
            cfg.caprock_vars,
            cfg.stress_coefficient,
            cfg.filters[n],
            cfg.gif,
            cfg.min_threshold[0],
            cfg.max_threshold[0],
            cfg.csv_columns[n],
        )
        maska.append(_map_values(cfg, data, var, values, n, n, mx, my))
    return maska


def _case_name(deck: str) -> str:
    """Get a lowercase case name from a path.

    Parameters
    ----------
    deck : str
        Simulation-case path.

    Returns
    -------
    str
        Final path component in lowercase.

    """
    if len(deck.split("/")) > 1:
        return deck.split("/")[-1].lower()
    return deck.lower()


def _draw_frame(
    t: int,
    deck: str,
    fig: Figure,
    axes: Any,
    original_loc: list[Any],
    cb: list[str],
    cmin: list[float],
    cmax: list[float],
    maska: list[Any],
    diffa: list[NDArray],
    named: str,
    deckd: str,
    slice_title: str,
    slice_name: str,
    cfg: PlopmConfig,
    generated_files: list[str],
    n: int,
    data: SimData,
    xc: NDArray,
    yc: NDArray,
    skip: int,
    sub1: int,
    mx: int,
    my: int,
    xname: str,
    yname: str,
) -> Iterable[Artist]:
    """Draw all maps belonging to one animation frame.

    This dispatcher selects cases, variables, restart steps, and subplot
    positions before delegating each map to :func:`draw_map`.

    Parameters
    ----------
    t : int
        Animation-frame or restart-step index.
    deck : str
        Primary simulation-case stem.
    fig : matplotlib.figure.Figure
        Figure receiving the maps.
    axes : matplotlib.axes.Axes or np.ndarray
        Target axes.
    original_loc, cb : list
        Original axes locators and active colorbars.
    cmin, cmax : list[float]
        Color limits for each variable or map.
    maska, diffa : list
        Mapped masks and cached difference arrays.
    named, deckd : str
        Display names for the primary and difference cases.
    slice_title, slice_name : str
        Human-readable slice descriptions.
    cfg : PlopmConfig
        Initialized map configuration.
    generated_files : list[str]
        Generated filenames updated during rendering.
    n : int
        Current variable or case index.
    data : SimData
        Loaded simulation data.
    xc, yc : np.ndarray
        Coordinate meshes.
    skip, sub1 : int
        Subplot-control values.
    mx, my : int
        Mapped grid dimensions.
    xname, yname : str
        Coordinate-axis names.

    Returns
    -------
    list[matplotlib.artist.Artist]
        Empty artist list required by the animation callback.

    """
    k = t
    if not cfg.subplot_grid[0]:
        k = 0
    elif len(data.steps) == 1:
        k = n
    if cfg.subplot_grid[0] and len(cfg.cases[0]) > 1:
        show_progress = sys.stdout.isatty()
        if show_progress:
            bar_ctx = alive_bar(len(cfg.cases[0]), bar="fish")
        else:
            bar_ctx = nullcontext()
        with bar_ctx as bar_animation:
            if len(cfg.variables) > 1:
                cmax = [np.max(cmax)] * len(cmax)
                cmin = [np.min(cmin)] * len(cmin)
                for nn, deckl in enumerate(cfg.cases[0]):
                    if show_progress:
                        bar_animation()
                    (
                        data,
                        xc,
                        yc,
                        named,
                        slice_title,
                        slice_name,
                        mx,
                        my,
                        xname,
                        yname,
                    ) = _prepare_map(cfg, deckl, nn)
                    _draw_map(
                        deckl,
                        fig,
                        axes,
                        original_loc,
                        cb,
                        cmin,
                        cmax,
                        maska,
                        diffa,
                        named,
                        deckd,
                        slice_title,
                        slice_name,
                        cfg,
                        generated_files,
                        data,
                        t,
                        nn,
                        nn,
                        xc,
                        yc,
                        sub1,
                        mx,
                        my,
                        xname,
                        yname,
                    )
            else:
                for nn, deckl in enumerate(cfg.cases[0]):
                    if show_progress:
                        bar_animation()
                    (
                        data,
                        xc,
                        yc,
                        named,
                        slice_title,
                        slice_name,
                        mx,
                        my,
                        xname,
                        yname,
                    ) = _prepare_map(cfg, deckl, nn)
                    if len(data.steps) > 1 and len(cfg.cases[0]) == len(data.steps):
                        _draw_map(
                            deckl,
                            fig,
                            axes,
                            original_loc,
                            cb,
                            cmin,
                            cmax,
                            maska,
                            diffa,
                            named,
                            deckd,
                            slice_title,
                            slice_name,
                            cfg,
                            generated_files,
                            data,
                            nn,
                            0,
                            nn,
                            xc,
                            yc,
                            sub1,
                            mx,
                            my,
                            xname,
                            yname,
                        )
                    else:
                        _draw_map(
                            deckl,
                            fig,
                            axes,
                            original_loc,
                            cb,
                            cmin,
                            cmax,
                            maska,
                            diffa,
                            named,
                            deckd,
                            slice_title,
                            slice_name,
                            cfg,
                            generated_files,
                            data,
                            t,
                            0,
                            nn,
                            xc,
                            yc,
                            sub1,
                            mx,
                            my,
                            xname,
                            yname,
                        )
    elif cfg.subplot_grid[0] and len(cfg.variables) > 1 and skip == 0:
        show_progress = sys.stdout.isatty()
        if show_progress:
            bar_ctx = alive_bar(len(cfg.variables), bar="fish")
        else:
            bar_ctx = nullcontext()
        with bar_ctx as bar_animation:
            for nn, _ in enumerate(cfg.variables):
                if show_progress:
                    bar_animation()
                _draw_map(
                    deck,
                    fig,
                    axes,
                    original_loc,
                    cb,
                    cmin,
                    cmax,
                    maska,
                    diffa,
                    named,
                    deckd,
                    slice_title,
                    slice_name,
                    cfg,
                    generated_files,
                    data,
                    t,
                    nn,
                    nn,
                    xc,
                    yc,
                    sub1,
                    mx,
                    my,
                    xname,
                    yname,
                )
    else:
        _draw_map(
            deck,
            fig,
            axes,
            original_loc,
            cb,
            cmin,
            cmax,
            maska,
            diffa,
            named,
            deckd,
            slice_title,
            slice_name,
            cfg,
            generated_files,
            data,
            t,
            n,
            k,
            xc,
            yc,
            sub1,
            mx,
            my,
            xname,
            yname,
        )
    return []


def _set_axis(
    fig: Figure,
    axes: Any,
    cfg: PlopmConfig,
    data: SimData,
    name: str,
    n: int,
    t: int,
    k: int,
    n_s: int,
    unit: str,
    xc: NDArray,
    yc: NDArray,
    extinf: float,
    named: str,
    deckd: str,
    defcol: bool,
    slice_title: str,
    feature_id: int,
) -> None:
    """Configure labels, limits, ticks, and annotations for a map axis.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure containing the map.
    axes : matplotlib.axes.Axes or np.ndarray
        Map axes.
    cfg : PlopmConfig
        Initialized map configuration.
    data : SimData
        Loaded simulation data.
    name : str
        Variable name.
    n, t, k, n_s : int
        Variable, restart, subplot, and slice indices.
    unit : str
        Variable unit label.
    xc, yc : np.ndarray
        Coordinate meshes.
    extinf : float
        Padding added to map extents.
    named, deckd : str
        Display names for the primary and difference cases.
    defcol : bool
        Whether default categorical colors are used.
    slice_title : str
        Human-readable slice description.
    feature_id : int
        Number assigned to the active well or fault feature.

    """
    unrst = data.unrst
    nx = data.nx
    ny = data.ny
    nz = data.nz
    actind = data.active_idx
    restart = data.steps
    porv = data.active_pv
    axis = axes.flat[k]
    name_lower = name.lower()
    is_discrete_num = (
        "num" in name
        and (cfg.colormaps[n] in cfg.disc_colormaps or defcol)
        and cfg.discrete
    )
    namet, time = name, ""
    if cfg.time_units[0] == "dates":
        date_values = unrst["INTEHEAD", restart[t]]
        date = datetime.date(
            date_values[66],
            date_values[65],
            date_values[64],
        )
        time = f" {date}"
    elif cfg.time_units[0] == "empty":
        pass
    else:
        tskl, tunit = time_unit(cfg.time_units[0])
        tunit = tunit[5:]
        if unrst and unrst.count("DOUBHEAD", 0):
            time = f" {tskl*unrst['DOUBHEAD', restart[t]][0]:.0f} {tunit}"
        elif cfg.time_units[0] in ["s", "m", "h", "d", "w", "y"]:
            time = f" {restart[t]:.0f} {tunit}"
        else:
            time = f" {restart[t]:.0f} [{cfg.time_units[0]}]"
    if cfg.equal_aspect:
        axis.axis("scaled")
    extra = ""
    if name_lower == "porv":
        extra = f", sum={np.sum(porv):.3e}"
    elif name_lower in cfg.mass_vars and cfg.difference_input:
        extra = f", |sum|={extinf:.3e} {unit}"
    elif name_lower in cfg.mass_vars:
        extra = f", sum={extinf:.3e} {unit}"
    elif cfg.difference_input:
        extra = f", |sum|={extinf:.3e}"
    elif cfg.variables[0] in ["wells", "faults"]:
        time = ""
        namet = f"Total no. {name} = {feature_id-1}, "
    elif is_discrete_num:
        time = ""
        namet = ""
    if cfg.csv_columns[n][0]:
        tslide = ""
    elif cfg.variables[0] in ["wells", "faults"] or is_discrete_num:
        tslide = slice_title[2:]
    else:
        tslide = slice_title
    if (
        cfg.subplot_grid[0]
        and len(cfg.cases[0]) > 1
        and cfg.title[k] == "0"
        and cfg.hide_map_elements[3] == 0
    ):
        if name_lower == "porv":
            named += f" (total porv={np.sum(data.porv)})"
        axis.set_title(named)
        if k == 0 and cfg.suptitle != "0":
            fig.suptitle(f"{time[1:]}")
    elif cfg.subplot_grid[0] and len(cfg.variables) > 1 and cfg.title[k] == "0":
        if k == 0 and cfg.suptitle != "0":
            fig.suptitle(f"{named}{time}")
    elif (
        cfg.gif
        and len(cfg.variables) == 1
        and cfg.title[k] == "0"
        and cfg.hide_map_elements[3] == 0
    ):
        if cfg.difference_input:
            axis.set_title(f"{named}-{deckd}{time}")
        else:
            axis.set_title(f"{named}{time}")
    elif (
        cfg.gif
        and len(cfg.variables) == 1
        and cfg.title[k] != "0"
        and cfg.hide_map_elements[3] == 0
    ):
        if not cfg.csv_columns[n][0]:
            axis.set_title(f"{cfg.title[k]} {time}")
        else:
            axis.set_title(f"{cfg.title[k]}")
            fig.suptitle(time)
    elif (
        len(restart) > 1
        and cfg.subplot_grid[0]
        and len(cfg.cases[0]) == 1
        and cfg.title[k] == "0"
        and cfg.hide_map_elements[3] == 0
    ):
        axis.set_title(f"{unrst['DOUBHEAD', restart[t]][0]} days")
        if k == 0 and cfg.suptitle != "0":
            if cfg.difference_input:
                fig.suptitle(f"{named}-{deckd}")
            else:
                fig.suptitle(f"{named}")
    elif cfg.hide_map_elements[3] == 0 and cfg.title[k] == "0":
        if cfg.difference_input:
            axis.set_title(f"{named}-{deckd}" + tslide + extra + time)
        else:
            axis.set_title(namet + tslide + extra + time)
    elif cfg.subplot_grid[0] and len(cfg.cases[0]) > 1:
        if k == 0 and cfg.suptitle != "0":
            if cfg.gif and cfg.csv_columns[n][0]:
                fig.suptitle(f"{restart[t]} {cfg.time_units[0]}")
            elif unrst:
                fig.suptitle(f"{unrst['DOUBHEAD', restart[t]][0]} days")
            else:
                fig.suptitle(f"{restart[t]} {cfg.time_units[0]}")
    if name_lower == "grid" and cfg.hide_map_elements[3] == 0 and cfg.title[k] == "0":
        axis.set_title(
            f"Grid = [{nx},{ny},{nz}], "
            + f"Total no. active cells = {np.max(actind)+1}"
        )
    if cfg.title[k] != "0" and cfg.hide_map_elements[3] == 0 and not cfg.gif:
        axis.set_title(cfg.title[k])
    if cfg.slice[n_s][2][0] == -2 and not axis.yaxis_inverted():
        axis.invert_yaxis()
    if len(cfg.xlim[n]) > 1:
        axis.set_xlim([float(cfg.xlim[n][0][1:]), float(cfg.xlim[n][1][:-1])])
        xlabels = np.linspace(
            float(cfg.xlim[n][0][1:]) * cfg.xscale,
            float(cfg.xlim[n][1][:-1]) * cfg.xscale,
            int(cfg.xtick_count[n]),
        )
    else:
        xlabels = np.linspace(
            np.min(xc) * cfg.xscale,
            np.max(xc) * cfg.xscale,
            int(cfg.xtick_count[n]),
        )
    _set_axis_ticks(
        axis, "x", xlabels, cfg.xscale, cfg.xformat[n], cfg.hide_map_elements[1]
    )
    if len(cfg.ylim[n]) > 1:
        axis.set_ylim([float(cfg.ylim[n][0][1:]), float(cfg.ylim[n][1][:-1])])
        ylabels = np.linspace(
            float(cfg.ylim[n][0][1:]) * cfg.yscale,
            float(cfg.ylim[n][1][:-1]) * cfg.yscale,
            int(cfg.ytick_count[n]),
        )
    else:
        ylabels = np.linspace(
            np.min(yc) * cfg.yscale,
            np.max(yc) * cfg.yscale,
            int(cfg.ytick_count[n]),
        )
    _set_axis_ticks(
        axis, "y", ylabels, cfg.yscale, cfg.yformat[n], cfg.hide_map_elements[0]
    )


def _formatted_ticks(
    values: NDArray,
    scale: float,
    value_format: str,
) -> tuple[list[float], list[str]]:
    """Format scaled tick locations and labels.

    Parameters
    ----------
    values : np.ndarray
        Unscaled tick values.
    scale : float
        Coordinate scale factor.
    value_format : str
        Python format specification.

    Returns
    -------
    tuple[list[float], list[str]]
        Scaled tick locations and formatted labels.

    """
    labels = [format(value, value_format) for value in values]
    ticks = [float(label) / scale for label in labels]
    return ticks, labels


def _set_axis_ticks(
    axis: Any,
    axis_name: str,
    labels: NDArray,
    scale: float,
    value_format: str,
    remove_axis: int,
) -> None:
    """Set formatted ticks on one coordinate axis.

    Parameters
    ----------
    axis :  matplotlib.axes.Axes or np.ndarray
        Map axes.
    axis_name : {"x", "y"}
        Coordinate axis to update.
    labels : np.ndarray
        Tick values before scaling.
    scale : float
        Coordinate scale factor.
    value_format : str
        Python format specification.
    remove_axis : int
        Nonzero when the selected axis is hidden.

    """
    if axis_name == "x":
        if value_format and remove_axis == 0:
            ticks, ticklabels = _formatted_ticks(labels, scale, value_format)
            axis.set_xticks(ticks)
            axis.set_xticklabels(ticklabels)
        elif remove_axis == 0:
            axis.set_xticks(labels / scale)
            if scale != 1:
                axis.set_xticklabels(labels)
    else:
        if value_format and remove_axis == 0:
            ticks, ticklabels = _formatted_ticks(labels, scale, value_format)
            axis.set_yticks(ticks)
            axis.set_yticklabels(ticklabels)
        elif remove_axis == 0:
            axis.set_yticks(labels / scale)
            if scale != 1:
                axis.set_yticklabels(labels)


def _draw_map(
    deck: str,
    fig: Figure,
    axes: Any,
    original_loc: list[Any],
    cb: list[Any],
    cmin: list[float],
    cmax: list[float],
    maska: list[Any],
    diffa: list[NDArray],
    named: str,
    deckd: str,
    slice_title: str,
    slice_name: str,
    cfg: PlopmConfig,
    generated_files: list[str],
    data: SimData,
    t: int,
    n: int,
    k: int,
    xc: NDArray,
    yc: NDArray,
    sub1: int,
    mx: int,
    my: int,
    xname: str,
    yname: str,
) -> None:
    """Draw and optionally save one spatial map.

    Parameters
    ----------
    deck : str
        Simulation-case stem.
    fig : matplotlib.figure.Figure
        Figure receiving the map.
    axes : matplotlib.axes.Axes or np.ndarray
        Target axes.
    original_loc, cb : list
        Original axes locators and active colorbars.
    cmin, cmax : list[float]
        Configured color limits.
    maska, diffa : list
        Mapped masks and cached difference arrays.
    named, deckd : str
        Display names for the primary and difference cases.
    slice_title, slice_name : str
        Human-readable slice descriptions.
    cfg : PlopmConfig
        Initialized map configuration.
    generated_files : list[str]
        Generated filenames updated when a PNG is saved.
    data : SimData
        Loaded simulation data.
    t, n, k : int
        Restart-step, variable, and subplot indices.
    xc, yc : np.ndarray
        Coordinate meshes.
    sub1 : int
        Number of subplot columns.
    mx, my : int
        Mapped grid dimensions.
    xname, yname : str
        Coordinate-axis names.

    """
    var = cfg.variables[n]
    unit, values = read_quantity(
        deck,
        data,
        var,
        data.steps[t],
        float(cfg.scale_factor[n]),
        cfg.mass_vars,
        cfg.mass_vars + cfg.mass_fracs,
        cfg.caprock_vars,
        cfg.stress_coefficient,
        cfg.filters[k],
        cfg.gif,
        cfg.min_threshold[n],
        cfg.max_threshold[n],
        cfg.csv_columns[k],
    )
    n_s, feature_id, features = 0, 1, None
    labels: list[str] = []
    if cfg.subplot_grid[0] and len(cfg.cases[0]) > 1:
        n_s = k
    if cfg.csv_columns[k][0]:
        quaa = values
    else:
        if cfg.variables[0] == "wells":
            features, labels = get_wells(cfg, k)
        elif cfg.variables[0] == "faults":
            features, labels = get_faults(cfg, k)
        feature_id = len(labels) + 1
        if cfg.slice[n_s][0][0] != -2:
            quaa = map_yz(cfg, data, var, values, k, mx, my, features, feature_id)
        elif cfg.slice[n_s][1][0] != -2:
            quaa = map_xz(cfg, data, var, values, k, mx, my, features, feature_id)
        else:
            quaa = map_xy(cfg, data, var, values, k, mx, my, features, feature_id)
    if cfg.difference_input:
        quaa -= diffa[t]
    if cfg.mask_variable:
        mask = maska[k]
        maxv = np.nanmax(mask)
        mask_condition = quaa < cfg.mask_threshold
        quaa[mask_condition] = -cmax[n] * (maxv - mask[mask_condition]) / (maxv - 1)
    if cfg.csv:
        text = [f"{val}\n" for val in quaa if not np.isnan(val)]
        name = _clean_name(f"{named}_{var}_{slice_name}_t{data.steps[t]}")
        if cfg.filename[n]:
            name = cfg.filename[n]
        filename = f"{name}.csv"
        with open(
            f"{cfg.output_dir}/{filename}",
            "w",
            encoding="utf8",
        ) as file:
            file.write("".join(text))
        generated_files.append(filename)
        return
    if var in cfg.mass_vars and cfg.difference_input:
        extinf = np.nansum(np.abs(quaa))
    elif var in cfg.mass_vars:
        extinf = np.sum(quaa[~np.isnan(quaa)])
    elif cfg.difference_input:
        extinf = np.nansum(np.abs(quaa))
    else:
        extinf = np.empty(0)
    ntick = 3
    ncolor = var + " " + unit
    defcol, temp, cmap = True, "tab20", matplotlib.colormaps.get_cmap("tab20")
    if cfg.colormaps[n] in plt.colormaps():
        defcol = False
        cmap = matplotlib.colormaps.get_cmap(cfg.colormaps[n])
        temp = cfg.colormaps[n]
    if var not in ("wells", "grid", "faults"):
        valid_maps = quaa[~np.isnan(quaa)]
        if (
            len(cfg.cases[0]) > 1
            and cfg.subplot_grid[0]
            or len(cfg.variables) > 1
            and cfg.subplot_grid[0]
            or len(data.steps) > 1
            and cfg.subplot_grid[0]
            and len(cfg.cases[0]) == 1
            or cfg.gif
            and not cfg.subplot_grid[0]
            or int(cfg.color_log[n]) == 1
        ):
            minc = cmin[n]
            maxc = cmax[n]
        elif not cfg.global_range and valid_maps.size > 0:
            minc = np.min(valid_maps)
            maxc = np.max(valid_maps)
        elif valid_maps.size > 0:
            values = np.asarray(values)
            valid_quan = values[~np.isnan(values)]
            if valid_quan.size > 0:
                minc = np.min(valid_quan)
                maxc = np.max(valid_quan)
            else:
                minc = 0
                maxc = 0
        else:
            minc = 0
            maxc = 0
        if cfg.clim[n][0]:
            minc = float(cfg.clim[n][0][1:])
            maxc = float(cfg.clim[n][1][:-1])
        elif cfg.difference_input and int(cfg.color_log[n]) == 0:
            minmax = max(abs(maxc), abs(minc))
            minc = -minmax
            maxc = minmax
        if maxc == minc:
            ntick = 1
        elif (
            "num" in var
            and (cfg.colormaps[n] in cfg.disc_colormaps or defcol)
            and cfg.discrete
            and (minc.is_integer() and maxc.is_integer())
        ):
            ntick = int(maxc - minc + 1)
        if cfg.mask_variable:
            minc = -maxc
    elif var in ["faults", "wells"]:
        minc = 1
        maxc = feature_id
    else:
        minc = 1
        maxc = 1
    nlc = ntick
    if cfg.colorbar_tick_count[n] and ntick > 1:
        ntick = int(cfg.colorbar_tick_count[n])
    if cfg.colorbar_label:
        ncolor = cfg.colorbar_label
    shc = 0.0
    if abs(minc) < sys.float_info.epsilon:
        minc = 0
    if ("num" in var and temp in cfg.disc_colormaps and cfg.discrete) or (
        defcol and temp != "nipy_spectral"
    ):
        if maxc == minc:
            shc = 2.0
        from_list = matplotlib.colors.LinearSegmentedColormap.from_list
        cmap = from_list(
            "custom",
            matplotlib.colormaps[temp](range(int(minc), int(minc) + nlc + int(shc))),
            nlc,
        )
        if ntick == 2:
            shc = (maxc - minc) / 2.0
        elif minc == 0 and "num" not in var and var != "mpi_rank" or cfg.mask_variable:
            shc = 0
        else:
            shc = 0.5
    if defcol:
        temp0 = []
        for values in cfg.colormaps[n].split(" "):
            if values[0] == "#":
                temp0.append(values)
            else:
                temp0.append([])
                for color in values.split(";"):
                    if color.isnumeric():
                        temp0[-1].append(float(color) / 255.0)
                    else:
                        plopm_error(
                            f"Color given in {cli_error_value(f'-c {cfg.colormaps[n]}')} not found."
                        )
        cmap = colors.ListedColormap(temp0)
    if cfg.inactive_color != "w":
        cmap = cmap.with_extremes(bad=cfg.inactive_color)
    axis = axes.flat[k]
    if len(cfg.grid_edges) > 1:
        if var == "grid":
            imag = axis.pcolormesh(
                xc,
                yc,
                quaa.reshape(my, mx),
                facecolors="none",
                edgecolors=cfg.grid_edges[0],
                lw=float(cfg.grid_edges[1]),
            )
        elif int(cfg.color_log[n]) == 0:
            imag = axis.pcolormesh(
                xc,
                yc,
                quaa.reshape(my, mx),
                shading="flat",
                cmap=cmap,
                edgecolors=cfg.grid_edges[0],
                lw=float(cfg.grid_edges[1]),
            )
        else:
            imag = axis.pcolormesh(
                xc,
                yc,
                quaa.reshape(my, mx),
                shading="flat",
                cmap=cmap,
                norm=colors.LogNorm(vmin=minc, vmax=maxc),
                edgecolors=cfg.grid_edges[0],
                lw=float(cfg.grid_edges[1]),
            )
    else:
        if var == "grid":
            imag = axis.pcolormesh(
                xc,
                yc,
                quaa.reshape(my, mx),
                facecolors="none",
                edgecolors="black",
                lw=0.001,
            )
        elif int(cfg.color_log[n]) == 0:
            imag = axis.pcolormesh(
                xc,
                yc,
                quaa.reshape(my, mx),
                shading="flat",
                cmap=cmap,
            )
        else:
            imag = axis.pcolormesh(
                xc,
                yc,
                quaa.reshape(my, mx),
                shading="flat",
                cmap=cmap,
                norm=colors.LogNorm(vmin=minc, vmax=maxc),
            )
    if cfg.subplot_grid[0] and cfg.gif and len(cfg.variables) > 1 and cb[k] != "":
        axes, cb = _remove_colorbar(axes, original_loc, cb, k)
    if cfg.subplot_grid[0] and cfg.gif and len(cfg.cases[0]) > 1 and cb[k] != "":
        axes, cb = _remove_colorbar(axes, original_loc, cb, k)
    if (
        not cfg.subplot_grid[0]
        and cb[k] != ""
        and cfg.gif
        and cfg.hide_map_elements[2] == 0
    ):
        axes, cb = _remove_colorbar(axes, original_loc, cb, k)
    divider = make_axes_locatable(axis)
    if cfg.mask_variable:
        vect = np.linspace(
            0,
            maxc,
            ntick,
            endpoint=True,
        )
    else:
        vect = np.linspace(
            minc,
            maxc,
            ntick,
            endpoint=True,
        )
    frmt = "{:" + cfg.cb_formats[n] + "}"

    def formatter(value: float, _: Any) -> str:
        """Format a colorbar value.

        Parameters
        ----------
        value : float
            Colorbar value.
        _ : Any
            Unused Matplotlib tick position.

        Returns
        -------
        str
            Formatted colorbar label.

        """
        return frmt.format(value)

    if not cfg.mask_variable:
        if int(cfg.color_log[n]) == 1:
            pass
        else:
            for i, val in enumerate(vect):
                if abs(float(frmt.format(val))) == 0:
                    vect[i] = 0
                    if i == 0:
                        minc = 0
    if var not in ("wells", "grid", "faults"):
        if int(cfg.color_log[n]) == 0:
            if len(data.steps) > 1 and cfg.subplot_grid[0] and len(cfg.cases[0]) == 1:
                if cfg.colorbar_position[0] != -1:
                    cb[0] = fig.colorbar(
                        imag,
                        cax=fig.add_axes(cfg.colorbar_position),
                        ticks=vect,
                        label=ncolor,
                        format=(
                            mticker.FixedFormatter(cfg.colorbar_ticks[n])
                            if cfg.colorbar_ticks[n]
                            else formatter
                        ),
                        shrink=0.2,
                        location="top",
                    )
            elif not cfg.subplot_grid[0] or len(cfg.cases[0]) == 1:
                cb[k] = fig.colorbar(
                    imag,
                    cax=divider.append_axes("right", size="2%", pad=0.05),
                    orientation="vertical",
                    ticks=vect,
                    label=ncolor,
                    format=(
                        mticker.FixedFormatter(cfg.colorbar_ticks[n])
                        if cfg.colorbar_ticks[n]
                        else formatter
                    ),
                )
            elif k == 0 and cfg.colorbar_position[0] != -1:
                cb[0] = fig.colorbar(
                    imag,
                    cax=fig.add_axes(cfg.colorbar_position),
                    ticks=vect,
                    label=ncolor,
                    format=(
                        mticker.FixedFormatter(cfg.colorbar_ticks[n])
                        if cfg.colorbar_ticks[n]
                        else formatter
                    ),
                    shrink=0.2,
                    location="top",
                )
        else:
            if cfg.color_log_ticks:

                class LogTickFormatter(LogFormatter):
                    def set_locs(self, locs: Any | None = None) -> None:
                        """Set logarithmic colorbar sublabels from the configuration.

                        Parameters
                        ----------
                        locs : Any, optional
                            Tick locations supplied by Matplotlib.

                        """
                        self._sublabels = set(cfg.color_log_ticks)

            if cfg.subplot_grid[0]:
                if cfg.colorbar_position[0] != -1:
                    if cfg.color_log_ticks:
                        cb[k] = fig.colorbar(
                            imag,
                            cax=fig.add_axes(cfg.colorbar_position),
                            label=ncolor,
                            shrink=0.2,
                            location="top",
                            ticks=cfg.color_log_ticks,
                            format=LogTickFormatter(),
                        )
                    else:
                        cb[k] = fig.colorbar(
                            imag,
                            cax=fig.add_axes(cfg.colorbar_position),
                            label=ncolor,
                            shrink=0.2,
                            location="top",
                        )
            else:
                if cfg.color_log_ticks:
                    cb[k] = fig.colorbar(
                        imag,
                        cax=divider.append_axes("right", size="5%", pad=0.05),
                        orientation="vertical",
                        label=ncolor,
                        ticks=cfg.color_log_ticks,
                        format=LogTickFormatter(),
                    )
                else:
                    cb[k] = fig.colorbar(
                        imag,
                        cax=divider.append_axes("right", size="5%", pad=0.05),
                        orientation="vertical",
                        label=ncolor,
                    )
    else:
        _add_map_overlay(fig, cfg, imag, divider, vect, n, var, features, labels)
    imag.set_clim(
        minc - shc,
        maxc + shc,
    )
    _set_axis(
        fig,
        axes,
        cfg,
        data,
        var,
        n,
        t,
        k,
        n_s,
        unit,
        xc,
        yc,
        extinf,
        named,
        deckd,
        defcol,
        slice_title,
        feature_id,
    )
    if cfg.xlabel[n] and cfg.hide_map_elements[1] == 0:
        axis.set_xlabel(cfg.xlabel[n])
    elif (
        cfg.hide_map_elements[1] == 0
        and len(cfg.variables) == 1
        and (k + sub1 >= len(cfg.cases[0]) or not cfg.subplot_grid[0])
    ):
        if len(data.steps) > 1 and cfg.subplot_grid[0] and len(cfg.cases[0]) == 1:
            if k + sub1 >= len(data.steps):
                axis.set_xlabel(f"{xname+cfg.xunit}")
        else:
            axis.set_xlabel(f"{xname+cfg.xunit}")
    elif (
        cfg.hide_map_elements[1] == 0
        and len(cfg.cases[0]) == 1
        and (k + sub1 >= len(cfg.variables) or not cfg.subplot_grid[0])
    ) or (
        cfg.hide_map_elements[1] == 0
        and len(cfg.cases[0]) == len(cfg.variables)
        and len(cfg.variables) > 1
        and (k + sub1 >= len(cfg.variables) or not cfg.subplot_grid[0])
    ):
        axis.set_xlabel(f"{xname+cfg.xunit}")
    if cfg.ylabel[n] and cfg.hide_map_elements[0] == 0:
        axis.set_ylabel(cfg.ylabel[n])
    elif cfg.hide_map_elements[0] == 0 and (k % sub1 == 0 or not cfg.subplot_grid[0]):
        axis.set_ylabel(f"{yname+cfg.yunit}")
    if cfg.hide_map_elements[2] == 1 and len(fig.axes) > 1:
        fig.delaxes(fig.axes[1])
    if (
        cfg.hide_map_elements[1] == 1
        or (
            k + sub1 < len(cfg.cases[0])
            and cfg.subplot_grid[0]
            and len(cfg.variables) == 1
            and cfg.remove_duplicate_labels
        )
        or cfg.hide_map_elements[1] == 1
        or (
            k + sub1 < len(cfg.variables)
            and cfg.subplot_grid[0]
            and len(cfg.cases[0]) == 1
            and cfg.remove_duplicate_labels
        )
        or (
            k + sub1 < len(data.steps)
            and len(data.steps) > 1
            and cfg.subplot_grid[0]
            and len(cfg.cases[0]) == 1
            and cfg.remove_duplicate_labels
        )
    ):
        axis.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    if cfg.hide_map_elements[0] == 1 or (
        k % sub1 > 0 and cfg.subplot_grid[0] and cfg.remove_duplicate_labels == 1
    ):
        axis.tick_params(axis="y", which="both", left=False, labelleft=False)
    axis.set_facecolor(cfg.fc)
    if not cfg.gif:
        if cfg.subplot_grid[0]:
            if (
                t == len(data.steps) - 1
                and len(data.steps) > 1
                or n == len(cfg.variables) - 1
                and len(cfg.variables) > 1
            ):
                _save_map(
                    fig,
                    cfg,
                    data,
                    generated_files,
                    named,
                    var,
                    slice_name,
                    t,
                    n,
                )
            else:
                if len(data.steps) == 1:
                    if k == max(len(cfg.variables) - 1, len(cfg.cases[0]) - 1):
                        _save_map(
                            fig,
                            cfg,
                            data,
                            generated_files,
                            named,
                            var,
                            slice_name,
                            t,
                            n,
                        )
                elif (
                    len(cfg.cases[0]) == 1
                    or len(data.steps) > 1
                    and len(cfg.cases[0]) == len(data.steps)
                ):
                    if t == len(data.steps) - 1:
                        _save_map(
                            fig,
                            cfg,
                            data,
                            generated_files,
                            named,
                            var,
                            slice_name,
                            t,
                            n,
                        )
                else:
                    _save_map(
                        fig,
                        cfg,
                        data,
                        generated_files,
                        named,
                        var,
                        slice_name,
                        t,
                        n,
                    )
        else:
            save_index = t if cfg.rst_range else n
            _save_map(
                fig,
                cfg,
                data,
                generated_files,
                named,
                var,
                slice_name,
                t,
                save_index,
            )
            plt.close()


def _clean_name(name: str) -> str:
    """Convert a variable expression to a filename-safe stem.

    Parameters
    ----------
    name : str
        Variable expression or filename stem.

    Returns
    -------
    str
        Name with operators and spaces replaced.

    """
    name = name.replace(" / ", "_over_")
    name = name.replace(" ", "")
    return name


def _save_map(
    fig: Figure,
    cfg: PlopmConfig,
    data: SimData,
    generated_files: list[str],
    named: str,
    var: str,
    slice_name: str,
    t: int,
    save_index: int,
) -> None:
    """Save the current spatial map as a PNG file.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure containing the map.
    cfg : PlopmConfig
        Output filename, directory, resolution, and face-color settings.
    data : SimData
        Simulation data containing the selected restart steps.
    generated_files : list[str]
        Generated filenames updated in place.
    named : str
        Case name used in the default filename.
    var : str
        Plotted variable name or expression.
    slice_name : str
        Slice description used in the default filename.
    t : int
        Index of the restart step being plotted.
    save_index : int
        Index used to select a custom filename.

    """
    fig.set_facecolor(cfg.fc)
    name = _clean_name(f"{named}_{var}_{slice_name}_t{data.steps[t]}")
    if save_index < len(cfg.filename) and cfg.filename[save_index]:
        name = cfg.filename[save_index]

    filename = f"{name}.png"
    fig.savefig(
        f"{cfg.output_dir}/{filename}",
        bbox_inches="tight",
        dpi=int(cfg.dpi[0]),
    )
    generated_files.append(filename)


def _remove_colorbar(
    axes: Any,
    original_loc: list[Any],
    cb: list[Any],
    colorbar_index: int,
) -> tuple[Any, list[Any]]:
    """Remove a colorbar and restore its axes locator.

    Parameters
    ----------
    axes : matplotlib.axes.Axes or np.ndarray
        Map axes.
    original_loc : list
        Original axes locators.
    cb : list
        Active colorbar objects.
    colorbar_index : int
        Colorbar and axes index to restore.

    Returns
    -------
    tuple
        Updated axes and colorbar list.

    """
    if (
        colorbar_index < len(cb)
        and colorbar_index < len(original_loc)
        and cb[colorbar_index] != ""
    ):
        cb[colorbar_index].remove()
        axes.flat[colorbar_index].set_axes_locator(original_loc[colorbar_index])
        cb[colorbar_index] = ""
    return axes, cb


def _add_map_overlay(
    fig: Figure,
    cfg: PlopmConfig,
    imag: ScalarMappable,
    divider: AxesDivider,
    vect: NDArray,
    n: int,
    var: str,
    features: list | None,
    labels: list[str],
) -> None:
    """Add a categorical colorbar and labels for map features.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure containing the map.
    cfg : PlopmConfig
        Initialized map configuration.
    imag : matplotlib.cm.ScalarMappable
        Mappable used to construct the colorbar.
    divider : mpl_toolkits.axes_grid1.axes_divider.AxesDivider
        Divider associated with the map axis.
    vect : np.ndarray
        Categorical colorbar tick values.
    n : int
        Variable index.
    var : str
        Categorical variable, such as ``"wells"`` or ``"faults"``.
    features : list, optional
        Feature locations grouped by label.
    labels : list[str]
        Feature names.

    """
    fig.colorbar(
        imag,
        cax=divider.append_axes("right", size="0%", pad=0.05),
        orientation="vertical",
        ticks=vect,
        format=lambda x, _: "",
    )
    feature_id = len(labels) + 1
    if var in ["faults", "wells"] and features is not None:
        cmap = matplotlib.colormaps[cfg.colormaps[n]]
        colour = cmap(np.linspace(0, 1, feature_id))
        if feature_id < 70:
            for label_index, label_name in enumerate(labels):
                _add_label(features, label_index, label_name, colour)
        else:
            for label_index, label_name in zip(
                [0, len(getattr(cfg, var)) - 1], [labels[0], labels[-1]]
            ):
                _add_label(features, label_index, label_name, colour)


def _add_label(
    features: list,
    label_index: int,
    label_name: str,
    colour: NDArray,
) -> None:
    """Draw one feature label when the feature is present.

    Parameters
    ----------
    features : list
        Feature locations grouped by label.
    label_index : int
        Index of the feature group.
    label_name : str
        Text shown beside the categorical colorbar.
    colour : np.ndarray
        Colors assigned to feature groups.

    """
    item = features[label_index]
    if any(item):
        plt.text(
            0,
            label_index + 1,
            f"{label_name}",
            c=colour[label_index],
            fontweight="bold",
        )
