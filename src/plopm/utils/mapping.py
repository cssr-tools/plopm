# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1702,R0912,C0325,R0913,R0914,R0915,R0917

"""Prepare slice geometry and map three-dimensional values to two dimensions.

The module builds labels and coordinate meshes for xy, xz, and yz slices,
applies optional rotation and translation, and aggregates active-cell values
through the selected grid interval.
"""

import numpy as np
from numpy.typing import NDArray

from plopm.config.config import PlopmConfig, SimData
from plopm.utils.readers import get_xy_coords, get_xz_coords, get_yz_coords


def get_yz_slice(
    cfg: PlopmConfig, data: SimData, n: int
) -> tuple[NDArray, NDArray, str, str, int, int, str, str]:
    """Prepare geometry and labels for a yz slice.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized map and slice configuration.
    data : SimData
        Loaded grid data.
    n : int
        Slice index.

    Returns
    -------
    tuple
        Coordinate meshes, display and filename slice labels, mapped grid
        dimensions, and coordinate-axis names.

    """
    slide_range = cfg.slice[n][0]
    nx = data.nx
    if slide_range[0] == ":":
        cfg.slice[n][0] = [0, nx]
        slice_title = f", slide i=0:{nx}"
        slice_name = f"0:{nx},j,k"
    elif slide_range[0] == slide_range[1] - 1:
        start_index = slide_range[0] + 1
        slice_title = f", slide i={start_index}"
        slice_name = f"{start_index},j,k"
    else:
        start_index = slide_range[0] + 1
        end_index = slide_range[1]
        slice_title = f", slide i={start_index}:{end_index}"
        slice_name = f"{start_index}:{end_index},j,k"
    xc, yc = get_yz_coords(cfg, data, n)
    mx = 2 * data.ny - 1
    my = 2 * data.nz - 1
    xname = "y"
    yname = "z"
    return xc, yc, slice_title, slice_name, mx, my, xname, yname


def get_xz_slice(
    cfg: PlopmConfig, data: SimData, n: int
) -> tuple[NDArray, NDArray, str, str, int, int, str, str]:
    """Prepare geometry and labels for an xz slice.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized map and slice configuration.
    data : SimData
        Loaded grid data.
    n : int
        Slice index.

    Returns
    -------
    tuple
        Coordinate meshes, display and filename slice labels, mapped grid
        dimensions, and coordinate-axis names.

    """
    slide_range = cfg.slice[n][1]
    ny = data.ny
    if slide_range[0] == ":":
        cfg.slice[n][1] = [0, ny]
        slice_title = f", slide j=0:{ny}"
        slice_name = f"i,0:{ny},k"
    elif slide_range[0] == slide_range[1] - 1:
        start_index = slide_range[0] + 1
        slice_title = f", slide j={start_index}"
        slice_name = f"i,{start_index},k"
    else:
        start_index = slide_range[0] + 1
        end_index = slide_range[1]
        slice_title = f", slide j={start_index}:{end_index}"
        slice_name = f"i,{start_index}:{end_index},k"
    xc, yc = get_xz_coords(cfg, data, n)
    mx = 2 * data.nx - 1
    my = 2 * data.nz - 1
    xname = "x"
    yname = "z"
    return xc, yc, slice_title, slice_name, mx, my, xname, yname


def get_xy_slice(
    cfg: PlopmConfig, data: SimData, n: int
) -> tuple[NDArray, NDArray, str, str, int, int, str, str]:
    """Prepare geometry and labels for an xy slice.

    Parameters
    ----------
    cfg : PlopmConfig
        Initialized map and slice configuration.
    data : SimData
        Loaded grid data.
    n : int
        Slice index.

    Returns
    -------
    tuple
        Coordinate meshes, display and filename slice labels, mapped grid
        dimensions, and coordinate-axis names.

    """
    slide_range = cfg.slice[n][2]
    nz = data.nz
    if slide_range[0] == ":":
        cfg.slice[n][2] = [0, nz]
        slice_title = f", slide k={1}:{nz}"
        slice_name = f"i,j,{1}:{nz}"
    elif slide_range[0] == slide_range[1] - 1:
        start_index = slide_range[0] + 1
        slice_title = f", slide k={start_index}"
        slice_name = f"i,j,{start_index}"
    else:
        start_index = slide_range[0] + 1
        end_index = slide_range[1]
        slice_title = f", slide k={start_index}:{end_index}"
        slice_name = f"i,j,{start_index}:{end_index}"
    xc, yc = get_xy_coords(cfg, data, n)
    mx = 2 * data.nx - 1
    my = 2 * data.ny - 1
    xname = "x"
    yname = "y"
    return xc, yc, slice_title, slice_name, mx, my, xname, yname


def transform_grid(
    cfg: PlopmConfig, n: int, xc: NDArray, yc: NDArray
) -> tuple[NDArray, NDArray]:
    """Rotate and translate a two-dimensional coordinate mesh.

    Parameters
    ----------
    cfg : PlopmConfig
        Rotation and translation settings.
    n : int
        Map index.
    xc, yc : np.ndarray
        Coordinate meshes to transform.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Transformed x- and y-coordinate meshes.

    """
    grd = int(cfg.rotation[n])
    angle = grd * np.pi / 180
    cos_val = np.cos(angle)
    sin_val = np.sin(angle)
    length = xc[-1][-1] - xc[0][0]
    width = yc[0][-1] - yc[-1][0]
    x_dis = float(cfg.translation[n][0][1:])
    y_dis = float(cfg.translation[n][1][:-1])
    base_x = 1.5 * length
    base_y = 1.5 * width
    dx = xc - base_x
    dy = yc - base_y
    return (
        base_x + x_dis + dx * cos_val - dy * sin_val,
        base_y + y_dis + dy * cos_val + dx * sin_val,
    )


def map_xz(
    cfg: PlopmConfig,
    data: SimData,
    var: str,
    values: NDArray,
    n: int,
    mx: int,
    my: int,
    features: list | None = None,
    feature_id: int = 1,
) -> NDArray:
    """Aggregate active-cell values onto an xz slice.

    Values are aggregated through the selected j interval. Permeability uses
    arithmetic or harmonic thickness weighting according to flow direction;
    other properties use the configured aggregation or pore-volume weighting.

    Parameters
    ----------
    cfg : PlopmConfig
        Slice and aggregation configuration.
    data : SimData
        Loaded grid properties and active-cell mapping.
    var : str
        Variable name.
    values : np.ndarray
        Values in active-cell order.
    n : int
        Map index.
    mx, my : int
        Mapped grid dimensions.
    features : list, optional
        Wells or faults grouped by label.
    feature_id : int, default: 1
        Category assigned when mapping one feature.

    Returns
    -------
    np.ndarray
        Values on the flattened xz plotting grid.

    """
    how = cfg.aggregation[n]
    nx = data.nx
    ny = data.ny
    nz = data.nz
    slide_start, slide_end = cfg.slice[n][1]
    layer_size = nx * ny
    porv = data.porv
    active_idx = data.active_idx
    dy = data.dy
    mapped_values = np.full(mx * my, np.nan)
    is_wells_or_faults = features is not None
    is_sum_property = var in cfg.mass_vars or var in [
        "porv",
        "dy",
        "tranx",
        "tranz",
    ]
    is_caprock = var in cfg.caprock_vars
    is_arithmetic_perm = var in ["permx", "permz"]
    for k in range(nz):
        layer_offset = k * layer_size
        output_layer_offset = 2 * (nz - k - 1) * mx
        for i in range(nx):
            p_v, val, d_y = 0.0, 0.0, 0.0
            if how == "min":
                val = np.inf
            if how == "max":
                val = -np.inf
            for sld in range(slide_start, slide_end):
                ind = i + sld * nx + layer_offset
                cell_pv = porv[ind]
                if cell_pv > 0:
                    active_id = active_idx[ind]
                    if how and not is_wells_or_faults:
                        if how == "first":
                            p_v = 1.0
                            if var == "index_i":
                                val = i + 1
                            elif var == "index_j":
                                val = sld + 1
                            elif var == "index_k":
                                val = k + 1
                            else:
                                val = values[active_id]
                            break
                        if how == "last":
                            p_v = 1.0
                            if var == "index_i":
                                val = i + 1
                            elif var == "index_j":
                                val = sld + 1
                            elif var == "index_k":
                                val = k + 1
                            else:
                                val = values[active_id]
                        elif how == "min":
                            p_v = 1.0
                            val = min(val, values[active_id])
                        elif how == "max":
                            p_v = 1.0
                            val = max(val, values[active_id])
                        elif how == "sum":
                            p_v = 1.0
                            val += values[active_id]
                        elif how == "mean":
                            p_v += 1.0
                            val += values[active_id]
                        elif how == "pvmean":
                            p_v += cell_pv
                            val += values[active_id] * cell_pv
                        elif how == "harmonic":
                            cell_value = values[active_id]
                            d_y += dy[active_id]
                            val = (
                                np.inf
                                if cell_value == 0
                                else val + dy[active_id] / cell_value
                            )
                            p_v += cell_pv
                        elif how == "arithmetic":
                            p_v += dy[active_id]
                            val += values[active_id] * dy[active_id]
                    elif is_sum_property:
                        p_v = 1.0
                        val += values[active_id]
                    elif is_caprock:
                        p_v = 1.0
                        val = values[active_id]
                        break
                    elif is_arithmetic_perm:
                        p_v += dy[active_id]
                        val += values[active_id] * dy[active_id]
                    elif var == "permy":
                        cell_value = values[active_id]
                        p_v = 1
                        d_y += dy[active_id]
                        val = (
                            np.inf
                            if cell_value == 0
                            else val + dy[active_id] / cell_value
                        )
                    elif var == "grid":
                        p_v = 1
                        val = 1
                    elif var in ["wells", "faults"]:
                        p_v = 1
                        val = feature_id
                    elif var == "index_i":
                        p_v = 1
                        val = i + 1
                    elif var == "index_j":
                        p_v = 1
                        val = sld + 1
                    elif var == "index_k":
                        p_v = 1
                        val = k + 1
                    else:
                        p_v += cell_pv
                        val += values[active_id] * cell_pv
            if how == "harmonic" or (not how and var == "permy"):
                mapped_values[2 * i + output_layer_offset] = (
                    np.nan
                    if p_v == 0
                    else 0.0 if val == np.inf else np.nan if val == 0 else d_y / val
                )
            else:
                mapped_values[2 * i + output_layer_offset] = (
                    np.nan if p_v == 0 else val / p_v
                )
    if is_wells_or_faults:
        assert features is not None
        for index, vals in enumerate(features):
            for value in vals:
                if value:
                    for k in range(value[2], value[3] + 1):
                        ind = value[0] + value[1] * nx + k * layer_size
                        if not cfg.global_range:
                            if porv[ind] > 0 and slide_start <= value[1] < slide_end:
                                mapped_values[2 * value[0] + 2 * (nz - k - 1) * mx] = (
                                    index + 1
                                )
                        else:
                            if porv[ind] > 0:
                                mapped_values[2 * value[0] + 2 * (nz - k - 1) * mx] = (
                                    index + 1
                                )
    return mapped_values


def map_yz(
    cfg: PlopmConfig,
    data: SimData,
    var: str,
    values: NDArray,
    n: int,
    mx: int,
    my: int,
    features: list | None = None,
    feature_id: int = 1,
) -> NDArray:
    """Aggregate active-cell values onto a yz slice.

    Values are aggregated through the selected i interval. Permeability uses
    arithmetic or harmonic thickness weighting according to flow direction;
    other properties use the configured aggregation or pore-volume weighting.

    Parameters
    ----------
    cfg : PlopmConfig
        Slice and aggregation configuration.
    data : SimData
        Loaded grid properties and active-cell mapping.
    var : str
        Variable name.
    values : np.ndarray
        Values in active-cell order.
    n : int
        Map index.
    mx, my : int
        Mapped grid dimensions.
    features : list, optional
        Wells or faults grouped by label.
    feature_id : int, default: 1
        Category assigned when mapping one feature.

    Returns
    -------
    np.ndarray
        Values on the flattened yz plotting grid.

    """
    how = cfg.aggregation[n]
    nx = data.nx
    ny = data.ny
    nz = data.nz
    slide_start, slide_end = cfg.slice[n][0]
    layer_size = nx * ny
    porv = data.porv
    active_idx = data.active_idx
    dx = data.dx
    mapped_values = np.full(mx * my, np.nan)
    is_wells_or_faults = features is not None
    is_sum_property = var in cfg.mass_vars or var in [
        "porv",
        "dx",
        "trany",
        "tranz",
    ]
    is_caprock = var in cfg.caprock_vars
    is_arithmetic_perm = var in ["permy", "permz"]
    for k in range(nz):
        layer_offset = k * layer_size
        output_layer_offset = 2 * (nz - k - 1) * mx
        for j in range(ny):
            row_offset = j * nx
            p_v, val, d_x = 0.0, 0.0, 0.0
            if how == "min":
                val = np.inf
            if how == "max":
                val = -np.inf
            for sld in range(slide_start, slide_end):
                ind = sld + row_offset + layer_offset
                cell_pv = porv[ind]
                if cell_pv > 0:
                    active_id = active_idx[ind]
                    if how and not is_wells_or_faults:
                        if how == "first":
                            p_v = 1.0
                            if var == "index_i":
                                val = sld + 1
                            elif var == "index_j":
                                val = j + 1
                            elif var == "index_k":
                                val = k + 1
                            else:
                                val = values[active_id]
                            break
                        if how == "last":
                            p_v = 1.0
                            if var == "index_i":
                                val = sld + 1
                            elif var == "index_j":
                                val = j + 1
                            elif var == "index_k":
                                val = k + 1
                            else:
                                val = values[active_id]
                        elif how == "min":
                            p_v = 1.0
                            val = min(val, values[active_id])
                        elif how == "max":
                            p_v = 1.0
                            val = max(val, values[active_id])
                        elif how == "sum":
                            p_v = 1.0
                            val += values[active_id]
                        elif how == "mean":
                            p_v += 1.0
                            val += values[active_id]
                        elif how == "pvmean":
                            p_v += cell_pv
                            val += values[active_id] * cell_pv
                        elif how == "harmonic":
                            cell_value = values[active_id]
                            d_x += dx[active_id]
                            val = (
                                np.inf
                                if cell_value == 0
                                else val + dx[active_id] / cell_value
                            )
                            p_v += cell_pv
                        elif how == "arithmetic":
                            p_v += dx[active_id]
                            val += values[active_id] * dx[active_id]
                    elif is_sum_property:
                        p_v = 1.0
                        val += values[active_id]
                    elif is_caprock:
                        p_v = 1.0
                        val = values[active_id]
                        break
                    elif is_arithmetic_perm:
                        p_v += dx[active_id]
                        val += values[active_id] * dx[active_id]
                    elif var == "permx":
                        cell_value = values[active_id]
                        p_v = 1
                        d_x += dx[active_id]
                        val = (
                            np.inf
                            if cell_value == 0
                            else val + dx[active_id] / cell_value
                        )
                    elif var == "grid":
                        p_v = 1
                        val = 1
                    elif var in ["wells", "faults"]:
                        p_v = 1
                        val = feature_id
                    elif var == "index_i":
                        p_v = 1
                        val = sld + 1
                    elif var == "index_j":
                        p_v = 1
                        val = j + 1
                    elif var == "index_k":
                        p_v = 1
                        val = k + 1
                    else:
                        p_v += cell_pv
                        val += values[active_id] * cell_pv
            if how == "harmonic" or (not how and var == "permx"):
                mapped_values[2 * j + output_layer_offset] = (
                    np.nan
                    if p_v == 0
                    else 0.0 if val == np.inf else np.nan if val == 0 else d_x / val
                )
            else:
                mapped_values[2 * j + output_layer_offset] = (
                    np.nan if p_v == 0 else val / p_v
                )
    if is_wells_or_faults:
        assert features is not None
        for index, vals in enumerate(features):
            for value in vals:
                if value:
                    for k in range(value[2], value[3] + 1):
                        ind = value[0] + value[1] * nx + k * layer_size
                        if not cfg.global_range:
                            if porv[ind] > 0 and slide_start <= value[0] < slide_end:
                                mapped_values[2 * value[1] + 2 * (nz - k - 1) * mx] = (
                                    index + 1
                                )
                        else:
                            if porv[ind] > 0:
                                mapped_values[2 * value[1] + 2 * (nz - k - 1) * mx] = (
                                    index + 1
                                )
    return mapped_values


def map_xy(
    cfg: PlopmConfig,
    data: SimData,
    var: str,
    values: NDArray,
    n: int,
    mx: int,
    my: int,
    features: list | None = None,
    feature_id: int = 1,
) -> NDArray:
    """Aggregate active-cell values onto an xy slice.

    Values are aggregated through the selected k interval. Dual-porosity rows
    are included when enabled, and permeability is weighted according to the
    vertical flow direction.

    Parameters
    ----------
    cfg : PlopmConfig
        Slice, aggregation, and dual-grid configuration.
    data : SimData
        Loaded grid properties and active-cell mapping.
    var : str
        Variable name.
    values : np.ndarray
        Values in active-cell order.
    n : int
        Map index.
    mx, my : int
        Mapped grid dimensions.
    features : list, optional
        Wells or faults grouped by label.
    feature_id : int, default: 1
        Category assigned when mapping one feature.

    Returns
    -------
    np.ndarray
        Values on the flattened xy plotting grid.

    """
    how = cfg.aggregation[n]
    nx = data.nx
    ny_total = data.ny
    dual = cfg.dual_grid[n] == "1" if n < len(cfg.dual_grid) else False
    ny = int((ny_total - 1) / 2) if dual else ny_total
    slide_start, slide_end = cfg.slice[n][2]
    layer_size = nx * ny_total
    porv = data.porv
    active_idx = data.active_idx
    dz = data.dz
    mapped_values = np.full(mx * my, np.nan)
    is_wells_or_faults = features is not None
    is_sum_property = var in cfg.mass_vars or var in [
        "porv",
        "dz",
        "tranx",
        "trany",
    ]
    is_caprock = var in cfg.caprock_vars
    is_arithmetic_perm = var in ["permx", "permy"]
    for j in range(ny):
        row_offset = j * nx
        dual_row_offset = (j + ny + 1) * nx
        for i in range(nx):
            p_v, val, d_z = 0.0, 0.0, 0.0
            if how == "min":
                val = np.inf
            if how == "max":
                val = -np.inf
            for sld in range(slide_start, slide_end):
                layer_offset = sld * layer_size
                ind = i + row_offset + layer_offset
                idd = i + dual_row_offset + layer_offset
                cell_pv = porv[ind]
                dual_cell_pv = porv[idd] if dual else 0
                if cell_pv > 0 or (dual and dual_cell_pv > 0):
                    active_id = active_idx[ind]
                    dual_active_id = active_idx[idd] if dual else active_id
                    if how and not is_wells_or_faults:
                        if how == "first":
                            p_v = 1.0
                            if var == "index_i":
                                val = i + 1
                            elif var == "index_j":
                                val = j + 1
                            elif var == "index_k":
                                val = sld + 1
                            else:
                                val = values[active_id]
                            break
                        if how == "last":
                            p_v = 1.0
                            if var == "index_i":
                                val = i + 1
                            elif var == "index_j":
                                val = j + 1
                            elif var == "index_k":
                                val = sld + 1
                            else:
                                val = values[active_id]
                        elif how == "min":
                            p_v = 1.0
                            if cell_pv > 0:
                                val = min(val, values[active_id])
                            if dual and dual_cell_pv > 0:
                                val = min(val, values[dual_active_id])
                        elif how == "max":
                            p_v = 1.0
                            if cell_pv > 0:
                                val = max(val, values[active_id])
                            if dual and dual_cell_pv > 0:
                                val = max(val, values[dual_active_id])
                        elif how == "sum":
                            p_v = 1.0
                            if cell_pv > 0:
                                val += values[active_id]
                            if dual and dual_cell_pv > 0:
                                val += values[dual_active_id]
                        elif how == "mean":
                            if cell_pv > 0:
                                p_v += 1.0
                                val += values[active_id]
                            if dual and dual_cell_pv > 0:
                                p_v += 1.0
                                val += values[dual_active_id]
                        elif how == "pvmean":
                            if cell_pv > 0:
                                p_v += cell_pv
                                val += values[active_id] * cell_pv
                            if dual and dual_cell_pv > 0:
                                p_v += dual_cell_pv
                                val += values[dual_active_id] * dual_cell_pv
                        elif how == "harmonic":
                            if cell_pv > 0:
                                cell_value = values[active_id]
                                d_z += dz[active_id]
                                val = (
                                    np.inf
                                    if cell_value == 0
                                    else val + dz[active_id] / cell_value
                                )
                                p_v += cell_pv
                            if dual and dual_cell_pv > 0:
                                cell_value = values[dual_active_id]
                                d_z += dz[dual_active_id]
                                val = (
                                    np.inf
                                    if cell_value == 0
                                    else val + dz[dual_active_id] / cell_value
                                )
                                p_v += dual_cell_pv
                        elif how == "arithmetic":
                            if cell_pv > 0:
                                p_v += dz[active_id]
                                val += values[active_id] * dz[active_id]
                            if dual and dual_cell_pv > 0:
                                p_v += dz[dual_active_id]
                                val += values[dual_active_id] * dz[dual_active_id]
                    elif is_sum_property:
                        p_v = 1.0
                        if cell_pv > 0:
                            val += values[active_id]
                        if dual and dual_cell_pv > 0:
                            val += values[dual_active_id]
                    elif is_caprock:
                        p_v = 1.0
                        val = values[active_id]
                        break
                    elif is_arithmetic_perm:
                        if cell_pv > 0:
                            p_v += dz[active_id]
                            val += values[active_id] * dz[active_id]
                        if dual and dual_cell_pv > 0:
                            p_v += dz[dual_active_id]
                            val += values[dual_active_id] * dz[dual_active_id]
                    elif var == "permz":
                        p_v = 1
                        if cell_pv > 0:
                            cell_value = values[active_id]
                            d_z += dz[active_id]
                            val = (
                                np.inf
                                if cell_value == 0
                                else val + dz[active_id] / cell_value
                            )
                        if dual and dual_cell_pv > 0:
                            cell_value = values[dual_active_id]
                            d_z += dz[dual_active_id]
                            val = (
                                np.inf
                                if cell_value == 0
                                else val + dz[dual_active_id] / cell_value
                            )
                    elif var == "grid":
                        p_v = 1
                        val = 1
                    elif var in ["wells", "faults"]:
                        p_v = 1
                        val = feature_id
                    elif var == "index_i":
                        p_v = 1
                        val = i + 1
                    elif var == "index_j":
                        p_v = 1
                        val = j + 1
                    elif var == "index_k":
                        p_v = 1
                        val = sld + 1
                    else:
                        if cell_pv > 0:
                            p_v += cell_pv
                            val += values[active_id] * cell_pv
                        if dual and dual_cell_pv > 0:
                            p_v += dual_cell_pv
                            val += values[dual_active_id] * dual_cell_pv
            if how == "harmonic" or (not how and var == "permz"):
                mapped_values[2 * i + 2 * j * mx] = (
                    np.nan
                    if p_v == 0
                    else 0.0 if val == np.inf else np.nan if val == 0 else d_z / val
                )
            else:
                mapped_values[2 * i + 2 * j * mx] = np.nan if p_v == 0 else val / p_v
    if is_wells_or_faults:
        assert features is not None
        for index, vals in enumerate(features):
            for value in vals:
                if value:
                    for k in range(value[2], value[3] + 1):
                        ind = value[0] + value[1] * nx + k * layer_size
                        if not cfg.global_range:
                            if porv[ind] > 0 and slide_start <= k < slide_end:
                                mapped_values[2 * value[0] + 2 * value[1] * mx] = (
                                    index + 1
                                )
                        else:
                            if porv[ind] > 0:
                                mapped_values[2 * value[0] + 2 * value[1] * mx] = (
                                    index + 1
                                )
    if dual and cfg.difference_input:
        mapped_values = mapped_values[: (2 * nx - 1) * (2 * ny - 1)]
    return mapped_values
