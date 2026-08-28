# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0911,R0912,R0913,R0915,R0917,R1702,R0914,C0302,E1102

"""Read and derive plotting quantities from OPM Flow output.

The module opens INIT, UNRST, EGRID, SMSPEC, deck, and CSV data; constructs
plotting coordinates; evaluates variable expressions; and derives saturation,
mass, caprock, distance, well, and fault quantities.
"""

import csv
import datetime
import os
import sys
from contextlib import nullcontext

import numpy as np
from alive_progress import alive_bar
from numpy.typing import NDArray
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import EGrid as OpmGrid
from opm.io.ecl import ERst as OpmRestart
from opm.io.ecl import ESmry as OpmSummary

from plopm.config.config import PlopmConfig, SimData
from plopm.utils.initialization import mass_unit, spatial_unit
from plopm.utils.terminal import (
    cli_error_value,
    cli_info_value,
    plopm_error,
    plopm_info,
)

csv.field_size_limit(sys.maxsize)

GAS_DEN_REF = 1.86843
WAT_DEN_REF = 998.108


def read_case(
    deck: str,
    gif: bool,
    vtk: bool,
    variables: list,
    restart: list,
    filters: list,
    n: int = 0,
) -> SimData:
    """Open the OPM output required for one simulation case.

    Parameters
    ----------
    deck : str
        Simulation-case stem without an extension.
    gif, vtk : bool
        Output modes controlling restart and grid loading.
    variables : list
        Requested variables or expressions.
    restart : list
        Requested restart report steps.
    filters : list
        Property-filter expressions.
    n : int, default: 0
        Case index used to select per-case settings.

    Returns
    -------
    SimData
        Loaded readers, grid properties, and report-step metadata.

    """
    if os.path.isfile(f"{deck}.INIT"):
        init = OpmFile(f"{deck}.INIT")
    else:
        plopm_error(f"unable to find {cli_error_value(f'{deck}.INIT')}")
    unrst = OpmRestart(f"{deck}.UNRST") if os.path.isfile(f"{deck}.UNRST") else None
    egrid = (
        OpmGrid(f"{deck}.EGRID")
        if os.path.isfile(f"{deck}.EGRID") and not vtk
        else None
    )

    porv = np.array(init["PORV"])
    dx = np.array(init["DX"])
    dy = np.array(init["DY"])
    dz = np.array(init["DZ"])

    act_mask = porv > 0
    pv = porv[act_mask]
    actind = np.cumsum(act_mask) - 1

    tnrst = []
    ntot = 1

    if filters[n]:
        porv0 = porv.copy()
        for value in filters[n].split("&"):
            filte = value.strip().split(" ")
            key = filte[0].upper()
            if init.count(key):
                arr = np.array(init[key])
                mask = porv0 > 0
                porv[mask] = _apply_filter(porv[mask], arr, filte[1], float(filte[2]))

    if unrst:
        steps = unrst.report_steps
        ntot = steps[-1] + 1
        if unrst.count("DOUBHEAD", 0):
            tnrst = [unrst["DOUBHEAD", ntm][0] for ntm in steps]
        if restart[0] == -1:
            restart = unrst.report_steps if gif else [ntot - 1]
    elif restart[0] == -1:
        restart = [ntot - 1]

    nx = ny = nz = 0

    if egrid:
        dim = egrid.dimension
        nx, ny, nz = dim
    elif "index_i" in variables or "index_j" in variables or "index_k" in variables:
        grid = OpmGrid(f"{deck}.EGRID")
        dim = grid.dimension
        nx, ny, nz = dim

    if not tnrst:
        tnrst = [0] * len(restart)

    return SimData(
        init,
        unrst,
        egrid,
        porv,
        dx,
        dy,
        dz,
        pv,
        actind,
        restart,
        tnrst,
        porv.size,
        ntot,
        nx,
        ny,
        nz,
    )


def get_yz_coords(cfg: PlopmConfig, data: SimData, n: int) -> tuple[NDArray, NDArray]:
    """Build coordinate meshes for a yz slice.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized map configuration.
    data : SimData
        Loaded grid data.
    n : int
        Slice index.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Y- and z-coordinate meshes.

    """
    xyz_func = data.grid.xyz_from_ijk
    ny_val = data.ny
    nz_val = data.nz
    base_i_all = cfg.slice[n][0][0]
    total_size = nz_val * 4 * ny_val
    xc_list = [0] * total_size
    yc_list = [0] * total_size
    idx = 0
    for j in range(nz_val):
        base_k = nz_val - j - 1
        base_idx_second = idx + 2 * ny_val
        tmp_idx = base_idx_second
        for i in range(ny_val):
            val = xyz_func(base_i_all, i, base_k, True)
            xc_list[idx] = val[1][4]
            yc_list[idx] = val[2][4]
            idx += 1
            xc_list[idx] = val[1][6]
            yc_list[idx] = val[2][6]
            idx += 1
            xc_list[tmp_idx] = val[1][0]
            yc_list[tmp_idx] = val[2][0]
            tmp_idx += 1
            xc_list[tmp_idx] = val[1][2]
            yc_list[tmp_idx] = val[2][2]
            tmp_idx += 1
        idx = base_idx_second + 2 * ny_val
    xc_array = np.asarray(xc_list)
    yc_array = np.asarray(yc_list)
    return xc_array.reshape(2 * nz_val, 2 * ny_val), yc_array.reshape(
        2 * nz_val, 2 * ny_val
    )


def get_xz_coords(cfg: PlopmConfig, data: SimData, n: int) -> tuple[NDArray, NDArray]:
    """Build coordinate meshes for an xz slice.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized map configuration.
    data : SimData
        Loaded grid data.
    n : int
        Slice index.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        X- and z-coordinate meshes.

    """
    xyz_func = data.grid.xyz_from_ijk
    nx_val = data.nx
    nz_val = data.nz
    base_j_all = cfg.slice[n][1][0]
    total_size = nz_val * 4 * nx_val
    xc_list = [0] * total_size
    yc_list = [0] * total_size
    idx = 0
    for j in range(nz_val):
        base_k = nz_val - j - 1
        base_idx_second = idx + 2 * nx_val
        tmp_idx = base_idx_second
        for i in range(nx_val):
            val = xyz_func(i, base_j_all, base_k, True)
            xc_list[idx] = val[0][4]
            yc_list[idx] = val[2][4]
            idx += 1
            xc_list[idx] = val[0][5]
            yc_list[idx] = val[2][5]
            idx += 1
            xc_list[tmp_idx] = val[0][0]
            yc_list[tmp_idx] = val[2][0]
            tmp_idx += 1
            xc_list[tmp_idx] = val[0][1]
            yc_list[tmp_idx] = val[2][1]
            tmp_idx += 1
        idx = base_idx_second + 2 * nx_val
    xc_array = np.asarray(xc_list)
    yc_array = np.asarray(yc_list)
    return xc_array.reshape(2 * nz_val, 2 * nx_val), yc_array.reshape(
        2 * nz_val, 2 * nx_val
    )


def get_xy_coords(cfg: PlopmConfig, data: SimData, n: int) -> tuple[NDArray, NDArray]:
    """Build coordinate meshes for an xy slice.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized map configuration.
    data : SimData
        Loaded grid data.
    n : int
        Slice index.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        X- and y-coordinate meshes.

    """
    xyz_func = data.grid.xyz_from_ijk
    nx_val = data.nx
    ny_val = data.ny
    base_k_all = cfg.slice[n][2][0]
    total_size = ny_val * 4 * nx_val
    xc_list = [0] * total_size
    yc_list = [0] * total_size
    idx = 0
    for j in range(ny_val):
        base_idx_second = idx + 2 * nx_val
        tmp_idx = base_idx_second
        for i in range(nx_val):
            val = xyz_func(i, j, base_k_all, True)
            xc_list[idx] = val[0][0]
            yc_list[idx] = val[1][0]
            idx += 1
            xc_list[idx] = val[0][1]
            yc_list[idx] = val[1][1]
            idx += 1
            xc_list[tmp_idx] = val[0][2]
            yc_list[tmp_idx] = val[1][2]
            tmp_idx += 1
            xc_list[tmp_idx] = val[0][3]
            yc_list[tmp_idx] = val[1][3]
            tmp_idx += 1
        idx = base_idx_second + 2 * nx_val
    xc_array = np.asarray(xc_list)
    yc_array = np.asarray(yc_list)
    return xc_array.reshape(2 * ny_val, 2 * nx_val), yc_array.reshape(
        2 * ny_val, 2 * nx_val
    )


def _resolve_var(
    cfg: PlopmConfig,
    data: SimData,
    key_up: str,
    key_low: str,
    step: int,
    init: OpmFile,
    unrst: OpmRestart,
    mass_all: list,
    caprock_list: list,
):
    """Resolve a variable from stored or derived quantities.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized configuration.
    data : SimData
        Loaded simulation data.
    key_up, key_low : str
        OPM keyword and normalized variable name.
    step : int
        Restart report step.
    init : OpmFile
        INIT reader.
    unrst : OpmRestart
        UNRST reader.
    mass_all, caprock_list : list
        Supported derived variable names.

    Returns
    -------
    np.ndarray or None
        Resolved values, or ``None`` when unavailable.

    """
    if init.count(key_up):
        return 1.0 * init[key_up, 0]
    if unrst is not None and unrst.count(key_up, step):
        return 1.0 * unrst[key_up, step]
    if key_low in mass_all:
        return _get_mass(data, key_low, step)
    if key_low in caprock_list:
        val, _ = _get_caprock(data, key_low, step, cfg.stress_coefficient)
        return val
    if key_low in ["swat", "soil", "sgas"]:
        return _get_saturation(data.unrst, key_low, step)
    return None


def _read_histogram(
    cfg: PlopmConfig, data: SimData, tokens: list, step: int
) -> NDArray:
    """Read values used to create a histogram.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized configuration.
    data : SimData
        Loaded simulation data.
    tokens : list
        Parsed variable-expression tokens.
    step : int
        Restart report step.

    Returns
    -------
    np.ndarray
        Values in global cell order with inactive cells set to NaN.

    """
    quan0_low = tokens[0]
    quan0 = quan0_low.upper()
    porv = data.porv
    nxyz = data.ncells
    init = data.init
    unrst = data.unrst
    mass_all = cfg.mass_vars + cfg.mass_fracs
    caprock_list = cfg.caprock_vars
    if quan0 != "PORV":
        act = porv > 0
    else:
        act = porv > -1
    var = np.nan * np.ones(nxyz, dtype=float)
    result = _resolve_var(
        cfg, data, quan0, quan0_low, step, init, unrst, mass_all, caprock_list
    )
    if result is not None:
        var[act] = result
    else:
        plopm_error(f"not found {cli_error_value(f'-v {tokens[0]}')}.")
    if len(tokens) > 1:
        ops = tokens[1::2]
        for j, val in enumerate(tokens[2::2]):
            val_up = val.upper()
            if val[0].isdigit() and not val[-1].isdigit():
                if unrst is None:
                    plopm_error(f"not found {cli_error_value(f'-v {val}')}.")
                other = 1.0 * unrst[val[1:].upper(), int(val[0])]
            elif val[0].isdigit() and val[-1].isdigit():
                other = np.full_like(var[act], float(val))
            else:
                other = _resolve_var(
                    cfg,
                    data,
                    val_up,
                    val,
                    step,
                    init,
                    unrst,
                    mass_all,
                    caprock_list,
                )
                if other is None:
                    plopm_error(f"not found {cli_error_value(f'-v {val}')}.")
            var_act = var[act]
            var[act] = _apply_operator(var_act, other, ops[j])
    return var


def _compute_distance(
    cfg: PlopmConfig, data: SimData, tokens: list, n: int
) -> tuple[NDArray, NDArray]:
    """Compute distance from selected cells to target points.

    Parameters
    ----------
    cfg : PlopmConfig
        Distance and sensor configuration.
    data : SimData
        Loaded simulation data.
    tokens : list
        Parsed expression selecting active cells.
    n : int
        Plot index.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Finite distances and their simulation times.

    """
    xyz_func = data.grid.xyz_from_ijk
    nx_val = data.nx
    ny_val = data.ny
    nz_val = data.nz
    nxyz = data.ncells
    ntot = data.nsteps
    porv = data.porv
    init = data.init
    unrst = data.unrst
    mass_all = cfg.mass_vars + cfg.mass_fracs
    distance_type = cfg.distance[0]
    xyz = np.zeros((nxyz, 3), dtype=float)
    act = porv > 0
    time = np.array(data.times)
    distance = np.nan * np.ones(ntot)
    index = 0
    for k in range(nz_val):
        for j in range(ny_val):
            for i in range(nx_val):
                xyz[index, :] = np.mean(xyz_func(i, j, k, True), axis=1)
                index += 1
    if cfg.distance[1] == "sensor":
        ind = (
            cfg.slice[n][0]
            + cfg.slice[n][1] * nx_val
            + cfg.slice[n][2] * nx_val * ny_val
        )
        points = [xyz[ind, :]]
        sensor_loc = f"[{points[0][0]:.2E},{points[0][1]:.2E},{points[0][2]:.2E}]"
        plopm_info(
            f"computing the {cli_info_value(cfg.distance[0])} distance of "
            f"{cli_info_value(tokens[0])} to the sensor "
            f"{cli_info_value(sensor_loc)} [m]"
        )
    else:
        points = []
        for k in range(nz_val):
            if ny_val > 1:
                base_k = k * nx_val * ny_val
                for i in range(nx_val):
                    ind = i + base_k
                    if act[ind]:
                        points.append(xyz[ind])
                    ind = i + (ny_val - 1) * nx_val + base_k
                    if act[ind]:
                        points.append(xyz[ind])
            if nx_val > 1:
                base_k = k * nx_val * ny_val
                for j in range(ny_val):
                    ind = j * nx_val + base_k
                    if act[ind]:
                        points.append(xyz[ind])
                    ind = nx_val - 1 + j * nx_val + base_k
                    if act[ind]:
                        points.append(xyz[ind])
        plopm_info(
            f"computing the {cli_info_value(cfg.distance[0])} distance of "
            f"{cli_info_value(tokens[0])} to the model boundaries"
        )
    show_progress = sys.stdout.isatty()
    if show_progress:
        bar_ctx = alive_bar(ntot * len(points), bar="fish")
    else:
        bar_ctx = nullcontext()
    with bar_ctx as bar_animation:
        for step in unrst.report_steps:
            xyzt = np.copy(xyz)
            var = np.nan * np.ones(nxyz, dtype=float)
            quan0_low = tokens[0]
            quan0_up = tokens[0].upper()
            if quan0_low in ["index_i", "index_j", "index_k"]:
                var[act] = _grid_indices(quan0_low, nx_val, ny_val, nz_val)
            elif unrst.count(quan0_up, step):
                var[act] = 1.0 * unrst[quan0_up, step]
            elif quan0_low in mass_all:
                var[act] = _get_mass(data, quan0_low, step)
            elif quan0_low in ["swat", "soil", "sgas"]:
                var[act] = _get_saturation(data.unrst, quan0_low, step)
            else:
                flag = f"-dist {','.join(cfg.distance)}"
                plopm_error(
                    f"invalid {cli_error_value(f'-v {tokens[0]}')} for "
                    f"{cli_info_value(flag)}."
                )
            if len(tokens) > 1:
                ops = tokens[1::2]
                for j, val in enumerate(tokens[2::2]):
                    val_up = val.upper()
                    if val[0].isdigit() and not val[-1].isdigit():
                        other = 1.0 * unrst[val[1:].upper(), int(val[0])]
                    elif val[0].isdigit() and val[-1].isdigit():
                        other = np.full_like(var[act], float(val))
                    elif init.count(val_up):
                        other = 1.0 * init[val_up, 0]
                        if val_up == "PORV":
                            other = other[act]
                    elif val in ["index_i", "index_j", "index_k"]:
                        var[act] = _grid_indices(val, nx_val, ny_val, nz_val)
                        continue
                    elif unrst.count(val_up, step):
                        other = 1.0 * unrst[val_up, step]
                    elif val in mass_all:
                        other = _get_mass(data, val, step)
                    elif val in ["swat", "soil", "sgas"]:
                        other = _get_saturation(data.unrst, val, step)
                    else:
                        plopm_error(f"not found {cli_error_value(f'-v {val}')}.")
                    var_act = var[act]
                    var[act] = _apply_operator(var_act, other, ops[j])
            else:
                var[var > 0] = 1
            xyzt[var != 1] = np.nan
            temp = np.nan * np.ones(len(points))
            for point_index, point in enumerate(points):
                if show_progress:
                    bar_animation()
                vals = np.linalg.norm(xyzt - point, axis=1)
                if not np.all(np.isnan(vals)):
                    if distance_type == "min":
                        temp[point_index] = np.nanmin(vals)
                    else:
                        temp[point_index] = np.nanmax(vals)
            if not np.isnan(temp).all():
                if distance_type == "min":
                    distance[step] = np.nanmin(temp)
                else:
                    distance[step] = np.nanmax(temp)
    return distance[~np.isnan(distance)], time[~np.isnan(distance)]


def _grid_indices(name: str, nx: int, ny: int, nz: int) -> list:
    """Create one-based grid indices in global cell order.

    Parameters
    ----------
    name : {"index_i", "index_j", "index_k"}
        Grid axis to index.
    nx, ny, nz : int
        Grid dimensions.

    Returns
    -------
    list[int]
        One-based indices for all grid cells.

    """
    nxyz = nx * ny * nz
    if name == "index_i":
        return [(grid_index % nx) + 1 for grid_index in range(nxyz)]
    if name == "index_j":
        return [((grid_index // nx) % ny) + 1 for grid_index in range(nxyz)]
    return [(grid_index // (nx * ny)) + 1 for grid_index in range(nxyz)]


def _aggregate(var: NDArray, op: str, porv: NDArray) -> NDArray:
    """_aggregate values with the selected method.

    Parameters
    ----------
    var : np.ndarray
        Values to _aggregate.
    op : str
        Aggregation method.
    porv : np.ndarray
        Pore-volume weights used by ``"pvmean"``.

    Returns
    -------
    np.ndarray or float
        _aggregated values.

    """
    if op == "min":
        return np.min(var)
    if op == "max":
        return np.max(var)
    if op == "sum":
        return np.sum(var)
    if op == "mean":
        return np.mean(var)
    if op == "pvmean":
        return np.sum(var * porv) / np.sum(porv)
    plopm_error(f"unknow/unsupported aggregation {cli_error_value(f'-agg {op}')}.")


def _read_values(
    cfg: PlopmConfig, data: SimData, tokens: list, n: int, ntot: list
) -> tuple[NDArray, NDArray]:
    """Read an _aggregated time series or grid-axis profile.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized series configuration.
    data : SimData
        Loaded simulation data.
    tokens : list
        Parsed variable-expression tokens.
    n : int
        Plot index.
    ntot : list
        Restart report steps to evaluate.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Values and corresponding time or grid coordinates.

    """
    slide = cfg.slice[n]
    axis_index = slide.index(-1) if -1 in slide else -1
    nx_val = data.nx
    ny_val = data.ny
    nz_val = data.nz
    if axis_index == 0:
        xsize = nx_val
    elif axis_index == 1:
        xsize = ny_val
    elif axis_index == 2:
        xsize = nz_val
    else:
        xsize = 1
    if len(ntot) > 1:
        tsize = len(ntot)
        time = np.array(data.times)
        var = 0.0 * np.ones(tsize)
    else:
        time = np.array(range(xsize), dtype=float)
        var = 0.0 * np.ones(xsize)
    init = data.init
    unrst = data.unrst
    mass_all = cfg.mass_vars + cfg.mass_fracs
    caprock_list = cfg.caprock_vars
    pv_all = data.active_pv
    layer_flag = cfg.layer
    egrid = data.grid
    quan0_low = tokens[0]
    quan0_up = quan0_low.upper()
    ops = tokens[1::2] if len(tokens) > 1 else []
    for output_index, step in enumerate(ntot):
        temp = np.ones(xsize, dtype=float)
        porv = np.ones(xsize, dtype=float)
        inds = [0] * xsize
        if layer_flag:
            if axis_index == 0:
                for index in range(xsize):
                    inds[index] = egrid.active_index(index, slide[1], slide[2])
            elif axis_index == 1:
                for index in range(xsize):
                    inds[index] = egrid.active_index(slide[0], index, slide[2])
            elif axis_index == 2:
                for index in range(xsize):
                    inds[index] = egrid.active_index(slide[0], slide[1], index)
        else:
            ind0 = egrid.active_index(slide[0], slide[1], slide[2])
            for index in range(xsize):
                inds[index] = ind0
        if quan0_low in mass_all:
            arr_main = _get_mass(data, quan0_low, step)
        elif quan0_low in caprock_list:
            arr_main, _ = _get_caprock(data, quan0_low, step, cfg.stress_coefficient)
        elif quan0_low in ["swat", "soil", "sgas"]:
            arr_main = _get_saturation(data.unrst, quan0_low, step)
        else:
            arr_main = None
        if len(tokens) > 1:
            arr_vals = []
            for val in tokens[2::2]:
                if val in mass_all:
                    arr_vals.append(_get_mass(data, val, step))
                elif val in caprock_list:
                    arr, _ = _get_caprock(data, val, step, cfg.stress_coefficient)
                    arr_vals.append(arr)
                elif val in ["swat", "soil", "sgas"]:
                    arr_vals.append(_get_saturation(data.unrst, val, step))
                else:
                    arr_vals.append(np.full_like(temp, np.nan))
        inds_arr = np.array(inds)

        if unrst.count("RPORV", step):
            porv = unrst["RPORV", step][inds_arr]
        else:
            porv = pv_all[inds_arr]

        if unrst.count(quan0_up, step):
            temp = 1.0 * unrst[quan0_up, step][inds_arr]
            # porv-weighted pressure for the dual model
            if cfg.dual_grid[n] == "1" and cfg.sensor:
                indd = egrid.active_index(
                    slide[0], slide[1] + int((data.ny - 1) / 2) + 1, slide[2]
                )
                presd = unrst[quan0_up, step][indd]
                if unrst.count("RPORV", step):
                    porvd = unrst["RPORV", step][indd]
                else:
                    porvd = pv_all[indd]
                temp = (temp * porv + presd * porvd) / (porv + porvd)
        elif init.count(quan0_up):
            temp = 1.0 * init[quan0_up, 0][inds_arr]
        elif arr_main is not None:
            temp = arr_main[inds_arr]
        else:
            plopm_error(f"not found {cli_error_value(f'-v {tokens[0]}')}.")

        if len(tokens) > 1:
            for j, val in enumerate(tokens[2::2]):
                val_up = val.upper()
                arr_val = arr_vals[j]
                if val[0].isdigit() and not val[-1].isdigit():
                    other = 1.0 * unrst[val[1:].upper(), int(val[0])][inds_arr]
                elif val[0].isdigit() and val[-1].isdigit():
                    other = np.full_like(temp, float(val))
                elif init.count(val_up):
                    other = 1.0 * init[val_up, 0][inds_arr]
                elif unrst.count(val_up, step):
                    other = 1.0 * unrst[val_up, step][inds_arr]
                elif not np.isnan(arr_val).all():
                    other = arr_val[inds_arr]
                else:
                    plopm_error(f"not found {cli_error_value(f'-v {val}')}.")
                temp = _apply_operator(temp, other, ops[j])
        ll = np.arange(xsize) + output_index
        if cfg.aggregation[0]:
            var[output_index] = _aggregate(temp, cfg.aggregation[0], porv)
        elif layer_flag:
            var = temp
        else:
            if xsize == 1:
                var[ll] = temp[0]
            else:
                var[ll] = temp
    if layer_flag and not cfg.aggregation[0]:
        xyz_func = egrid.xyz_from_ijk
        if axis_index == 0:
            for i in range(nx_val):
                time[i] = np.mean(xyz_func(i, slide[1], slide[2], True), axis=1)[0]
        elif axis_index == 1:
            for j in range(ny_val):
                time[j] = np.mean(xyz_func(slide[0], j, slide[2], True), axis=1)[1]
        else:
            for k in range(nz_val):
                time[k] = np.mean(xyz_func(slide[0], slide[1], k, True), axis=1)[2]
    return var, time


def read_series(
    cfg: PlopmConfig, case: str, values: str, tunit: str, qskl: float, n: int
) -> tuple[NDArray, NDArray, str, str]:
    """Read one one-dimensional series for plotting.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized series configuration.
    case : str
        Simulation-case stem or CSV path.
    values : str
        Variable name or expression.
    tunit : str
        Requested time-unit code.
    qskl : float
        Scale factor applied to values.
    n : int
        Plot or case index.

    Returns
    -------
    tuple[np.ndarray, np.ndarray, str, str]
        Coordinates, values, coordinate unit, and value unit.

    """
    time, vunit = np.array([0, 1]), ""
    tskl, tunit = time_unit(tunit)
    tokens = values.split(" ")
    csv_flag = cfg.csv_columns[n][0]
    q0_low = tokens[0]
    use_sw = "krw" in "".join(cfg.variables)
    if csv_flag:
        csvv = np.genfromtxt(f"{case}.csv", delimiter=",", skip_header=1)
        col_t = cfg.csv_columns[n][0] - 1
        col_v = cfg.csv_columns[n][1] - 1
        time = tskl * csvv[:, col_t] / 86400.0
        var = csvv[:, col_v]
    elif cfg.distance[0]:
        xskl, xunit = spatial_unit(cfg.xunits)
        data = read_case(
            case, cfg.gif, cfg.vtk, cfg.variables, cfg.restart, cfg.filters
        )
        var, time = _compute_distance(cfg, data, tokens, n)
        vunit = f" ({cfg.distance[0]} distance to {cfg.distance[1]} in {xunit})"
        var *= xskl
    elif cfg.histogram[0]:
        data = read_case(
            case, cfg.gif, cfg.vtk, cfg.variables, cfg.restart, cfg.filters
        )
        var = _read_histogram(cfg, data, tokens, data.steps[0])
        tunit = ""
    elif cfg.sensor or cfg.aggregation[0]:
        data = read_case(
            case, cfg.gif, cfg.vtk, cfg.variables, cfg.restart, cfg.filters
        )
        var, time = _read_values(cfg, data, tokens, n, data.unrst.report_steps)
        time *= tskl
        if tunit == "Dates":
            dates = []
            unrst = data.unrst

            for step in range(len(unrst)):
                intehead = unrst["INTEHEAD", step]
                dates.append(
                    datetime.date(
                        year=int(intehead[66]),
                        month=int(intehead[65]),
                        day=int(intehead[64]),
                    )
                )

            time = np.asarray(dates)
    elif cfg.layer:
        xskl, tunit = spatial_unit(cfg.xunits)
        data = read_case(
            case, cfg.gif, cfg.vtk, cfg.variables, cfg.restart, cfg.filters
        )
        tmp = data.steps[n] if n < len(cfg.restart) else data.steps[0]
        var, time = _read_values(cfg, data, tokens, n, [tmp])
        time *= xskl
    elif q0_low[:3] in ["krw", "krg"] or q0_low[:4] in [
        "krog",
        "krow",
        "pcow",
        "pcog",
        "pcwg",
    ]:
        snu = 1
        hyst = False
        if q0_low[-1] == "h":
            hyst = True
            q0_low = tokens[0][:-1]
        if len(q0_low) == 3:
            what = q0_low[:3]
        elif q0_low in ["krow", "krog", "pcow", "pcog", "pcwg"]:
            what = q0_low[:4]
        elif q0_low[:3] in ["krw", "krg"]:
            what = q0_low[:3]
            snu = int(tokens[0][3:])
        else:
            what = q0_low[:4]
            snu = int(tokens[0][4:])
        if not os.path.isfile(f"{case}.INIT"):
            plopm_error(
                f"Missing {cli_error_value(f'{case}.INIT')}, required by "
                f"{cli_info_value(f'-v {q0_low}')}."
            )
        init = OpmFile(f"{case}.INIT")
        tabdim = init["TABDIMS"]
        table = np.array(init["TAB"])
        nswe = tabdim[24]
        nsnum = tabdim[25]
        vunit = ""
        if what == "krg":
            tunit = "s$_w$ [-]" if use_sw else "s$_g$ [-]"
            sht = tabdim[23] - 1
            base = sht + (snu - 1) * nswe
            time = table[base : base + nswe]
            time = time[time <= 1.0]
            count_v = len(time)
            var = table[
                sht + nswe * nsnum + (snu - 1) * nswe : sht + nswe * nsnum + snu * nswe
            ][:count_v]
            if hyst:
                base2 = sht + (nsnum // 2 + snu - 1) * nswe
                timeh = table[base2 : base2 + nswe]
                timeh = timeh[timeh <= 1.0]
                count_v = len(timeh)
                var = np.append(
                    var,
                    np.flip(
                        table[
                            sht
                            + nswe * nsnum
                            + (nsnum // 2 + snu - 1) * nswe : sht
                            + nswe * nsnum
                            + (nsnum // 2 + snu) * nswe
                        ][:count_v]
                    ),
                )
                time = np.append(time, np.flip(timeh))
            if use_sw:
                time = 1.0 - time
        elif what == "krow":
            nswe = tabdim[21]
            tunit = "s$_w$ [-]"
            sht = tabdim[26] - 1
            base = sht + (snu - 1) * nswe
            time = table[base : base + nswe]
            time = time[time <= 1.0]
            count_v = len(time)
            if tabdim[22] == 2:
                sht += nswe
            var = np.flip(
                table[
                    sht
                    + nswe * nsnum
                    + (snu - 1) * nswe : sht
                    + nswe * nsnum
                    + snu * nswe
                ][:count_v]
            )
        elif what == "krw":
            nswe = tabdim[21]
            tunit = "s$_w$ [-]"
            sht = tabdim[20] - 1
            base = sht + (snu - 1) * nswe
            time = table[base : base + nswe]
            time = time[time <= 1.0]
            count_v = len(time)
            var = table[
                sht + nswe * nsnum + (snu - 1) * nswe : sht + nswe * nsnum + snu * nswe
            ][:count_v]
            if hyst:
                base2 = sht + (nsnum // 2 + snu - 1) * nswe
                timeh = table[base2 : base2 + nswe]
                timeh = timeh[timeh <= 1.0]
                count_v = len(timeh)
                var = np.append(
                    np.flip(var),
                    table[
                        sht
                        + nswe * nsnum
                        + (nsnum // 2 + snu - 1) * nswe : sht
                        + nswe * nsnum
                        + (nsnum // 2 + snu) * nswe
                    ][:count_v],
                )
                time = np.append(np.flip(time), timeh)
        elif what == "pcow":
            nswe = tabdim[21]
            tunit = "s$_w$ [-]"
            sht = tabdim[20] - 1
            base = sht + (snu - 1) * nswe
            time = table[base : base + nswe]
            time = time[time <= 1.0]
            count_v = len(time)
            var = table[
                sht
                + 2 * nswe * nsnum
                + (snu - 1) * nswe : sht
                + 2 * nswe * nsnum
                + snu * nswe
            ][:count_v]
        else:
            tunit = "s$_g$ [-]"
            sht = tabdim[23] - 1
            base = sht + (snu - 1) * nswe
            time = table[base : base + nswe]
            time = time[time <= 1.0]
            count_v = len(time)
            var = table[
                sht
                + 2 * nswe * nsnum
                + (snu - 1) * nswe : sht
                + 2 * nswe * nsnum
                + snu * nswe
            ][:count_v]
    elif values[:6] == "pcfact" or values[:8] == "permfact":
        cap = 6 if values[:6] == "pcfact" else 8
        snu = int(tokens[0][cap:]) if not values in ["pcfact", "permfact"] else 1
        tmp0 = []
        tmp2 = []
        found = False
        vec = tokens[0].upper()[:cap]
        file_name = _find_keyword(case, vec)
        count = 0
        with open(file_name, "r", encoding="utf8") as file:
            for row in csv.reader(file, delimiter=" "):
                if len(row) > 0:
                    if row[0] == vec:
                        found = True
                    if count == snu:
                        break
                    if (
                        len(row) > 1
                        and row[0].strip() != "--"
                        and found
                        and count == snu - 1
                    ):
                        tmp0.append(float(row[0]))
                        tmp2.append(float(row[1]))
                        if len(row) > 2 and row[2].strip() == "/":
                            break
                    if (
                        found
                        and row[0] == "/"
                        or len(row) > 2
                        and row[2].strip() == "/"
                    ):
                        count += 1
        if not tmp2:
            plopm_error(f"not found {cli_error_value(f'-v {tokens[0]}')}.")
        var = np.array(tmp2)
        time = np.array(tmp0)
    else:
        summary = OpmSummary(f"{case}.SMSPEC")
        key = tokens[0].upper()
        keys = summary.keys()
        if tokens[0] in cfg.summary_mass:
            var = summary[key[:-1]]
        elif key in summary:
            var = summary[key]
        else:
            plopm_error(f"no {cli_error_value(f'-v {tokens[0]}')} found.")
        if len(tokens) > 1:
            ops = tokens[1::2]
            for index, val in enumerate(tokens[2::2]):
                if val.upper() in keys:
                    other = summary[val.upper()]
                else:
                    other = float(val)
                var = _apply_operator(var, other, ops[index])
        if tunit == "Dates":
            smsp_dates = 86400 * summary["TIME"]
            time = np.array(
                [
                    summary.start_date + datetime.timedelta(seconds=float(sec))
                    for sec in smsp_dates
                ]
            )
        else:
            time = summary["TIME"] * tskl
    if tokens[0] in ["fgip", "fgit"]:
        vunit = " [sm$^3$]"
    elif tokens[0] in cfg.summary_mass:
        var *= GAS_DEN_REF
        vunit = mass_unit(qskl)
    elif tokens[0] in ["time"]:
        vunit = " [d]"
    return time, var * qskl, tunit, vunit


def _find_keyword(case: str, vec: str) -> str:
    """Find the deck file containing an OPM keyword.

    Parameters
    ----------
    case : str
        Simulation-case stem.
    vec : str
        OPM keyword to locate.

    Returns
    -------
    str
        DATA or included file containing the keyword.

    """
    include = False
    path = ""
    parts = case.split("/")
    if len(parts) > 1:
        path = "/".join(parts[:-1]) + "/"
    case_file = case + ".DATA"
    includes = []
    with open(case_file, "r", encoding="utf8") as file:
        for row in csv.reader(file):
            if not row:
                continue
            val = row[0]
            if val == vec:
                return case_file
            if val == "INCLUDE":
                include = True
                continue
            if include:
                name = val.split("/")[0].strip(" ")
                if "'" in name:
                    name = name[1:-1]
                full = path + name
                if os.path.isfile(full):
                    includes.append(full)
                include = False
    for include_file in includes:
        with open(include_file, "r", encoding="utf8") as file:
            for row in csv.reader(file):
                if not row:
                    continue
                if row[0] == vec:
                    return include_file
    files = case_file
    if len(includes) > 1:
        if len(includes) == 1:
            files += f" and {includes[0]}"
        else:
            files += ", "
            files += ", ".join(includes[:-1])
            files += f" and {includes[-1]}"
    plopm_error(f"not found keyword {cli_error_value(f'-v {vec}')} " f"in {files}.")


def _apply_operator(
    var: NDArray[np.float64], other: NDArray[np.float64], op: str
) -> NDArray[np.float64]:
    """Apply an arithmetic or comparison operator.

    Parameters
    ----------
    var, other : np.ndarray
        Left- and right-hand values.
    op : str
        Arithmetic or comparison operator.

    Returns
    -------
    np.ndarray
        Operation result. Failed comparisons are NaN.

    """
    if op == "+":
        return var + other
    if op == "-":
        return var - other
    if op == "*":
        return var * other
    if op == "/":
        return var / other
    mask = ~np.isnan(var)
    qmask = ~np.isnan(other)
    mask = mask & qmask
    if op == "==":
        var[mask] = np.where(var[mask] == other[mask], 1.0, np.nan)
    elif op == ">=":
        var[mask] = np.where(var[mask] >= other[mask], 1.0, np.nan)
    elif op == "<=":
        var[mask] = np.where(var[mask] <= other[mask], 1.0, np.nan)
    elif op == "<":
        var[mask] = np.where(var[mask] < other[mask], 1.0, np.nan)
    elif op == ">":
        var[mask] = np.where(var[mask] > other[mask], 1.0, np.nan)
    elif op == "!=":
        var[mask] = np.where(var[mask] != other[mask], 1.0, np.nan)
    else:
        plopm_error(f"unknow operation {cli_error_value(f'-v {op}')}.")
    return var


def time_unit(times: str) -> tuple[float, str]:
    """Get the conversion and label for a time unit.

    Parameters
    ----------
    times : str
        Time-unit code or ``"dates"``.

    Returns
    -------
    tuple[float, str]
        Factor converting OPM days and the axis label.

    """
    if times == "s":
        return 86400.0, "Time [seconds]"
    if times == "m":
        return 1440.0, "Time [minutes]"
    if times == "h":
        return 24.0, "Time [hours]"
    if times == "d":
        return 1.0, "Time [days]"
    if times == "w":
        return 0.14285714285714285, "Time [weeks]"
    if times == "y":
        return 0.002737909255898758, "Time [years]"
    if times == "dates":
        return 1, "Dates"
    return 86400.0, "Time [seconds]"


def read_csv_grid(
    cfg: PlopmConfig, deck: str, n: int
) -> tuple[NDArray, NDArray, int, int, str, str]:
    """Read coordinate meshes from a regular CSV grid.

    Parameters
    ----------
    cfg : PlopmConfig
        CSV column and animation configuration.
    deck : str
        CSV path without the extension.
    n : int
        Map index.

    Returns
    -------
    tuple
        Coordinate meshes, dimensions, and axis names.

    """
    if cfg.gif:
        file_name = deck.replace("PLOPM", str(cfg.restart[0]))
    else:
        file_name = deck
    csvv = np.genfromtxt(f"{file_name}.csv", delimiter=",", skip_header=1)
    col_x = cfg.csv_columns[n][0] - 1
    col_y = cfg.csv_columns[n][1] - 1
    x0 = csvv[0, col_x]
    x1 = csvv[-1, col_x]
    y0 = csvv[0, col_y]
    y1 = csvv[-1, col_y]
    x = x1 + x0
    y = y1 + y0
    mx = round(x / (2.0 * x0))
    my = round(y / (2.0 * y0))
    xname = "x"
    yname = "y"
    xmx = np.linspace(0, x, mx + 1)
    ymy = np.linspace(0, y, my + 1)
    return xmx[None, :], ymy[::-1][:, None], mx, my, xname, yname


def _apply_filter(porvs: NDArray, other: NDArray, op: str, value: float) -> NDArray:
    """Apply a comparison filter to pore-volume values.

    Parameters
    ----------
    porvs : np.ndarray
        Pore-volume values.
    other : np.ndarray
        Values tested by the filter.
    op : str
        Comparison operator.
    value : float
        Comparison threshold.

    Returns
    -------
    np.ndarray
        Pore volume where the condition is true and zero elsewhere.

    """
    if op == "==":
        mask = other == value
    elif op == ">=":
        mask = other >= value
    elif op == "<=":
        mask = other <= value
    elif op == "<":
        mask = other < value
    elif op == ">":
        mask = other > value
    elif op == "!=":
        mask = other != value
    else:
        plopm_error(f"unknow filter operation {cli_error_value(f'-flt {op}')}.")
    return np.where(mask, porvs, 0)


def get_unit(name: str) -> str:
    """Get the display unit for a variable.

    Parameters
    ----------
    name : str
        Variable name.

    Returns
    -------
    str
        Matplotlib-formatted unit label.

    """
    name_low = name.lower()
    if name_low in {"disperc", "depth", "dx", "dy", "dz"}:
        return " [m]"
    if name_low in {"porv", "fgip", "fgit"}:
        return r" [sm$^3$]"
    if name_low in {"permx", "permy", "permz"}:
        return " [mD]"
    if name_low in {"tranx", "trany", "tranz"}:
        return " [cP rm$^3$/ (day bar)]"
    if name_low in {"pressure", "rpr", "fpr", "fprr", "wbhp"}:
        return " [bar]"
    return " [-]"


def read_quantity(
    deck: str,
    data: SimData,
    name: str,
    step: int,
    scale: float,
    mass: list[str],
    mass_all: list[str],
    caprock: list[str],
    stress: float,
    filters: str,
    isgif: bool,
    vmin: str,
    vmax: str,
    cvs: list,
) -> tuple[str, NDArray]:
    """Read and transform one spatial or VTK quantity.

    Parameters
    ----------
    deck : str
        Simulation-case stem or CSV path.
    data : SimData
        Loaded simulation data.
    name : str
        Variable name or expression.
    step : int
        Restart report step.
    scale : float
        Scale factor applied to derived values.
    mass, mass_all, caprock : list[str]
        Supported derived-variable groups.
    stress : float
        Stress coefficient for caprock quantities.
    filters : str
        Property-filter expression.
    isgif : bool
        Whether the CSV path contains a restart placeholder.
    vmin, vmax : str
        Optional value thresholds.
    cvs : list
        CSV input and column settings.

    Returns
    -------
    tuple[str, np.ndarray]
        Unit label and quantity values.

    """
    names = name.split(" ")
    unit = get_unit(name)
    name0_low = names[0]
    name0 = name0_low.upper()
    if cvs[0]:
        if isgif:
            file_name = deck.replace("PLOPM", str(step))
        else:
            file_name = deck
        csvv = np.genfromtxt(f"{file_name}.csv", delimiter=",", skip_header=1)
        col = cvs[2] - 1
        values = csvv[:, col]
    else:
        if data.init.count(name0):
            values = np.array(data.init[name0], dtype=float)
            if name0_low == "porv":
                values = data.active_pv
        elif name0_low in ["wells", "faults", "grid"]:
            values = np.zeros_like(data.init["SATNUM"])
        elif name0_low in ["index_i", "index_j", "index_k"]:
            values = np.array(
                _grid_indices(name0_low, data.nx, data.ny, data.nz), dtype=float
            )
            values = values[data.porv > 0]
        elif data.unrst.count(name0, step):
            values = data.unrst[name0, step]
            if data.unrst.count("RPORV", step):
                if filters:
                    porv0 = np.array(data.init["PORV"])
                    mask = porv0 > 0
                    base_rporv = np.array(data.unrst["RPORV", step])
                    for value in filters.split("&"):
                        filte = value.strip().split(" ")
                        key = filte[0].upper()
                        if data.init.count(key):
                            q1 = np.array(data.init[key])
                        elif data.unrst.count(key, step):
                            q1 = np.array(data.unrst[key, step])
                        else:
                            plopm_error(
                                f"unknow filter quantity {cli_error_value(f'-flt {key}')}."
                            )
                        base_rporv = _apply_filter(
                            base_rporv, q1, filte[1], float(filte[2])
                        )
                    data.porv[mask] = base_rporv
                else:
                    data.porv[data.porv > 0] = np.array(data.unrst["RPORV", step])
        elif name0_low in mass_all:
            values = _get_mass(data, name0_low, step) * scale
            if name0_low in mass:
                unit = mass_unit(scale)
        elif name0_low in caprock:
            values, unit = _get_caprock(data, name0_low, step, stress)
        elif name0_low in ["swat", "soil", "sgas"]:
            values = _get_saturation(data.unrst, name0_low, step) * scale
        else:
            plopm_error(f"not found {cli_error_value(f'-v {name0}')}.")
        if len(names) > 1:
            ops = names[1::2]
            for j, val in enumerate(names[2::2]):
                if val[0].isdigit() and not val[-1].isdigit():
                    q1 = data.unrst[val[1:].upper(), int(val[0])]
                elif val[0].isdigit() and val[-1].isdigit():
                    q1 = np.full_like(values, float(val))
                elif data.init.count(val.upper()):
                    q1 = np.array(data.init[val.upper()])
                    if val.upper() == "PORV":
                        q1 = q1[data.porv > 0]
                elif val in ["index_i", "index_j", "index_k"]:
                    q1 = np.array(
                        _grid_indices(val, data.nx, data.ny, data.nz),
                        dtype=float,
                    )
                    q1 = q1[data.porv > 0]
                elif data.unrst.count(val.upper(), step):
                    q1 = data.unrst[val.upper(), step]
                elif val in mass_all:
                    q1 = _get_mass(data, val, step) * scale
                elif val in caprock:
                    q1, unit = _get_caprock(data, val, step, stress)
                else:
                    plopm_error(f"not found {cli_error_value(f'-v {val}')}.")
                values = _apply_operator(values, q1, ops[j])
    if vmin:
        values = np.asarray(values)
        values[values < float(vmin)] = np.nan
    if vmax:
        values = np.asarray(values)
        values[values > float(vmax)] = np.nan
    return unit, values


def _get_saturation(unrst: OpmRestart, name: str, step: int) -> NDArray:
    """Derive a missing phase saturation.

    Parameters
    ----------
    unrst : OpmRestart
        UNRST reader.
    name : {"soil", "swat", "sgas"}
        Saturation to derive.
    step : int
        Restart report step.

    Returns
    -------
    np.ndarray
        Requested phase saturation.

    """
    if unrst.count("SOIL", step):
        soil = np.array(unrst["SOIL", step])
    else:
        soil = np.array(0)
    if unrst.count("SGAS", step):
        sgas = np.array(unrst["SGAS", step])
    else:
        sgas = np.array(0)
    if unrst.count("SWAT", step):
        swat = np.array(unrst["SWAT", step])
    else:
        swat = np.array(0)
    if name == "soil":
        return 1 - sgas - swat
    if name == "swat":
        return 1 - sgas - soil
    return 1 - soil - swat


def _get_mass(data: SimData, name: str, step: int) -> NDArray:
    """Compute component masses and mass fractions.

    Parameters
    ----------
    data : SimData
        Loaded restart data and pore volume.
    name : str
        Requested derived variable.
    step : int
        Restart report step.

    Returns
    -------
    np.ndarray
        Requested component quantity.

    """
    sgas = np.array(data.unrst["SGAS", step])
    rhog = np.array(data.unrst["GAS_DEN", step])
    rhow = np.array(data.unrst["WAT_DEN", step])
    if data.unrst.count("RSW", step):
        rsw = np.array(data.unrst["RSW", step])
    else:
        rsw = np.zeros_like(sgas)
    if data.unrst.count("RVW", step):
        rvw = np.array(data.unrst["RVW", step])
    else:
        rvw = np.zeros_like(sgas)
    if data.unrst.count("RPORV", step):
        rpv = np.array(data.unrst["RPORV", step])
    else:
        rpv = data.active_pv
    denom_l = rsw + WAT_DEN_REF / GAS_DEN_REF
    denom_g = rvw + GAS_DEN_REF / WAT_DEN_REF
    x_l_co2 = np.zeros_like(rsw)
    x_g_h2o = np.zeros_like(rvw)
    mask_l = denom_l != 0
    mask_g = denom_g != 0
    x_l_co2[mask_l] = rsw[mask_l] / denom_l[mask_l]
    x_g_h2o[mask_g] = rvw[mask_g] / denom_g[mask_g]
    inv_sgas = 1.0 - sgas
    inv_xg = 1.0 - x_g_h2o
    inv_xl = 1.0 - x_l_co2
    co2_g = inv_xg * sgas * rhog * rpv
    co2_d = x_l_co2 * inv_sgas * rhow * rpv
    h2o_l = inv_xl * inv_sgas * rhow * rpv
    h2o_v = x_g_h2o * sgas * rhog * rpv
    return _select_mass(name, co2_g, co2_d, h2o_l, h2o_v, x_l_co2, x_g_h2o)


def _select_mass(
    name: str,
    co2_g: NDArray,
    co2_d: NDArray,
    h2o_l: NDArray,
    h2o_v: NDArray,
    x_l_co2: NDArray,
    x_g_h2o: NDArray,
) -> NDArray:
    """Select a mass or mass-fraction result by name.

    Parameters
    ----------
    name : str
        Requested derived variable.
    co2_g, co2_d : np.ndarray
        Free and dissolved CO2 masses.
    h2o_l, h2o_v : np.ndarray
        Liquid and vapor water masses.
    x_l_co2, x_g_h2o : np.ndarray
        CO2-in-liquid and water-in-gas mass fractions.

    Returns
    -------
    np.ndarray
        Selected mass or mass fraction.

    """
    if name == "gasm":
        return co2_g
    if name == "dism":
        return co2_d
    if name == "liqm":
        return h2o_l
    if name == "vapm":
        return h2o_v
    if name == "h2om":
        return h2o_v + h2o_l
    if name == "xco2l":
        return x_l_co2
    if name == "xh2ov":
        return x_g_h2o
    if name == "xco2v":
        return 1 - x_g_h2o
    if name == "xh2ol":
        return 1 - x_l_co2
    return co2_g + co2_d


def _get_caprock(
    data: SimData, name: str, step: int, stress: float
) -> tuple[NDArray, str]:
    """Compute a caprock-integrity quantity.

    Parameters
    ----------
    data : SimData
        Loaded static and restart properties.
    name : str
        Requested caprock variable.
    step : int
        Restart report step.
    stress : float
        Vertical stress coefficient.

    Returns
    -------
    tuple[np.ndarray, str]
        Computed values and unit label.

    """
    init = data.init
    unrst = data.unrst
    dz = np.array(init["DZ", 0])
    depth = np.array(init["DEPTH", 0])
    dz_half = 0.5 * dz
    dz_corr = 0.5 * dz
    if unrst.count("WAT_DEN", 0) and unrst.count("WAT_DEN", step):
        den0 = np.array(unrst["WAT_DEN", 0])
        den1 = np.array(unrst["WAT_DEN", step])
    else:
        den0 = np.array(1000.0)
        den1 = np.array(1000.0)
    fac = 9.81 / 1e5
    pz_c0 = fac * dz_corr * den0
    pz_c1 = fac * dz_corr * den1
    pressure0 = np.array(unrst["PRESSURE", 0])
    pressure1 = np.array(unrst["PRESSURE", step])
    limipres = stress * (depth - dz_half)
    overpres = limipres - (pressure1 - pz_c1)
    limipres -= pressure0 - pz_c0
    objepres = np.zeros_like(overpres)
    mask = limipres != 0
    objepres[mask] = overpres[mask] / limipres[mask]
    if name == "limipres":
        return limipres, " [bar]"
    if name == "overpres":
        return -overpres, " [bar]"
    return objepres, " [-]"


def get_wells(cfg: PlopmConfig, n: int) -> tuple[list, list]:
    """Read wells intersecting the selected slice.

    Parameters
    ----------
    cfg : PlopmConfig
        Case and slice configuration.
    n : int
        Case index.

    Returns
    -------
    tuple[list, list[str]]
        Completion intervals grouped by well and the well names.

    """
    wells: list[list[list[int]]] = []
    lwells: list[str] = []
    well_map = {}
    haswells = False
    sources = False
    with open(f"{cfg.cases[0][n]}.DATA", "r", encoding="utf8") as file:
        for row in csv.reader(file):
            if not row:
                continue
            tokens = row[0].split()
            if not tokens:
                continue
            key = tokens[0]
            if key == "COMPDAT":
                haswells = True
                continue
            if key == "SOURCE":
                sources = True
                continue
            if key == "/":
                haswells = False
                sources = False
                continue
            if key.startswith("--"):
                continue
            if haswells:
                if len(tokens) < 5:
                    continue
                wname = tokens[0]
                if wname not in well_map:
                    well_map[wname] = len(lwells)
                    lwells.append(wname)
                    wells.append([])
                idx = well_map[wname]
                wells[idx].append(
                    [
                        int(tokens[1]) - 1,
                        int(tokens[2]) - 1,
                        int(tokens[3]) - 1,
                        int(tokens[4]) - 1,
                    ]
                )
            elif sources:
                if len(tokens) < 3:
                    continue
                wname = tokens[0]
                if wname not in well_map:
                    well_map[wname] = len(lwells)
                    lwells.append(wname)
                    wells.append([])
                idx = well_map[wname]
                wells[idx].append(
                    [
                        int(tokens[0]) - 1,
                        int(tokens[1]) - 1,
                        int(tokens[2]) - 1,
                        int(tokens[2]) - 1,
                    ]
                )
    if not cfg.global_range:
        sld_x = cfg.slice[n][0]
        sld_y = cfg.slice[n][1]
        sld_z = cfg.slice[n][2]
        whow = cfg.slice_mode
        for i, wells_list in enumerate(wells):
            for j, well in enumerate(wells_list):
                if not well:
                    continue
                keep = True
                if sld_x[0] > -1:
                    val = well[0]
                    if whow == "min":
                        keep = sld_x[0] <= val < sld_x[1]
                    else:
                        keep = val == sld_x[0]
                elif sld_y[0] > -1:
                    val = well[1]
                    if whow == "min":
                        keep = sld_y[0] <= val < sld_y[1]
                    else:
                        keep = val == sld_y[0]
                else:
                    z0, z1 = well[2], well[3]
                    if whow == "min":
                        keep = not (sld_z[1] < z0 or sld_z[0] > z1)
                    else:
                        keep = sld_z[0] >= z0 and sld_z[0] <= z1
                if not keep:
                    wells[i][j] = []
    return wells, lwells


def get_faults(cfg: PlopmConfig, n: int) -> tuple[list, list]:
    """Read faults intersecting the selected slice.

    Parameters
    ----------
    cfg : PlopmConfig
        Case and slice configuration.
    n : int
        Case index.

    Returns
    -------
    tuple[list, list[str]]
        Grid segments grouped by fault and the fault names.

    """
    faults: list[list[list[int]]] = []
    lfaults: list[str] = []
    fault_map = {}
    hasfaults = False
    with open(f"{cfg.cases[0][n]}.DATA", "r", encoding="utf8") as file:
        for row in csv.reader(file):
            if not row:
                continue
            tokens = row[0].split()
            if not tokens:
                continue
            key = tokens[0]
            if key == "FAULTS":
                hasfaults = True
                continue
            if hasfaults:
                if key.startswith("--"):
                    continue
                if "/" in key:
                    break
                if len(tokens) < 7:
                    continue
                fname = key
                if fname not in fault_map:
                    fault_map[fname] = len(lfaults)
                    lfaults.append(fname)
                    faults.append([])
                idx = fault_map[fname]
                faults[idx].append(
                    [
                        int(tokens[1]) - 1,
                        int(tokens[3]) - 1,
                        int(tokens[5]) - 1,
                        int(tokens[6]) - 1,
                    ]
                )
    if not cfg.global_range:
        sld_x = cfg.slice[n][0]
        sld_y = cfg.slice[n][1]
        sld_z = cfg.slice[n][2]
        whow = cfg.slice_mode
        for i, flist in enumerate(faults):
            for j, fault in enumerate(flist):
                if not fault:
                    continue
                keep = True
                if sld_x[0] > -1:
                    val = fault[0]
                    if whow == "min":
                        keep = sld_x[0] <= val < sld_x[1]
                    else:
                        keep = val == sld_x[0]
                elif sld_y[0] > -1:
                    val = fault[1]
                    if whow == "min":
                        keep = sld_y[0] <= val < sld_y[1]
                    else:
                        keep = val == sld_y[0]
                else:
                    z0, z1 = fault[2], fault[3]
                    if whow == "min":
                        keep = not (sld_z[1] < z0 or sld_z[0] > z1)
                    else:
                        keep = sld_z[0] >= z0 and sld_z[0] <= z1
                if not keep:
                    faults[i][j] = []
    return faults, lfaults
