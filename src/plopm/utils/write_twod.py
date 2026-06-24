# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W3301,W0123,R0912,R0915,R0914,R1702,W0611,R0913,R0917,C0302,C0115,R0916,E1102

"""Utility functions to write the 2D figures (PNGs and GIFs)"""

import datetime
import sys
from contextlib import nullcontext
from typing import Any
from collections.abc import Iterable
import colorcet  # noqa: F401  # registers colorcet colormaps with matplotlib
import numpy as np
from numpy.typing import NDArray
from alive_progress import alive_bar
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.artist import Artist
from matplotlib.animation import FuncAnimation, writers
from matplotlib import animation, colors
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.cm import ScalarMappable
from matplotlib.ticker import LogFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.axes_divider import AxesDivider
from plopm.config.config import ConfigPlopm, ReadData
from plopm.utils.readers import (
    get_quantity,
    get_csvs,
    get_faults,
    get_readers,
    get_wells,
    initialize_time,
)
from plopm.utils.mapping import (
    handle_slide_x,
    handle_slide_y,
    handle_slide_z,
    rotate_grid,
    map_xzcoords,
    map_xycoords,
    map_yzcoords,
)


def prepare_maps(
    cfg: ConfigPlopm, deck: str, n: int
) -> tuple[ReadData, NDArray, NDArray, str, str, str, int, int, str, str]:
    """Get the spatial coordinates"""
    if cfg.csvs[n][0]:
        xc, yc, mx, my, xname, yname = get_csvs(cfg, deck, n)
        slidet, sliden = "", ""
        read = ReadData(restart=cfg.restart)
    else:
        read = get_readers(deck, cfg.gif, cfg.vtk, cfg.vrs, cfg.restart, cfg.filter, n)
        slide = cfg.slide[n]
        if slide[0][0] != -2:
            xc, yc, slidet, sliden, mx, my, xname, yname = handle_slide_x(cfg, read, n)
        elif slide[1][0] != -2:
            xc, yc, slidet, sliden, mx, my, xname, yname = handle_slide_y(cfg, read, n)
        else:
            xc, yc, slidet, sliden, mx, my, xname, yname = handle_slide_z(cfg, read, n)
    if int(cfg.rotate[n]) != 0 or cfg.translate[n] != ["[0", "0]"]:
        xc, yc = rotate_grid(cfg, n, xc, yc)
    return (
        read,
        xc,
        yc,
        deck.rsplit("/", 1)[-1].lower(),
        slidet,
        sliden,
        mx,
        my,
        xname,
        yname,
    )


def make_maps(cfg: ConfigPlopm) -> None:
    """Method to create the 2d maps using pcolormesh"""

    def create_figure(
        rows: int = 1,
        columns: int = 1,
        layout: str | None = None,
    ) -> tuple[Figure, Axes]:
        plt.close()
        if layout:
            fig, axiss = plt.subplots(rows, columns, layout=layout)
        else:
            fig, axiss = plt.subplots(rows, columns)
        return fig, axiss

    def normalize_axis(axiss: Axes | NDArray[Any]) -> NDArray:
        if isinstance(axiss, np.ndarray):
            return axiss
        return np.array([axiss])

    def prepare_colorbars(axiss: NDArray[Any]) -> tuple[list[Any], list[str]]:
        original_loc, cb = [], []
        for axis in axiss.flat:
            original_loc.append(axis.get_axes_locator())
            cb.append("")
        return original_loc, cb

    def delete_extra_axes(axiss: NDArray[Any], keep: int, fig: Figure) -> None:
        for o in range(max(0, len(axiss.flat) - keep)):
            axis_to_remove = axiss.flat[-1 - o]
            if axis_to_remove in fig.axes:
                fig.delaxes(axis_to_remove)

    def save_animation(im_ani: FuncAnimation, name: str) -> None:
        if cfg.loop or not writers.is_available("ffmpeg"):
            im_ani.save(f"{cfg.output}/{name}.gif")
        else:
            im_ani.save(f"{cfg.output}/{name}.gif", extra_args=["-loop", "-1"])

    skip = 0
    if (
        cfg.subfigs[0]
        and len(cfg.vrs) > 1
        and len(cfg.restart) == 1
        and len(cfg.names[0]) == 1
    ):
        skip = 1
    if cfg.subfigs[0]:
        fig, axis = create_figure(int(cfg.subfigs[0]), int(cfg.subfigs[1]))
        sub1 = int(cfg.subfigs[1])
    else:
        fig, axis = create_figure(1, 1, "compressed")
        sub1 = 1
    if cfg.subfigs[0] and cfg.gif and len(cfg.names[0]) > 1:
        _, _, _, cmin, cmax, diffa = find_min_max(cfg)
        maska = get_mask(cfg) if cfg.mask else []
        deckd = set_deck_name(cfg.diff) if cfg.diff else ""
        fig, axis = create_figure(
            int(cfg.subfigs[0]), int(cfg.subfigs[1]), "compressed"
        )
        axiss = normalize_axis(axis)
        read, xc, yc, named, slidet, sliden, mx, my, xname, yname = prepare_maps(
            cfg, cfg.names[0][0], 0
        )
        original_loc, cb = prepare_colorbars(axiss)
        delete_extra_axes(axiss, len(cfg.names[0]), fig)
        im_ani = animation.FuncAnimation(
            fig,
            mapit,
            fargs=(
                cfg.names[0][0],
                fig,
                axiss,
                original_loc,
                cb,
                cmin,
                cmax,
                maska,
                diffa,
                named,
                deckd,
                slidet,
                sliden,
                cfg,
                0,
                read,
                xc,
                yc,
                skip,
                sub1,
                mx,
                my,
                xname,
                yname,
            ),
            frames=len(read.restart),
            interval=cfg.interval,
            blit=False,
            repeat=False,
        )
        save_animation(im_ani, cfg.save[0] if cfg.save[0] else cfg.vrs[0])
    elif cfg.subfigs[0] and cfg.gif and len(cfg.vrs) > 1:
        read, xc, yc, cmin, cmax, diffa = find_min_max(cfg)
        deckd = set_deck_name(cfg.diff) if cfg.diff else ""
        read, xc, yc, named, slidet, sliden, mx, my, xname, yname = prepare_maps(
            cfg, cfg.names[0][0], 0
        )
        maska = get_mask(cfg) if cfg.mask else []
        if len(read.restart) > 1:
            fig, axis = create_figure(int(cfg.subfigs[0]), int(cfg.subfigs[1]))
        axiss = normalize_axis(axis)
        plt.tight_layout(pad=1.7)
        original_loc, cb = prepare_colorbars(axiss)
        delete_extra_axes(axiss, len(cfg.vrs), fig)
        im_ani = animation.FuncAnimation(
            fig,
            mapit,
            fargs=(
                cfg.names[0][0],
                fig,
                axiss,
                original_loc,
                cb,
                cmin,
                cmax,
                maska,
                diffa,
                named,
                deckd,
                slidet,
                sliden,
                cfg,
                0,
                read,
                xc,
                yc,
                skip,
                sub1,
                mx,
                my,
                xname,
                yname,
            ),
            frames=len(read.restart),
            interval=cfg.interval,
            blit=False,
            repeat=False,
        )
        save_animation(im_ani, cfg.save[0] if cfg.save[0] else named)
    else:
        _, _, _, cmin, cmax, diffa = find_min_max(cfg)
        maska = get_mask(cfg) if cfg.mask else []
        deckd = set_deck_name(cfg.diff) if cfg.diff else ""
        read, xc, yc, named, slidet, sliden, mx, my, xname, yname = prepare_maps(
            cfg, cfg.names[0][0], 0
        )
        for n, var in enumerate(cfg.vrs):
            if len(read.restart) > 1:
                if cfg.subfigs[0]:
                    fig, axis = create_figure(int(cfg.subfigs[0]), int(cfg.subfigs[1]))
                else:
                    fig, axis = create_figure(1, 1)
            if not cfg.subfigs[0] and not cfg.gif:
                plt.close()
                fig, axis = create_figure(1, 1, "tight")
            axiss = normalize_axis(axis)
            original_loc, cb = prepare_colorbars(axiss)
            if len(read.restart) > 1:
                delete_extra_axes(axiss, len(read.restart), fig)
            if cfg.gif and len(read.restart) > 1:
                im_ani = animation.FuncAnimation(
                    fig,
                    mapit,
                    fargs=(
                        cfg.names[0][0],
                        fig,
                        axiss,
                        original_loc,
                        cb,
                        cmin,
                        cmax,
                        maska,
                        diffa,
                        named,
                        deckd,
                        slidet,
                        sliden,
                        cfg,
                        n,
                        read,
                        xc,
                        yc,
                        skip,
                        sub1,
                        mx,
                        my,
                        xname,
                        yname,
                    ),
                    frames=len(read.restart),
                    interval=cfg.interval,
                    blit=False,
                    repeat=False,
                )
                name = f"{cfg.save[0] if cfg.save[0] else named + '_' + var}"
                save_animation(im_ani, name)
            else:
                if len(cfg.names[0]) > 1:
                    delete_extra_axes(axiss, len(cfg.names[0]), fig)
                if len(read.restart) > 1 and len(cfg.names[0]) == len(read.restart):
                    if not cfg.subfigs[0]:
                        fig, axis = create_figure(1, 1)
                        axiss = normalize_axis(axis)
                        original_loc, cb = prepare_colorbars(axiss)
                    mapit(
                        0,
                        cfg.names[0][0],
                        fig,
                        axiss,
                        original_loc,
                        cb,
                        cmin,
                        cmax,
                        maska,
                        diffa,
                        named,
                        deckd,
                        slidet,
                        sliden,
                        cfg,
                        n,
                        read,
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
                    for t, _ in enumerate(read.restart):
                        if not cfg.subfigs[0]:
                            plt.close()
                            fig, axis = create_figure(1, 1)
                            axiss = normalize_axis(axis)
                            original_loc, cb = prepare_colorbars(axiss)
                        mapit(
                            t,
                            cfg.names[0][0],
                            fig,
                            axiss,
                            original_loc,
                            cb,
                            cmin,
                            cmax,
                            maska,
                            diffa,
                            named,
                            deckd,
                            slidet,
                            sliden,
                            cfg,
                            n,
                            read,
                            xc,
                            yc,
                            skip,
                            sub1,
                            mx,
                            my,
                            xname,
                            yname,
                        )


def fill_map_array(
    cfg: ConfigPlopm,
    read: ReadData,
    var: str,
    quan: NDArray,
    slide_index: int,
    map_index: int,
    mx: int,
    my: int,
    use_csv: bool = False,
) -> NDArray:
    """Retrieve the quantity"""
    if use_csv:
        quaa = np.asarray(quan).copy()
    elif cfg.slide[slide_index][0][0] != -2:
        quaa = map_yzcoords(cfg, read, var, quan, map_index, mx, my)
    elif cfg.slide[slide_index][1][0] != -2:
        quaa = map_xzcoords(cfg, read, var, quan, map_index, mx, my)
    else:
        quaa = map_xycoords(cfg, read, var, quan, map_index, mx, my)
    return quaa


def find_min_max(
    cfg: ConfigPlopm,
) -> tuple[ReadData, NDArray, NDArray, list[float], list[float], list[NDArray]]:
    """Method to find the min and max for the colorbars"""
    cmin, cmax = [float("inf")], [float("-inf")]
    diffa: list[NDArray] = []
    xc, yc = np.empty(0), np.empty(0)
    if (cfg.rst_range and cfg.png and not cfg.subfigs[0]) or (
        cfg.bounds[0][0] and not cfg.diff
    ):
        return ReadData(), xc, yc, cmin, cmax, diffa

    def apply_diff_and_log(
        quaa: NDArray,
        var_index: int,
        restart_index: int,
    ) -> None:
        if cfg.diff:
            quaa -= diffa[restart_index]
        if int(cfg.log[var_index]) == 1:
            quaa[quaa <= 0] = np.nan

    def update_color_range(quaa: NDArray) -> None:
        if np.any(~np.isnan(quaa)):
            cmin[-2] = min(cmin[-2], np.nanmin(quaa))
            cmax[-2] = max(cmax[-2], np.nanmax(quaa))

    if cfg.restart[0] == -1 and cfg.gif:
        read = get_readers(
            cfg.names[0][0], cfg.gif, cfg.vtk, cfg.vrs, cfg.restart, cfg.filter
        )
    else:
        read = ReadData(restart=cfg.restart)
    if cfg.diff:
        var = cfg.vrs[0]
        for t, _ in enumerate(read.restart):
            read, xc, yc, _, _, _, mx, my, _, _ = prepare_maps(cfg, cfg.diff, 1)
            _, quan = get_quantity(
                cfg.diff,
                read,
                var,
                read.restart[t],
                float(cfg.adjust[0]),
                cfg.mass,
                cfg.mass + cfg.xmass,
                cfg.caprock,
                cfg.stress,
                cfg.filter[0],
                cfg.gif,
                cfg.vmin[0],
                cfg.vmax[0],
                cfg.csvs[0],
            )
            quaa = fill_map_array(cfg, read, var, quan, 1, 1, mx, my)
            diffa.append(quaa.copy())
    if len(cfg.vrs) == len(cfg.names[0]) and len(cfg.names[0]) > 1:
        for m, var in enumerate(cfg.vrs):
            cmin.append(cmin[-1])
            cmax.append(cmax[-1])
            for t, _ in enumerate(read.restart):
                read, xc, yc, _, _, _, mx, my, _, _ = prepare_maps(
                    cfg, cfg.names[0][m], m
                )
                _, quan = get_quantity(
                    cfg.names[0][m],
                    read,
                    var,
                    read.restart[t],
                    float(cfg.adjust[m]),
                    cfg.mass,
                    cfg.mass + cfg.xmass,
                    cfg.caprock,
                    cfg.stress,
                    cfg.filter[0],
                    cfg.gif,
                    cfg.vmin[m],
                    cfg.vmax[m],
                    cfg.csvs[0],
                )
                quaa = fill_map_array(cfg, read, var, quan, m, m, mx, my)
                apply_diff_and_log(quaa, m, t)
                update_color_range(quaa)
    else:
        for m, var in enumerate(cfg.vrs):
            cmin.append(cmin[-1])
            cmax.append(cmax[-1])
            for n, deck in enumerate(cfg.names[0]):
                for t, _ in enumerate(read.restart):
                    read, xc, yc, _, _, _, mx, my, _, _ = prepare_maps(cfg, deck, n)
                    _, quan = get_quantity(
                        deck,
                        read,
                        var,
                        read.restart[t],
                        float(cfg.adjust[m]),
                        cfg.mass,
                        cfg.mass + cfg.xmass,
                        cfg.caprock,
                        cfg.stress,
                        cfg.filter[n],
                        cfg.gif,
                        cfg.vmin[m],
                        cfg.vmax[m],
                        cfg.csvs[n],
                    )
                    quaa = fill_map_array(
                        cfg, read, var, quan, n, n, mx, my, cfg.csvs[n][0]
                    )
                    apply_diff_and_log(quaa, m, t)
                    update_color_range(quaa)
    return read, xc, yc, cmin, cmax, diffa


def get_mask(cfg: ConfigPlopm) -> list[NDArray]:
    """Read the mask"""
    maska = []
    var = cfg.mask
    for n, deck in enumerate(cfg.names[0]):
        read, _, _, _, _, _, mx, my, _, _ = prepare_maps(cfg, deck, n)
        _, quan = get_quantity(
            deck,
            read,
            var,
            0,
            float(cfg.adjust[0]),
            cfg.mass,
            cfg.mass + cfg.xmass,
            cfg.caprock,
            cfg.stress,
            cfg.filter[n],
            cfg.gif,
            cfg.vmin[0],
            cfg.vmax[0],
            cfg.csvs[n],
        )
        maska.append(fill_map_array(cfg, read, var, quan, n, n, mx, my))
    return maska


def set_deck_name(deck: str) -> str:
    """For the title"""
    if len(deck.split("/")) > 1:
        return deck.split("/")[-1].lower()
    return deck.lower()


def mapit(
    t: int,
    deck: str,
    fig: Figure,
    axiss: Any,
    original_loc: list[Any],
    cb: list[str],
    cmin: list[float],
    cmax: list[float],
    maska: list[Any],
    diffa: list[NDArray],
    named: str,
    deckd: str,
    slidet: str,
    sliden: str,
    cfg: ConfigPlopm,
    n: int,
    read: ReadData,
    xc: NDArray,
    yc: NDArray,
    skip: int,
    sub1: int,
    mx: int,
    my: int,
    xname: str,
    yname: str,
) -> Iterable[Artist]:
    """Method to coordinate the generation of axis"""
    k = t
    if not cfg.subfigs[0]:
        k = 0
    elif len(read.restart) == 1:
        k = n
    if cfg.subfigs[0] and len(cfg.names[0]) > 1:
        show_progress = sys.stdout.isatty()
        if show_progress:
            bar_ctx = alive_bar(len(cfg.names[0]), bar="fish")
        else:
            bar_ctx = nullcontext()
        with bar_ctx as bar_animation:
            if len(cfg.vrs) > 1:
                cmax = [np.max(cmax)] * len(cmax)
                cmin = [np.min(cmin)] * len(cmin)
                for nn, deckl in enumerate(cfg.names[0]):
                    if show_progress:
                        bar_animation()
                    read, xc, yc, named, slidet, sliden, mx, my, xname, yname = (
                        prepare_maps(cfg, deckl, nn)
                    )
                    mapits(
                        deckl,
                        fig,
                        axiss,
                        original_loc,
                        cb,
                        cmin,
                        cmax,
                        maska,
                        diffa,
                        named,
                        deckd,
                        slidet,
                        sliden,
                        cfg,
                        read,
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
                for nn, deckl in enumerate(cfg.names[0]):
                    if show_progress:
                        bar_animation()
                    read, xc, yc, named, slidet, sliden, mx, my, xname, yname = (
                        prepare_maps(cfg, deckl, nn)
                    )
                    if len(read.restart) > 1 and len(cfg.names[0]) == len(read.restart):
                        mapits(
                            deckl,
                            fig,
                            axiss,
                            original_loc,
                            cb,
                            cmin,
                            cmax,
                            maska,
                            diffa,
                            named,
                            deckd,
                            slidet,
                            sliden,
                            cfg,
                            read,
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
                        mapits(
                            deckl,
                            fig,
                            axiss,
                            original_loc,
                            cb,
                            cmin,
                            cmax,
                            maska,
                            diffa,
                            named,
                            deckd,
                            slidet,
                            sliden,
                            cfg,
                            read,
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
    elif cfg.subfigs[0] and len(cfg.vrs) > 1 and skip == 0:
        show_progress = sys.stdout.isatty()
        if show_progress:
            bar_ctx = alive_bar(len(cfg.vrs), bar="fish")
        else:
            bar_ctx = nullcontext()
        with bar_ctx as bar_animation:
            for nn, _ in enumerate(cfg.vrs):
                if show_progress:
                    bar_animation()
                mapits(
                    deck,
                    fig,
                    axiss,
                    original_loc,
                    cb,
                    cmin,
                    cmax,
                    maska,
                    diffa,
                    named,
                    deckd,
                    slidet,
                    sliden,
                    cfg,
                    read,
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
        mapits(
            deck,
            fig,
            axiss,
            original_loc,
            cb,
            cmin,
            cmax,
            maska,
            diffa,
            named,
            deckd,
            slidet,
            sliden,
            cfg,
            read,
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


def handle_axis(
    fig: Figure,
    axiss: Any,
    cfg: ConfigPlopm,
    read: ReadData,
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
    slidet: str,
    nwelult: int,
) -> None:
    """Method to handle the figure axis"""

    def formatted_ticks(
        values: NDArray,
        scale: float,
        value_format: str,
    ) -> tuple[list[float], list[str]]:
        labels = [format(value, value_format) for value in values]
        ticks = [float(label) / scale for label in labels]
        return ticks, labels

    def set_axis_ticks(
        axis_name: str,
        labels: NDArray,
        scale: float,
        value_format: str,
        remove_axis: int,
    ) -> None:

        if axis_name == "x":
            if value_format and remove_axis == 0:
                ticks, ticklabels = formatted_ticks(labels, scale, value_format)
                axis.set_xticks(ticks)
                axis.set_xticklabels(ticklabels)
            elif remove_axis == 0:
                axis.set_xticks(labels / scale)
                if scale != 1:
                    axis.set_xticklabels(labels)
        else:
            if value_format and remove_axis == 0:
                ticks, ticklabels = formatted_ticks(labels, scale, value_format)
                axis.set_yticks(ticks)
                axis.set_yticklabels(ticklabels)
            elif remove_axis == 0:
                axis.set_yticks(labels / scale)
                if scale != 1:
                    axis.set_yticklabels(labels)

    unrst = read.unrst
    nx = read.nx
    ny = read.ny
    nz = read.nz
    actind = read.actind
    restart = read.restart
    porv = read.pv
    axis = axiss.flat[k]
    name_lower = name.lower()
    is_discrete_num = (
        "num" in name and (cfg.cmaps[n] in cfg.cmdisc or defcol) and cfg.discrete
    )
    namet, time = name, ""
    if cfg.tunits[0] == "dates":
        date_values = unrst["INTEHEAD", restart[t]]
        date = datetime.datetime(
            date_values[66], date_values[65], date_values[64], 0, 0
        )
        time = f" {date.date()}"
    elif cfg.tunits[0] == "empty":
        pass
    else:
        tskl, tunit = initialize_time(cfg.tunits[0])
        tunit = tunit[5:]
        if unrst:
            time = f" {tskl*unrst['DOUBHEAD', restart[t]][0]:.0f} {tunit}"
        else:
            time = f" {restart[t]:.0f} {tunit}"
    if cfg.scale:
        axis.axis("scaled")
    extra = ""
    if name_lower == "porv":
        extra = f", sum={np.sum(porv):.3e}"
    elif name_lower in cfg.mass and cfg.diff:
        extra = f", |sum|={extinf:.3e} {unit}"
    elif name_lower in cfg.mass:
        extra = f", sum={extinf:.3e} {unit}"
    elif cfg.diff:
        extra = f", |sum|={extinf:.3e}"
    elif cfg.vrs[0] in ["wells", "faults"]:
        time = ""
        namet = f"Total no. {name} = {nwelult-1}, "
    elif is_discrete_num:
        time = ""
        namet = ""
    if cfg.csvs[n][0]:
        tslide = ""
    elif cfg.vrs[0] in ["wells", "faults"] or is_discrete_num:
        tslide = slidet[2:]
    else:
        tslide = slidet
    if (
        cfg.subfigs[0]
        and len(cfg.names[0]) > 1
        and cfg.title[k] == "0"
        and cfg.rm[3] == 0
    ):
        axis.set_title(named)
        if k == 0 and cfg.suptitle != "0":
            fig.suptitle(f"{time[1:]}")
    elif cfg.subfigs[0] and len(cfg.vrs) > 1 and cfg.title[k] == "0":
        if k == 0 and cfg.suptitle != "0":
            fig.suptitle(f"{named}{time}")
    elif cfg.gif and len(cfg.vrs) == 1 and cfg.title[k] == "0" and cfg.rm[3] == 0:
        if cfg.diff:
            axis.set_title(f"{named}-{deckd}{time}")
        else:
            axis.set_title(f"{named}{time}")
    elif cfg.gif and len(cfg.vrs) == 1 and cfg.title[k] != "0" and cfg.rm[3] == 0:
        if not cfg.csvs[n][0]:
            axis.set_title(f"{cfg.title[k]} {time}")
        else:
            axis.set_title(f"{cfg.title[k]}")
            fig.suptitle(time)
    elif (
        len(restart) > 1
        and cfg.subfigs[0]
        and len(cfg.names[0]) == 1
        and cfg.title[k] == "0"
        and cfg.rm[3] == 0
    ):
        axis.set_title(f"{unrst['DOUBHEAD', restart[t]][0]} days")
        if k == 0 and cfg.suptitle != "0":
            if cfg.diff:
                fig.suptitle(f"{named}-{deckd}")
            else:
                fig.suptitle(f"{named}")
    elif cfg.rm[3] == 0 and cfg.title[k] == "0":
        if cfg.diff:
            axis.set_title(f"{named}-{deckd}" + tslide + extra + time)
        else:
            axis.set_title(namet + tslide + extra + time)
    elif cfg.subfigs[0] and len(cfg.names[0]) > 1:
        if k == 0 and cfg.suptitle != "0":
            if cfg.gif and cfg.csvs[n][0]:
                fig.suptitle(f"{restart[t]} {cfg.tunits[0]}")
            elif unrst:
                fig.suptitle(f"{unrst['DOUBHEAD', restart[t]][0]} days")
            else:
                fig.suptitle(f"{restart[t]} {cfg.tunits[0]}")
    if name_lower == "grid" and cfg.rm[3] == 0 and cfg.title[k] == "0":
        axis.set_title(
            f"Grid = [{nx},{ny},{nz}], "
            + f"Total no. active cells = {np.max(actind)+1}"
        )
    if cfg.title[k] != "0" and cfg.rm[3] == 0 and not cfg.gif:
        axis.set_title(cfg.title[k])
    if cfg.slide[n_s][2][0] == -2 and not axis.yaxis_inverted():
        axis.invert_yaxis()
    if len(cfg.xlim[n]) > 1:
        axis.set_xlim([float(cfg.xlim[n][0][1:]), float(cfg.xlim[n][1][:-1])])
        xlabels = np.linspace(
            float(cfg.xlim[n][0][1:]) * cfg.xskl,
            float(cfg.xlim[n][1][:-1]) * cfg.xskl,
            int(cfg.xlnum[n]),
        )
    else:
        xlabels = np.linspace(
            np.min(xc) * cfg.xskl,
            np.max(xc) * cfg.xskl,
            int(cfg.xlnum[n]),
        )
    set_axis_ticks("x", xlabels, cfg.xskl, cfg.xformat[n], cfg.rm[1])
    if len(cfg.ylim[n]) > 1:
        axis.set_ylim([float(cfg.ylim[n][0][1:]), float(cfg.ylim[n][1][:-1])])
        ylabels = np.linspace(
            float(cfg.ylim[n][0][1:]) * cfg.yskl,
            float(cfg.ylim[n][1][:-1]) * cfg.yskl,
            int(cfg.ylnum[n]),
        )
    else:
        ylabels = np.linspace(
            np.min(yc) * cfg.yskl,
            np.max(yc) * cfg.yskl,
            int(cfg.ylnum[n]),
        )
    set_axis_ticks("y", ylabels, cfg.yskl, cfg.yformat[n], cfg.rm[0])


def mapits(
    deck: str,
    fig: Figure,
    axiss: Any,
    original_loc: list[Any],
    cb: list[Any],
    cmin: list[float],
    cmax: list[float],
    maska: list[Any],
    diffa: list[NDArray],
    named: str,
    deckd: str,
    slidet: str,
    sliden: str,
    cfg: ConfigPlopm,
    read: ReadData,
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
    """Generate the spatial maps"""

    def clean_name(name: str) -> str:
        name = name.replace(" / ", "_over_")
        name = name.replace(" ", "")
        return name

    def save_map(named: str, save_index: int) -> None:
        fig.set_facecolor(cfg.fc)
        name = clean_name(f"{named}_{var}_{sliden}_t{read.restart[t]}")
        if save_index < len(cfg.save):
            if cfg.save[save_index]:
                name = cfg.save[save_index]
        fig.savefig(
            f"{cfg.output}/{name}.png",
            bbox_inches="tight",
            dpi=int(cfg.dpi[0]),
        )

    def remove_colorbar(
        axiss: Any,
        original_loc: list[Any],
        cb: list[Any],
        colorbar_index: int,
    ) -> tuple[Any, list[Any]]:
        if (
            colorbar_index < len(cb)
            and colorbar_index < len(original_loc)
            and cb[colorbar_index] != ""
        ):
            cb[colorbar_index].remove()
            axiss.flat[colorbar_index].set_axes_locator(original_loc[colorbar_index])
            cb[colorbar_index] = ""
        return axiss, cb

    var = cfg.vrs[n]
    unit, quan = get_quantity(
        deck,
        read,
        var,
        read.restart[t],
        float(cfg.adjust[n]),
        cfg.mass,
        cfg.mass + cfg.xmass,
        cfg.caprock,
        cfg.stress,
        cfg.filter[k],
        cfg.gif,
        cfg.vmin[n],
        cfg.vmax[n],
        cfg.csvs[k],
    )
    n_s, nwelult, welult = 0, 1, None
    lwelult: list[str] = []
    if cfg.subfigs[0] and len(cfg.names[0]) > 1:
        n_s = k
    if cfg.csvs[k][0]:
        quaa = quan
    else:
        if cfg.vrs[0] == "wells":
            welult, lwelult = get_wells(cfg, k)
        elif cfg.vrs[0] == "faults":
            welult, lwelult = get_faults(cfg, k)
        nwelult = len(lwelult) + 1
        if cfg.slide[n_s][0][0] != -2:
            quaa = map_yzcoords(cfg, read, var, quan, k, mx, my, welult, nwelult)
        elif cfg.slide[n_s][1][0] != -2:
            quaa = map_xzcoords(cfg, read, var, quan, k, mx, my, welult, nwelult)
        else:
            quaa = map_xycoords(cfg, read, var, quan, k, mx, my, welult, nwelult)
    if cfg.diff:
        quaa -= diffa[t]
    if cfg.mask:
        mask = maska[k]
        maxv = np.nanmax(mask)
        mask_condition = quaa < cfg.maskthr
        quaa[mask_condition] = -cmax[n] * (maxv - mask[mask_condition]) / (maxv - 1)
    if cfg.csv:
        text = [f"{val}\n" for val in quaa if not np.isnan(val)]
        name = clean_name(f"{named}_{var}_{sliden}_t{read.restart[t]}")
        if cfg.save[n]:
            name = cfg.save[n]
        with open(f"{cfg.output}/{name}.csv", "w", encoding="utf8") as file:
            file.write("".join(text))
        return
    if var in cfg.mass and cfg.diff:
        extinf = np.nansum(np.abs(quaa))
    elif var in cfg.mass:
        extinf = np.sum(quaa[~np.isnan(quaa)])
    elif cfg.diff:
        extinf = np.nansum(np.abs(quaa))
    else:
        extinf = np.empty(0)
    ntick = 3
    ncolor = var + " " + unit
    defcol, temp, cmap = True, "tab20", matplotlib.colormaps.get_cmap("tab20")
    if cfg.cmaps[n] in plt.colormaps():
        defcol = False
        cmap = matplotlib.colormaps.get_cmap(cfg.cmaps[n])
        temp = cfg.cmaps[n]
    if var not in ("wells", "grid", "faults"):
        valid_maps = quaa[~np.isnan(quaa)]
        if len(cfg.names[0]) > 1 and cfg.subfigs[0]:
            minc = cmin[n]
            maxc = cmax[n]
        elif len(cfg.vrs) > 1 and cfg.subfigs[0]:
            minc = cmin[n]
            maxc = cmax[n]
        elif len(read.restart) > 1 and cfg.subfigs[0] and len(cfg.names[0]) == 1:
            minc = cmin[n]
            maxc = cmax[n]
        elif cfg.gif and not cfg.subfigs[0] or int(cfg.log[n]) == 1:
            minc = cmin[n]
            maxc = cmax[n]
        elif not cfg.global_ and valid_maps.size > 0:
            minc = np.min(valid_maps)
            maxc = np.max(valid_maps)
        elif valid_maps.size > 0:
            quan = np.asarray(quan)
            valid_quan = quan[~np.isnan(quan)]
            if valid_quan.size > 0:
                minc = np.min(valid_quan)
                maxc = np.max(valid_quan)
            else:
                minc = 0
                maxc = 0
        else:
            minc = 0
            maxc = 0
        if cfg.bounds[n][0]:
            minc = float(cfg.bounds[n][0][1:])
            maxc = float(cfg.bounds[n][1][:-1])
        elif cfg.diff and int(cfg.log[n]) == 0:
            minmax = max(abs(maxc), abs(minc))
            minc = -minmax
            maxc = minmax
        if maxc == minc:
            ntick = 1
        elif (
            "num" in var
            and (cfg.cmaps[n] in cfg.cmdisc or defcol)
            and cfg.discrete
            and (minc.is_integer() and maxc.is_integer())
        ):
            ntick = int(maxc - minc + 1)
        if cfg.mask:
            minc = -maxc
    elif var in ["faults", "wells"]:
        minc = 1
        maxc = nwelult
    else:
        minc = 1
        maxc = 1
    nlc = ntick
    if cfg.cnum[n] and ntick > 1:
        ntick = int(cfg.cnum[n])
    if cfg.clabel:
        ncolor = cfg.clabel
    shc = 0.0
    if abs(minc) < sys.float_info.epsilon:
        minc = 0
    if ("num" in var and temp in cfg.cmdisc and cfg.discrete) or (
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
        elif minc == 0 and "num" not in var and var != "mpi_rank":
            shc = 0
        elif cfg.mask:
            shc = 0
        else:
            shc = 0.5
    if defcol:
        temp0 = []
        for values in cfg.cmaps[n].split(" "):
            if values[0] == "#":
                temp0.append(values)
            else:
                temp0.append([])
                for color in values.split(";"):
                    if color.isnumeric():
                        temp0[-1].append(float(color) / 255.0)
                    else:
                        print("Error for color given in -c:", cfg.cmaps[n])
                        sys.exit()
        cmap = colors.ListedColormap(temp0)
    if cfg.ncolor != "w":
        cmap = cmap.with_extremes(bad=cfg.ncolor)
    axis = axiss.flat[k]
    if len(cfg.grid) > 1:
        if var == "grid":
            imag = axis.pcolormesh(
                xc,
                yc,
                quaa.reshape(my, mx),
                facecolors="none",
                edgecolors=cfg.grid[0],
                lw=float(cfg.grid[1]),
            )
        elif int(cfg.log[n]) == 0:
            imag = axis.pcolormesh(
                xc,
                yc,
                quaa.reshape(my, mx),
                shading="flat",
                cmap=cmap,
                edgecolors=cfg.grid[0],
                lw=float(cfg.grid[1]),
            )
        else:
            imag = axis.pcolormesh(
                xc,
                yc,
                quaa.reshape(my, mx),
                shading="flat",
                cmap=cmap,
                norm=colors.LogNorm(vmin=minc, vmax=maxc),
                edgecolors=cfg.grid[0],
                lw=float(cfg.grid[1]),
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
        elif int(cfg.log[n]) == 0:
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
    if cfg.subfigs[0] and cfg.gif and len(cfg.vrs) > 1 and cb[k] != "":
        axiss, cb = remove_colorbar(axiss, original_loc, cb, k)
    if cfg.subfigs[0] and cfg.gif and len(cfg.names[0]) > 1 and cb[k] != "":
        axiss, cb = remove_colorbar(axiss, original_loc, cb, k)
    if not cfg.subfigs[0] and cb[k] != "" and cfg.gif and cfg.rm[2] == 0:
        axiss, cb = remove_colorbar(axiss, original_loc, cb, k)
    divider = make_axes_locatable(axis)
    if cfg.mask:
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
    frmt = "{:" + cfg.cformat[n] + "}"

    def formatter(value: float, _: Any) -> str:
        return frmt.format(value)

    if not cfg.mask:
        if int(cfg.log[n]) == 1:
            pass
        else:
            for i, val in enumerate(vect):
                if abs(float(frmt.format(val))) == 0:
                    vect[i] = 0
                    if i == 0:
                        minc = 0
    if var not in ("wells", "grid", "faults"):
        if int(cfg.log[n]) == 0:
            if len(read.restart) > 1 and cfg.subfigs[0] and len(cfg.names[0]) == 1:
                if cfg.cbsfax[0] != -1:
                    cb[0] = fig.colorbar(
                        imag,
                        cax=fig.add_axes(cfg.cbsfax),
                        ticks=vect,
                        label=ncolor,
                        format=(
                            mticker.FixedFormatter(cfg.cticks[n])
                            if cfg.cticks[n]
                            else formatter
                        ),
                        shrink=0.2,
                        location="top",
                    )
            elif not cfg.subfigs[0] or len(cfg.names[0]) == 1:
                cb[k] = fig.colorbar(
                    imag,
                    cax=divider.append_axes("right", size="2%", pad=0.05),
                    orientation="vertical",
                    ticks=vect,
                    label=ncolor,
                    format=(
                        mticker.FixedFormatter(cfg.cticks[n])
                        if cfg.cticks[n]
                        else formatter
                    ),
                )
            elif k == 0 and cfg.cbsfax[0] != -1:
                cb[0] = fig.colorbar(
                    imag,
                    cax=fig.add_axes(cfg.cbsfax),
                    ticks=vect,
                    label=ncolor,
                    format=(
                        mticker.FixedFormatter(cfg.cticks[n])
                        if cfg.cticks[n]
                        else formatter
                    ),
                    shrink=0.2,
                    location="top",
                )
        else:
            if cfg.clogthks:

                class LogTickFormatter(LogFormatter):
                    def set_locs(self, locs: Any | None = None) -> None:
                        self._sublabels = set(cfg.clogthks)

            if cfg.subfigs[0]:
                if cfg.cbsfax[0] != -1:
                    if cfg.clogthks:
                        cb[k] = fig.colorbar(
                            imag,
                            cax=fig.add_axes(cfg.cbsfax),
                            label=ncolor,
                            shrink=0.2,
                            location="top",
                            ticks=cfg.clogthks,
                            format=LogTickFormatter(),
                        )
                    else:
                        cb[k] = fig.colorbar(
                            imag,
                            cax=fig.add_axes(cfg.cbsfax),
                            label=ncolor,
                            shrink=0.2,
                            location="top",
                        )
            else:
                if cfg.clogthks:
                    cb[k] = fig.colorbar(
                        imag,
                        cax=divider.append_axes("right", size="5%", pad=0.05),
                        orientation="vertical",
                        label=ncolor,
                        ticks=cfg.clogthks,
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
        handle_well_or_grid_or_fault(
            fig, cfg, imag, divider, vect, n, var, welult, lwelult
        )
    imag.set_clim(
        minc - shc,
        maxc + shc,
    )
    handle_axis(
        fig,
        axiss,
        cfg,
        read,
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
        slidet,
        nwelult,
    )
    if cfg.xlabel[n] and cfg.rm[1] == 0:
        axis.set_xlabel(cfg.xlabel[n])
    elif (
        cfg.rm[1] == 0
        and len(cfg.vrs) == 1
        and (k + sub1 >= len(cfg.names[0]) or not cfg.subfigs[0])
    ):
        if len(read.restart) > 1 and cfg.subfigs[0] and len(cfg.names[0]) == 1:
            if k + sub1 >= len(read.restart):
                axis.set_xlabel(f"{xname+cfg.xunit}")
        else:
            axis.set_xlabel(f"{xname+cfg.xunit}")
    elif (
        cfg.rm[1] == 0
        and len(cfg.names[0]) == 1
        and (k + sub1 >= len(cfg.vrs) or not cfg.subfigs[0])
    ):
        axis.set_xlabel(f"{xname+cfg.xunit}")
    elif (
        cfg.rm[1] == 0
        and len(cfg.names[0]) == len(cfg.vrs)
        and len(cfg.vrs) > 1
        and (k + sub1 >= len(cfg.vrs) or not cfg.subfigs[0])
    ):
        axis.set_xlabel(f"{xname+cfg.xunit}")
    if cfg.ylabel[n] and cfg.rm[0] == 0:
        axis.set_ylabel(cfg.ylabel[n])
    elif cfg.rm[0] == 0 and (k % sub1 == 0 or not cfg.subfigs[0]):
        axis.set_ylabel(f"{yname+cfg.yunit}")
    if cfg.rm[2] == 1 and len(fig.axes) > 1:
        fig.delaxes(fig.axes[1])
    if cfg.rm[1] == 1 or (
        k + sub1 < len(cfg.names[0])
        and cfg.subfigs[0]
        and len(cfg.vrs) == 1
        and cfg.delax
    ):
        axis.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    elif cfg.rm[1] == 1 or (
        k + sub1 < len(cfg.vrs)
        and cfg.subfigs[0]
        and len(cfg.names[0]) == 1
        and cfg.delax
    ):
        axis.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    elif (
        k + sub1 < len(read.restart)
        and len(read.restart) > 1
        and cfg.subfigs[0]
        and len(cfg.names[0]) == 1
        and cfg.delax
    ):
        axis.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    if cfg.rm[0] == 1 or (k % sub1 > 0 and cfg.subfigs[0] and cfg.delax == 1):
        axis.tick_params(axis="y", which="both", left=False, labelleft=False)
    axis.set_facecolor(cfg.fc)
    if not cfg.gif:
        if cfg.subfigs[0]:
            if t == len(read.restart) - 1 and len(read.restart) > 1:
                save_map(named, n)
            elif n == len(cfg.vrs) - 1 and len(cfg.vrs) > 1:
                save_map(named, n)
            else:
                if len(read.restart) == 1:
                    if k == max(len(cfg.vrs) - 1, len(cfg.names[0]) - 1):
                        save_map(named, n)
                elif len(cfg.names[0]) == 1:
                    if t == len(read.restart) - 1:
                        save_map(named, n)
                elif len(read.restart) > 1 and len(cfg.names[0]) == len(read.restart):
                    if t == len(read.restart) - 1:
                        save_map(named, n)
                else:
                    save_map(named, n)
        else:
            save_index = t if cfg.rst_range else n
            save_map(named, save_index)
            plt.close()


def handle_well_or_grid_or_fault(
    fig: Figure,
    cfg: ConfigPlopm,
    imag: ScalarMappable,
    divider: AxesDivider,
    vect: NDArray,
    n: int,
    var: str,
    welult: list | None,
    lwelult: list[str],
) -> None:
    """Method to create the 2d maps using pcolormesh"""

    def add_label(
        welult: list,
        label_index: int,
        label_name: str,
        colour: NDArray,
    ) -> None:
        item = welult[label_index]
        if any(item):
            plt.text(
                0,
                label_index + 1,
                f"{label_name}",
                c=colour[label_index],
                fontweight="bold",
            )

    fig.colorbar(
        imag,
        cax=divider.append_axes("right", size="0%", pad=0.05),
        orientation="vertical",
        ticks=vect,
        format=lambda x, _: "",
    )
    nwelult = len(lwelult) + 1
    if var in ["faults", "wells"] and welult is not None:
        cmap = matplotlib.colormaps[cfg.cmaps[n]]
        colour = cmap(np.linspace(0, 1, nwelult))
        if nwelult < 70:
            for label_index, label_name in enumerate(lwelult):
                add_label(welult, label_index, label_name, colour)
        else:
            for label_index, label_name in zip(
                [0, len(getattr(cfg, var)) - 1], [lwelult[0], lwelult[-1]]
            ):
                add_label(welult, label_index, label_name, colour)
