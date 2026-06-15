# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1702,R0912,C0325,R0913,R0914,R0915,R0917

"""Utility function for the grid and locations in the geological models"""

import numpy as np
from numpy.typing import NDArray
from plopm.utils.readers import get_xycoords, get_xzcoords, get_yzcoords
from plopm.config.config import ConfigPlopm, ReadData


def handle_slide_x(
    cfg: ConfigPlopm, read: ReadData, n: int
) -> tuple[NDArray, NDArray, str, str, int, int, str, str]:
    """Processing the selected yz slide to obtain the grid properties"""
    slide_range = cfg.slide[n][0]
    nx = read.nx
    if slide_range[0] == ":":
        cfg.slide[n][0] = [0, nx]
        slidet = f", slide i=0:{nx}"
        sliden = f"0:{nx},j,k"
    elif slide_range[0] == slide_range[1] - 1:
        start_index = slide_range[0] + 1
        slidet = f", slide i={start_index}"
        sliden = f"{start_index},j,k"
    else:
        start_index = slide_range[0] + 1
        end_index = slide_range[1]
        slidet = f", slide i={start_index}:{end_index}"
        sliden = f"{start_index}:{end_index},j,k"
    xc, yc = get_yzcoords(cfg, read, n)
    mx = 2 * read.ny - 1
    my = 2 * read.nz - 1
    xname = "y"
    yname = "z"
    return xc, yc, slidet, sliden, mx, my, xname, yname


def handle_slide_y(
    cfg: ConfigPlopm, read: ReadData, n: int
) -> tuple[NDArray, NDArray, str, str, int, int, str, str]:
    """Processing the selected xz slide to obtain the grid properties"""
    slide_range = cfg.slide[n][1]
    ny = read.ny
    if slide_range[0] == ":":
        cfg.slide[n][1] = [0, ny]
        slidet = f", slide j=0:{ny}"
        sliden = f"i,0:{ny},k"
    elif slide_range[0] == slide_range[1] - 1:
        start_index = slide_range[0] + 1
        slidet = f", slide j={start_index}"
        sliden = f"i,{start_index},k"
    else:
        start_index = slide_range[0] + 1
        end_index = slide_range[1]
        slidet = f", slide j={start_index}:{end_index}"
        sliden = f"i,{start_index}:{end_index},k"
    xc, yc = get_xzcoords(cfg, read, n)
    mx = 2 * read.nx - 1
    my = 2 * read.nz - 1
    xname = "x"
    yname = "z"
    return xc, yc, slidet, sliden, mx, my, xname, yname


def handle_slide_z(
    cfg: ConfigPlopm, read: ReadData, n: int
) -> tuple[NDArray, NDArray, str, str, int, int, str, str]:
    """Processing the selected xy slide to obtain the grid properties"""
    slide_range = cfg.slide[n][2]
    nz = read.nz
    if slide_range[0] == ":":
        cfg.slide[n][2] = [0, nz]
        slidet = f", slide k={1}:{nz}"
        sliden = f"i,j,{1}:{nz}"
    elif slide_range[0] == slide_range[1] - 1:
        start_index = slide_range[0] + 1
        slidet = f", slide k={start_index}"
        sliden = f"i,j,{start_index}"
    else:
        start_index = slide_range[0] + 1
        end_index = slide_range[1]
        slidet = f", slide k={start_index}:{end_index}"
        sliden = f"i,j,{start_index}:{end_index}"
    xc, yc = get_xycoords(cfg, read, n)
    mx = 2 * read.nx - 1
    my = 2 * read.ny - 1
    xname = "x"
    yname = "y"
    return xc, yc, slidet, sliden, mx, my, xname, yname


def rotate_grid(
    cfg: ConfigPlopm, n: int, xc: NDArray, yc: NDArray
) -> tuple[NDArray, NDArray]:
    """Rotate the grid if requiered"""
    grd = int(cfg.rotate[n])
    angle = grd * np.pi / 180
    cos_val = np.cos(angle)
    sin_val = np.sin(angle)
    length = xc[-1][-1] - xc[0][0]
    width = yc[0][-1] - yc[-1][0]
    x_dis = float(cfg.translate[n][0][1:])
    y_dis = float(cfg.translate[n][1][:-1])
    base_x = 1.5 * length
    base_y = 1.5 * width
    dx = xc - base_x
    dy = yc - base_y
    return (
        base_x + x_dis + dx * cos_val - dy * sin_val,
        base_y + y_dis + dy * cos_val + dx * sin_val,
    )


def map_xzcoords(
    cfg: ConfigPlopm,
    read: ReadData,
    var: str,
    quan: NDArray,
    n: int,
    mx: int,
    my: int,
    welult: list | None = None,
    nwelult: int = 1,
) -> NDArray:
    """Map the properties from the simulations to the 2D slide"""
    how = cfg.how[n]
    nx = read.nx
    ny = read.ny
    nz = read.nz
    slide_start, slide_end = cfg.slide[n][1]
    layer_size = nx * ny
    porv = read.porv
    actind_array = read.actind
    dy = read.dy
    mapped_values = np.full(mx * my, np.nan)
    is_wells_or_faults = welult is not None
    is_sum_property = var in cfg.mass or var in [
        "porv",
        "dy",
        "tranx",
        "tranz",
    ]
    is_caprock = var in cfg.caprock
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
                porv_ind = porv[ind]
                if porv_ind > 0:
                    actind = actind_array[ind]
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
                                val = quan[actind]
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
                                val = quan[actind]
                        elif how == "min":
                            p_v = 1.0
                            val = min(val, quan[actind])
                        elif how == "max":
                            p_v = 1.0
                            val = max(val, quan[actind])
                        elif how == "sum":
                            p_v = 1.0
                            val += quan[actind]
                        elif how == "mean":
                            p_v += 1.0
                            val += quan[actind]
                        elif how == "pvmean":
                            p_v += porv_ind
                            val += quan[actind] * porv_ind
                        elif how == "harmonic":
                            quan_value = quan[actind]
                            d_y += dy[actind]
                            val = (
                                np.inf
                                if quan_value == 0
                                else val + dy[actind] / quan_value
                            )
                            p_v += porv_ind
                        elif how == "arithmetic":
                            p_v += dy[actind]
                            val += quan[actind] * dy[actind]
                    elif is_sum_property:
                        p_v = 1.0
                        val += quan[actind]
                    elif is_caprock:
                        p_v = 1.0
                        val = quan[actind]
                        break
                    elif is_arithmetic_perm:
                        p_v += dy[actind]
                        val += quan[actind] * dy[actind]
                    elif var == "permy":
                        quan_value = quan[actind]
                        p_v = 1
                        d_y += dy[actind]
                        val = (
                            np.inf if quan_value == 0 else val + dy[actind] / quan_value
                        )
                    elif var == "grid":
                        p_v = 1
                        val = 1
                    elif var in ["wells", "faults"]:
                        p_v = 1
                        val = nwelult
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
                        p_v += porv_ind
                        val += quan[actind] * porv_ind
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
        assert welult is not None
        for index, values in enumerate(welult):
            for value in values:
                if value:
                    for k in range(value[2], value[3] + 1):
                        ind = value[0] + value[1] * nx + k * layer_size
                        if not cfg.global_:
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


def map_yzcoords(
    cfg: ConfigPlopm,
    read: ReadData,
    var: str,
    quan: NDArray,
    n: int,
    mx: int,
    my: int,
    welult: list | None = None,
    nwelult: int = 1,
) -> NDArray:
    """Map the properties from the simulations to the 2D slide"""
    how = cfg.how[n]
    nx = read.nx
    ny = read.ny
    nz = read.nz
    slide_start, slide_end = cfg.slide[n][0]
    layer_size = nx * ny
    porv = read.porv
    actind_array = read.actind
    dx = read.dx
    mapped_values = np.full(mx * my, np.nan)
    is_wells_or_faults = welult is not None
    is_sum_property = var in cfg.mass or var in [
        "porv",
        "dx",
        "trany",
        "tranz",
    ]
    is_caprock = var in cfg.caprock
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
                porv_ind = porv[ind]
                if porv_ind > 0:
                    actind = actind_array[ind]
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
                                val = quan[actind]
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
                                val = quan[actind]
                        elif how == "min":
                            p_v = 1.0
                            val = min(val, quan[actind])
                        elif how == "max":
                            p_v = 1.0
                            val = max(val, quan[actind])
                        elif how == "sum":
                            p_v = 1.0
                            val += quan[actind]
                        elif how == "mean":
                            p_v += 1.0
                            val += quan[actind]
                        elif how == "pvmean":
                            p_v += porv_ind
                            val += quan[actind] * porv_ind
                        elif how == "harmonic":
                            quan_value = quan[actind]
                            d_x += dx[actind]
                            val = (
                                np.inf
                                if quan_value == 0
                                else val + dx[actind] / quan_value
                            )
                            p_v += porv_ind
                        elif how == "arithmetic":
                            p_v += dx[actind]
                            val += quan[actind] * dx[actind]
                    elif is_sum_property:
                        p_v = 1.0
                        val += quan[actind]
                    elif is_caprock:
                        p_v = 1.0
                        val = quan[actind]
                        break
                    elif is_arithmetic_perm:
                        p_v += dx[actind]
                        val += quan[actind] * dx[actind]
                    elif var == "permx":
                        quan_value = quan[actind]
                        p_v = 1
                        d_x += dx[actind]
                        val = (
                            np.inf if quan_value == 0 else val + dx[actind] / quan_value
                        )
                    elif var == "grid":
                        p_v = 1
                        val = 1
                    elif var in ["wells", "faults"]:
                        p_v = 1
                        val = nwelult
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
                        p_v += porv_ind
                        val += quan[actind] * porv_ind
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
        assert welult is not None
        for index, values in enumerate(welult):
            for value in values:
                if value:
                    for k in range(value[2], value[3] + 1):
                        ind = value[0] + value[1] * nx + k * layer_size
                        if not cfg.global_:
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


def map_xycoords(
    cfg: ConfigPlopm,
    read: ReadData,
    var: str,
    quan: NDArray,
    n: int,
    mx: int,
    my: int,
    welult: list | None = None,
    nwelult: int = 1,
) -> NDArray:
    """Map the properties from the simulations to the 2D slide"""
    how = cfg.how[n]
    nx = read.nx
    ny_total = read.ny
    dual = cfg.dual[n] == "1" if n < len(cfg.dual) else False
    ny = int((ny_total - 1) / 2) if dual else ny_total
    slide_start, slide_end = cfg.slide[n][2]
    layer_size = nx * ny_total
    porv = read.porv
    actind_array = read.actind
    dz = read.dz
    mapped_values = np.full(mx * my, np.nan)
    is_wells_or_faults = welult is not None
    is_sum_property = var in cfg.mass or var in [
        "porv",
        "dz",
        "tranx",
        "trany",
    ]
    is_caprock = var in cfg.caprock
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
                porv_ind = porv[ind]
                porv_idd = porv[idd] if dual else 0
                if porv_ind > 0 or (dual and porv_idd > 0):
                    actind = actind_array[ind]
                    actidd = actind_array[idd] if dual else actind
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
                                val = quan[actind]
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
                                val = quan[actind]
                        elif how == "min":
                            p_v = 1.0
                            if porv_ind > 0:
                                val = min(val, quan[actind])
                            if dual and porv_idd > 0:
                                val = min(val, quan[actidd])
                        elif how == "max":
                            p_v = 1.0
                            if porv_ind > 0:
                                val = max(val, quan[actind])
                            if dual and porv_idd > 0:
                                val = max(val, quan[actidd])
                        elif how == "sum":
                            p_v = 1.0
                            if porv_ind > 0:
                                val += quan[actind]
                            if dual and porv_idd > 0:
                                val += quan[actidd]
                        elif how == "mean":
                            if porv_ind > 0:
                                p_v += 1.0
                                val += quan[actind]
                            if dual and porv_idd > 0:
                                p_v += 1.0
                                val += quan[actidd]
                        elif how == "pvmean":
                            if porv_ind > 0:
                                p_v += porv_ind
                                val += quan[actind] * porv_ind
                            if dual and porv_idd > 0:
                                p_v += porv_idd
                                val += quan[actidd] * porv_idd
                        elif how == "harmonic":
                            if porv_ind > 0:
                                quan_value = quan[actind]
                                d_z += dz[actind]
                                val = (
                                    np.inf
                                    if quan_value == 0
                                    else val + dz[actind] / quan_value
                                )
                                p_v += porv_ind
                            if dual and porv_idd > 0:
                                quan_value = quan[actidd]
                                d_z += dz[actidd]
                                val = (
                                    np.inf
                                    if quan_value == 0
                                    else val + dz[actidd] / quan_value
                                )
                                p_v += porv_idd
                        elif how == "arithmetic":
                            if porv_ind > 0:
                                p_v += dz[actind]
                                val += quan[actind] * dz[actind]
                            if dual and porv_idd > 0:
                                p_v += dz[actidd]
                                val += quan[actidd] * dz[actidd]
                    elif is_sum_property:
                        p_v = 1.0
                        if porv_ind > 0:
                            val += quan[actind]
                        if dual and porv_idd > 0:
                            val += quan[actidd]
                    elif is_caprock:
                        p_v = 1.0
                        val = quan[actind]
                        break
                    elif is_arithmetic_perm:
                        if porv_ind > 0:
                            p_v += dz[actind]
                            val += quan[actind] * dz[actind]
                        if dual and porv_idd > 0:
                            p_v += dz[actidd]
                            val += quan[actidd] * dz[actidd]
                    elif var == "permz":
                        p_v = 1
                        if porv_ind > 0:
                            quan_value = quan[actind]
                            d_z += dz[actind]
                            val = (
                                np.inf
                                if quan_value == 0
                                else val + dz[actind] / quan_value
                            )
                        if dual and porv_idd > 0:
                            quan_value = quan[actidd]
                            d_z += dz[actidd]
                            val = (
                                np.inf
                                if quan_value == 0
                                else val + dz[actidd] / quan_value
                            )
                    elif var == "grid":
                        p_v = 1
                        val = 1
                    elif var in ["wells", "faults"]:
                        p_v = 1
                        val = nwelult
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
                        if porv_ind > 0:
                            p_v += porv_ind
                            val += quan[actind] * porv_ind
                        if dual and porv_idd > 0:
                            p_v += porv_idd
                            val += quan[actidd] * porv_idd
            if how == "harmonic" or (not how and var == "permz"):
                mapped_values[2 * i + 2 * j * mx] = (
                    np.nan
                    if p_v == 0
                    else 0.0 if val == np.inf else np.nan if val == 0 else d_z / val
                )
            else:
                mapped_values[2 * i + 2 * j * mx] = np.nan if p_v == 0 else val / p_v
    if is_wells_or_faults:
        assert welult is not None
        for index, values in enumerate(welult):
            for value in values:
                if value:
                    for k in range(value[2], value[3] + 1):
                        ind = value[0] + value[1] * nx + k * layer_size
                        if not cfg.global_:
                            if porv[ind] > 0 and slide_start <= k < slide_end:
                                mapped_values[2 * value[0] + 2 * value[1] * mx] = (
                                    index + 1
                                )
                        else:
                            if porv[ind] > 0:
                                mapped_values[2 * value[0] + 2 * value[1] * mx] = (
                                    index + 1
                                )
    return mapped_values
