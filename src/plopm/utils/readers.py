# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0911,R0912,R0913,R0915,R0917,R1702,R0914,C0302,E1102

"""Utility functions to read the OPM Flow simulator type output files"""

import os
import csv
import sys
from contextlib import nullcontext
import datetime
import numpy as np
from numpy.typing import NDArray
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import EGrid as OpmGrid
from opm.io.ecl import ERst as OpmRestart
from opm.io.ecl import ESmry as OpmSummary
from alive_progress import alive_bar
from plopm.utils.initialization import initialize_mass, initialize_spatial
from plopm.config.config import ConfigPlopm, ReadData

GAS_DEN_REF = 1.86843
WAT_DEN_REF = 998.108


def get_readers(
    deck: str,
    gif: bool,
    vtk: bool,
    vrs: list,
    restart: list,
    filters: list,
    n: int = 0,
) -> ReadData:
    """Load the opm parsing methods"""
    if os.path.isfile(f"{deck}.INIT"):
        init = OpmFile(f"{deck}.INIT")
    else:
        print(f"Unable to find {deck} with .INIT.")
        sys.exit()
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
                porv[mask] = handle_filter(porv[mask], arr, filte[1], float(filte[2]))

    if unrst:
        steps = unrst.report_steps
        ntot = steps[-1] + 1
        tnrst = [unrst["DOUBHEAD", ntm][0] for ntm in steps]
        if restart[0] == -1:
            restart = unrst.report_steps if gif else [ntot - 1]
    elif restart[0] == -1:
        restart = [ntot - 1]

    nx = ny = nz = 0

    if egrid:
        dim = egrid.dimension
        nx, ny, nz = dim
    elif "index_i" in vrs or "index_j" in vrs or "index_k" in vrs:
        grid = OpmGrid(f"{deck}.EGRID")
        dim = grid.dimension
        nx, ny, nz = dim

    if not tnrst:
        tnrst = [0] * len(restart)

    return ReadData(
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


def get_yzcoords(cfg: ConfigPlopm, read: ReadData, n: int) -> tuple[NDArray, NDArray]:
    """Handle the coordinates from the OPM Grid to the 2D yz-mesh using opm"""
    xyz_func = read.egrid.xyz_from_ijk
    ny_val = read.ny
    nz_val = read.nz
    base_i_all = cfg.slide[n][0][0]
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


def get_xzcoords(cfg: ConfigPlopm, read: ReadData, n: int) -> tuple[NDArray, NDArray]:
    """Handle the coordinates from the OPM Grid to the 2D xz-mesh using opm"""
    xyz_func = read.egrid.xyz_from_ijk
    nx_val = read.nx
    nz_val = read.nz
    base_j_all = cfg.slide[n][1][0]
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


def get_xycoords(cfg: ConfigPlopm, read: ReadData, n: int) -> tuple[NDArray, NDArray]:
    """Handle the coordinates from the OPM Grid to the 2D xy-mesh"""
    xyz_func = read.egrid.xyz_from_ijk
    nx_val = read.nx
    ny_val = read.ny
    base_k_all = cfg.slide[n][2][0]
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


def resolve_variable(
    cfg: ConfigPlopm,
    read: ReadData,
    key_up: str,
    key_low: str,
    nrst: int,
    init: OpmFile,
    unrst: OpmRestart,
    mass_all: list,
    caprock_list: list,
):
    """Handle the variable"""
    if init.count(key_up):
        return 1.0 * init[key_up, 0]
    if unrst is not None and unrst.count(key_up, nrst):
        return 1.0 * unrst[key_up, nrst]
    if key_low in mass_all:
        return handle_mass(read, key_low, nrst)
    if key_low in caprock_list:
        val, _ = handle_caprock(read, key_low, nrst, cfg.stress)
        return val
    if key_low in ["swat", "soil", "sgas"]:
        return handle_saturation(read.unrst, key_low, nrst)
    return None


def get_histogram(cfg: ConfigPlopm, read: ReadData, quans: list, nrst: int) -> NDArray:
    """Get the required variables from the histogram"""
    quan0_low = quans[0]
    quan0 = quan0_low.upper()
    porv = read.porv
    nxyz = read.nxyz
    init_dic = read.init
    unrst_dic = read.unrst
    mass_all = cfg.mass + cfg.xmass
    caprock_list = cfg.caprock
    if quan0 != "PORV":
        act = porv > 0
    else:
        act = porv > -1
    var = np.nan * np.ones(nxyz, dtype=float)
    result = resolve_variable(
        cfg, read, quan0, quan0_low, nrst, init_dic, unrst_dic, mass_all, caprock_list
    )
    if result is not None:
        var[act] = result
    else:
        print(f"Unknow -v variable ({quans[0]}).")
        sys.exit()
    if len(quans) > 1:
        ops = quans[1::2]
        for j, val in enumerate(quans[2::2]):
            val_up = val.upper()
            if val[0].isdigit() and not val[-1].isdigit():
                if unrst_dic is None:
                    print(f"Unknow -v variable ({val}).")
                    sys.exit()
                quan1 = 1.0 * unrst_dic[val[1:].upper(), int(val[0])]
            elif val[0].isdigit() and val[-1].isdigit():
                quan1 = np.full_like(var[act], float(val))
            else:
                quan1 = resolve_variable(
                    cfg,
                    read,
                    val_up,
                    val,
                    nrst,
                    init_dic,
                    unrst_dic,
                    mass_all,
                    caprock_list,
                )
                if quan1 is None:
                    print(f"Unknow -v variable ({val}).")
                    sys.exit()
            var_act = var[act]
            var[act] = operate(var_act, quan1, ops[j])
    return var


def compute_distance(
    cfg: ConfigPlopm, read: ReadData, quans: list, n: int
) -> tuple[NDArray, NDArray]:
    """Get the required variables from the simulation files"""
    xyz_func = read.egrid.xyz_from_ijk
    nx_val = read.nx
    ny_val = read.ny
    nz_val = read.nz
    nxyz = read.nxyz
    ntot = read.ntot
    porv = read.porv
    init_dic = read.init
    unrst_dic = read.unrst
    mass_all = cfg.mass + cfg.xmass
    distance_type = cfg.distance[0]
    xyz = np.zeros((nxyz, 3), dtype=float)
    act = porv > 0
    time = np.array(read.tnrst)
    distance = np.nan * np.ones(ntot)
    index = 0
    for k in range(nz_val):
        for j in range(ny_val):
            for i in range(nx_val):
                xyz[index, :] = np.mean(xyz_func(i, j, k, True), axis=1)
                index += 1
    if cfg.distance[1] == "sensor":
        ind = (
            cfg.slide[n][0]
            + cfg.slide[n][1] * nx_val
            + cfg.slide[n][2] * nx_val * ny_val
        )
        points = [xyz[ind, :]]
        print(
            f"Computing the {cfg.distance[0]} distance to the sensor "
            f"[{points[0][0]:.2E},{points[0][1]:.2E},{points[0][2]:.2E}] m"
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
        print(f"Computing the {cfg.distance[0]} distance to the boundaries")
    show_progress = sys.stdout.isatty()
    if show_progress:
        bar_ctx = alive_bar(ntot * len(points), bar="fish")
    else:
        bar_ctx = nullcontext()
    with bar_ctx as bar_animation:
        for nrst in unrst_dic.report_steps:
            xyzt = np.copy(xyz)
            var = np.nan * np.ones(nxyz, dtype=float)
            quan0_low = quans[0]
            quan0_up = quans[0].upper()
            if quan0_low in ["index_i", "index_j", "index_k"]:
                var[act] = get_indices(quan0_low, nx_val, ny_val, nz_val)
            elif unrst_dic.count(quan0_up, nrst):
                var[act] = 1.0 * unrst_dic[quan0_up, nrst]
            elif quan0_low in mass_all:
                var[act] = handle_mass(read, quan0_low, nrst)
            elif quan0_low in ["swat", "soil", "sgas"]:
                var[act] = handle_saturation(read.unrst, quan0_low, nrst)
            else:
                print(f"Unknow -v variable ({quans[0]}).")
                sys.exit()
            if len(quans) > 1:
                ops = quans[1::2]
                for j, val in enumerate(quans[2::2]):
                    val_up = val.upper()
                    if val[0].isdigit() and not val[-1].isdigit():
                        quan1 = 1.0 * unrst_dic[val[1:].upper(), int(val[0])]
                    elif val[0].isdigit() and val[-1].isdigit():
                        quan1 = np.full_like(var[act], float(val))
                    elif init_dic.count(val_up):
                        quan1 = 1.0 * init_dic[val_up, 0]
                        if val_up == "PORV":
                            quan1 = quan1[act]
                    elif val in ["index_i", "index_j", "index_k"]:
                        var[act] = get_indices(val, nx_val, ny_val, nz_val)
                        continue
                    elif unrst_dic.count(val_up, nrst):
                        quan1 = 1.0 * unrst_dic[val_up, nrst]
                    elif val in mass_all:
                        quan1 = handle_mass(read, val, nrst)
                    elif val in ["swat", "soil", "sgas"]:
                        quan1 = handle_saturation(read.unrst, val, nrst)
                    else:
                        print(f"Unknow -v variable ({val}).")
                        sys.exit()
                    var_act = var[act]
                    var[act] = operate(var_act, quan1, ops[j])
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
                    distance[nrst] = np.nanmin(temp)
                else:
                    distance[nrst] = np.nanmax(temp)
    return distance[~np.isnan(distance)], time[~np.isnan(distance)]


def get_indices(name: str, nx: int, ny: int, nz: int) -> list:
    """Compute the i, j, or k indices"""
    nxyz = nx * ny * nz
    if name == "index_i":
        return [(grid_index % nx) + 1 for grid_index in range(nxyz)]
    if name == "index_j":
        return [((grid_index // nx) % ny) + 1 for grid_index in range(nxyz)]
    return [(grid_index // (nx * ny)) + 1 for grid_index in range(nxyz)]


def project(var: NDArray, oper: str, porv: NDArray) -> NDArray:
    """Applied the requested projection"""
    if oper == "min":
        return np.min(var)
    if oper == "max":
        return np.max(var)
    if oper == "sum":
        return np.sum(var)
    if oper == "mean":
        return np.mean(var)
    if oper == "pvmean":
        return np.sum(var * porv) / np.sum(porv)
    print(f"Unknow/unsupported projection ({oper}).")
    sys.exit()


def do_read_variables(
    cfg: ConfigPlopm, read: ReadData, quans: list, n: int, ntot: list
) -> tuple[NDArray, NDArray]:
    """Get the required variables from the simulation files"""
    slide = cfg.slide[n]
    axis_index = slide.index(-1) if -1 in slide else -1
    nx_val = read.nx
    ny_val = read.ny
    nz_val = read.nz
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
        time = np.array(read.tnrst)
        var = 0.0 * np.ones(tsize)
    else:
        time = np.array(range(xsize), dtype=float)
        var = 0.0 * np.ones(xsize)
    init_dic = read.init
    unrst_dic = read.unrst
    mass_all = cfg.mass + cfg.xmass
    caprock_list = cfg.caprock
    pv_all = read.pv
    layer_flag = cfg.layer
    egrid = read.egrid
    quan0_low = quans[0]
    quan0_up = quan0_low.upper()
    ops = quans[1::2] if len(quans) > 1 else []
    for output_index, nrst in enumerate(ntot):
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
            arr_main = handle_mass(read, quan0_low, nrst)
        elif quan0_low in caprock_list:
            arr_main, _ = handle_caprock(read, quan0_low, nrst, cfg.stress)
        elif quan0_low in ["swat", "soil", "sgas"]:
            arr_main = handle_saturation(read.unrst, quan0_low, nrst)
        else:
            arr_main = None
        if len(quans) > 1:
            arr_vals = []
            for val in quans[2::2]:
                if val in mass_all:
                    arr_vals.append(handle_mass(read, val, nrst))
                elif val in caprock_list:
                    arr, _ = handle_caprock(read, val, nrst, cfg.stress)
                    arr_vals.append(arr)
                elif val in ["swat", "soil", "sgas"]:
                    arr_vals.append(handle_saturation(read.unrst, val, nrst))
                else:
                    arr_vals.append(np.full_like(temp, np.nan))
        inds_arr = np.array(inds)

        if unrst_dic.count(quan0_up, nrst):
            temp = 1.0 * unrst_dic[quan0_up, nrst][inds_arr]
        elif init_dic.count(quan0_up):
            temp = 1.0 * init_dic[quan0_up, 0][inds_arr]
        elif arr_main is not None:
            temp = arr_main[inds_arr]
        else:
            print(f"Unknow -v variable ({quans[0]}).")
            sys.exit()

        if unrst_dic.count("RPORV", nrst):
            porv = unrst_dic["RPORV", nrst][inds_arr]
        else:
            porv = pv_all[inds_arr]

        if len(quans) > 1:
            for j, val in enumerate(quans[2::2]):
                val_up = val.upper()
                arr_val = arr_vals[j]
                if val[0].isdigit() and not val[-1].isdigit():
                    quan1 = 1.0 * unrst_dic[val[1:].upper(), int(val[0])][inds_arr]
                elif val[0].isdigit() and val[-1].isdigit():
                    quan1 = np.full_like(temp, float(val))
                elif init_dic.count(val_up):
                    quan1 = 1.0 * init_dic[val_up, 0][inds_arr]
                elif unrst_dic.count(val_up, nrst):
                    quan1 = 1.0 * unrst_dic[val_up, nrst][inds_arr]
                elif not np.isnan(arr_val).all():
                    quan1 = arr_val[inds_arr]
                else:
                    print(f"Unknow -v variable ({val}).")
                    sys.exit()
                temp = operate(temp, quan1, ops[j])
        ll = np.arange(xsize) + output_index
        if cfg.how[0]:
            var[output_index] = project(temp, cfg.how[0], porv)
        elif layer_flag:
            var = temp
        else:
            if xsize == 1:
                var[ll] = temp[0]
            else:
                var[ll] = temp
    if layer_flag and not cfg.how[0]:
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


def read_oned(
    cfg: ConfigPlopm, case: str, quan: str, tunit: str, qskl: float, n: int
) -> tuple[NDArray, NDArray, str, str]:
    """Handle the oned vectors"""
    time, vunit = np.array([0, 1]), ""
    tskl, tunit = initialize_time(tunit)
    quans = quan.split(" ")
    csv_flag = cfg.csvs[n][0]
    q0_low = quans[0]
    if csv_flag:
        csvv = np.genfromtxt(f"{case}.csv", delimiter=",", skip_header=1)
        col_t = cfg.csvs[n][0] - 1
        col_v = cfg.csvs[n][1] - 1
        time = tskl * csvv[:, col_t] / 86400.0
        var = csvv[:, col_v]
    elif cfg.distance[0]:
        xskl, xunit = initialize_spatial(cfg.xunits)
        read = get_readers(case, cfg.gif, cfg.vtk, cfg.vrs, cfg.restart, cfg.filter)
        var, time = compute_distance(cfg, read, quans, n)
        vunit = f" ({cfg.distance[0]} distance to {cfg.distance[1]} in {xunit})"
        var *= xskl
    elif cfg.histogram[0]:
        read = get_readers(case, cfg.gif, cfg.vtk, cfg.vrs, cfg.restart, cfg.filter)
        var = get_histogram(cfg, read, quans, read.restart[0])
        tunit = ""
    elif cfg.sensor or cfg.how[0]:
        read = get_readers(case, cfg.gif, cfg.vtk, cfg.vrs, cfg.restart, cfg.filter)
        var, time = do_read_variables(cfg, read, quans, n, read.unrst.report_steps)
        time *= tskl
        if tunit == "Dates":
            tmp = []
            unrst_dic = read.unrst
            for index in range(len(unrst_dic)):
                values = unrst_dic["INTEHEAD", index]
                tmp.append(datetime.datetime(values[66], values[65], values[64], 0, 0))
            time = np.array(tmp)
    elif cfg.layer:
        xskl, tunit = initialize_spatial(cfg.xunits)
        read = get_readers(case, cfg.gif, cfg.vtk, cfg.vrs, cfg.restart, cfg.filter)
        tmp = read.restart[n] if n < len(cfg.restart) else read.restart[0]
        var, time = do_read_variables(cfg, read, quans, n, [tmp])
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
            q0_low = quans[0][:-1]
        if len(q0_low) == 3:
            what = q0_low[:3]
        elif q0_low in ["krow", "krog", "pcow", "pcog", "pcwg"]:
            what = q0_low[:4]
        elif q0_low[:3] in ["krw", "krg"]:
            what = q0_low[:3]
            snu = int(quans[0][3:])
        else:
            what = q0_low[:4]
            snu = int(quans[0][4:])
        if not os.path.isfile(f"{case}.INIT"):
            print(f"Saturation functions required {case}.INIT")
            sys.exit()
        init = OpmFile(f"{case}.INIT")
        tabdim = init["TABDIMS"]
        table = np.array(init["TAB"])
        nswe = tabdim[24]
        nsnum = tabdim[25]
        vunit = ""
        if what == "krg":
            tunit = "s$_g$ [-]"
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
            if tabdim[22] == 2:
                sht += nswe
            var = table[
                sht + nswe * nsnum + (snu - 1) * nswe : sht + nswe * nsnum + snu * nswe
            ][:count_v]
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
    elif quan[:6] == "pcfact":
        tmp0 = []
        tmp2 = []
        found = False
        snu = int(quans[0][6:])
        vec = quans[0].upper()[:6]
        file_name = where_at(case, vec)
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
                    if found:
                        if row[0] == "/":
                            count += 1
                        elif len(row) > 2 and row[2].strip() == "/":
                            count += 1
        if not tmp2:
            print(f"No {quans[0]} found.")
            sys.exit()
        var = np.array(tmp2)
        time = np.array(tmp0)
    else:
        summary = OpmSummary(f"{case}.SMSPEC")
        key = quans[0].upper()
        keys = summary.keys()
        if quans[0] in cfg.smass:
            var = summary[key[:-1]]
        else:
            var = summary[key]
        if len(quans) > 1:
            ops = quans[1::2]
            for index, val in enumerate(quans[2::2]):
                if val.upper() in keys:
                    quan1 = summary[val.upper()]
                else:
                    quan1 = float(val)
                var = operate(var, quan1, ops[index])
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
    if quans[0] in ["fgip", "fgit"]:
        vunit = " [sm$^3$]"
    elif quans[0] in cfg.smass:
        var *= GAS_DEN_REF
        vunit = initialize_mass(qskl)
    elif quans[0] in ["time"]:
        vunit = " [d]"
    return time, var * qskl, tunit, vunit


def where_at(case: str, vec: str) -> str:
    """Using the input deck (.DATA) to read the i,j fault locations"""
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
    print(f"No {vec} found (only looking in {case_file} and INCLUDE files).")
    sys.exit()


def operate(
    var: NDArray[np.float64], quan1: NDArray[np.float64], oper: str
) -> NDArray[np.float64]:
    """Applied the requested operation"""
    if oper == "+":
        return var + quan1
    if oper == "-":
        return var - quan1
    if oper == "*":
        return var * quan1
    if oper == "/":
        return var / quan1
    mask = ~np.isnan(var)
    qmask = ~np.isnan(quan1)
    mask = mask & qmask
    if oper == "==":
        var[mask] = np.where(var[mask] == quan1[mask], 1.0, np.nan)
    elif oper == ">=":
        var[mask] = np.where(var[mask] >= quan1[mask], 1.0, np.nan)
    elif oper == "<=":
        var[mask] = np.where(var[mask] <= quan1[mask], 1.0, np.nan)
    elif oper == "<":
        var[mask] = np.where(var[mask] < quan1[mask], 1.0, np.nan)
    elif oper == ">":
        var[mask] = np.where(var[mask] > quan1[mask], 1.0, np.nan)
    elif oper == "!=":
        var[mask] = np.where(var[mask] != quan1[mask], 1.0, np.nan)
    else:
        print(f"Unknow operation ({oper}).")
        sys.exit()
    return var


def initialize_time(times: str) -> tuple[float, str]:
    """Handle the time units for the x axis in the summary"""
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


def get_csvs(
    cfg: ConfigPlopm, deck: str, n: int
) -> tuple[NDArray, NDArray, int, int, str, str]:
    """Read the csv quantities"""
    if cfg.gif:
        file_name = deck.replace("PLOPM", str(cfg.restart[0]))
    else:
        file_name = deck
    csvv = np.genfromtxt(f"{file_name}.csv", delimiter=",", skip_header=1)
    col_x = cfg.csvs[n][0] - 1
    col_y = cfg.csvs[n][1] - 1
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


def handle_filter(porvs: NDArray, quan1: NDArray, oper: str, value: float) -> NDArray:
    """Apply the requested filter"""
    if oper == "==":
        mask = quan1 == value
    elif oper == ">=":
        mask = quan1 >= value
    elif oper == "<=":
        mask = quan1 <= value
    elif oper == "<":
        mask = quan1 < value
    elif oper == ">":
        mask = quan1 > value
    elif oper == "!=":
        mask = quan1 != value
    else:
        print(f"Unknow filter ({oper}).")
        sys.exit()
    return np.where(mask, porvs, 0)


def get_unit(name: str) -> str:
    """Get the variable unit"""
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


def get_quantity(
    deck: str,
    read: ReadData,
    name: str,
    nrst: int,
    skl: float,
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
    """Handle the quantity from the OPM output files"""
    names = name.split(" ")
    unit = get_unit(name)
    name0_low = names[0]
    name0 = name0_low.upper()
    if cvs[0]:
        if isgif:
            file_name = deck.replace("PLOPM", str(nrst))
        else:
            file_name = deck
        csvv = np.genfromtxt(f"{file_name}.csv", delimiter=",", skip_header=1)
        col = cvs[2] - 1
        quan = csvv[:, col]
    else:
        if read.init.count(name0):
            quan = np.array(read.init[name0], dtype=float)
            if name0_low == "porv":
                quan = read.pv
        elif name0_low in ["wells", "faults", "grid"]:
            quan = np.zeros_like(read.init["SATNUM"])
        elif name0_low in ["index_i", "index_j", "index_k"]:
            quan = np.array(
                get_indices(name0_low, read.nx, read.ny, read.nz), dtype=float
            )
            quan = quan[read.porv > 0]
        elif read.unrst.count(name0, nrst):
            quan = read.unrst[name0, nrst]
            if read.unrst.count("RPORV", nrst):
                if filters:
                    porv0 = np.array(read.init["PORV"])
                    mask = porv0 > 0
                    base_rporv = np.array(read.unrst["RPORV", nrst])
                    for value in filters.split("&"):
                        filte = value.strip().split(" ")
                        key = filte[0].upper()
                        if read.init.count(key):
                            q1 = np.array(read.init[key])
                        elif read.unrst.count(key, nrst):
                            q1 = np.array(read.unrst[key, nrst])
                        else:
                            print(f"Unknow filter quantity ({key}).")
                            sys.exit()
                        base_rporv = handle_filter(
                            base_rporv, q1, filte[1], float(filte[2])
                        )
                    read.porv[mask] = base_rporv
                else:
                    read.porv[read.porv > 0] = np.array(read.unrst["RPORV", nrst])
        elif name0_low in mass_all:
            quan = handle_mass(read, name0_low, nrst) * skl
            if name0_low in mass:
                unit = initialize_mass(skl)
        elif name0_low in caprock:
            quan, unit = handle_caprock(read, name0_low, nrst, stress)
        elif name0_low in ["swat", "soil", "sgas"]:
            quan = handle_saturation(read.unrst, name0_low, nrst) * skl
        else:
            print(f"Unknow -v variable ({name0}).")
            sys.exit()
        if len(names) > 1:
            ops = names[1::2]
            for j, val in enumerate(names[2::2]):
                if val[0].isdigit() and not val[-1].isdigit():
                    q1 = read.unrst[val[1:].upper(), int(val[0])]
                elif val[0].isdigit() and val[-1].isdigit():
                    q1 = np.full_like(quan, float(val))
                elif read.init.count(val.upper()):
                    q1 = np.array(read.init[val.upper()])
                    if val.upper() == "PORV":
                        q1 = q1[read.porv > 0]
                elif val in ["index_i", "index_j", "index_k"]:
                    q1 = np.array(
                        get_indices(val, read.nx, read.ny, read.nz),
                        dtype=float,
                    )
                    q1 = q1[read.porv > 0]
                elif read.unrst.count(val.upper(), nrst):
                    q1 = read.unrst[val.upper(), nrst]
                elif val in mass_all:
                    q1 = handle_mass(read, val, nrst) * skl
                elif val in caprock:
                    q1, unit = handle_caprock(read, val, nrst, stress)
                else:
                    print(f"Unknow -v variable ({val}).")
                    sys.exit()
                quan = operate(quan, q1, ops[j])
    if vmin:
        quan = np.asarray(quan)
        quan[quan < float(vmin)] = np.nan
    if vmax:
        quan = np.asarray(quan)
        quan[quan > float(vmax)] = np.nan
    return unit, quan


def handle_saturation(unrst: OpmRestart, name: str, nrst: int) -> NDArray:
    """Compute the oil saturation"""
    if unrst.count("SOIL", nrst):
        soil = np.array(unrst["SOIL", nrst])
    else:
        soil = np.array(0)
    if unrst.count("SGAS", nrst):
        sgas = np.array(unrst["SGAS", nrst])
    else:
        sgas = np.array(0)
    if unrst.count("SWAT", nrst):
        swat = np.array(unrst["SWAT", nrst])
    else:
        swat = np.array(0)
    if name == "soil":
        return 1 - sgas - swat
    if name == "swat":
        return 1 - sgas - soil
    return 1 - soil - swat


def handle_mass(read: ReadData, name: str, nrst: int) -> NDArray:
    """Compute the mass (intensive quantities)"""
    sgas = np.array(read.unrst["SGAS", nrst])
    rhog = np.array(read.unrst["GAS_DEN", nrst])
    rhow = np.array(read.unrst["WAT_DEN", nrst])
    if read.unrst.count("RSW", nrst):
        rsw = np.array(read.unrst["RSW", nrst])
    else:
        rsw = np.zeros_like(sgas)
    if read.unrst.count("RVW", nrst):
        rvw = np.array(read.unrst["RVW", nrst])
    else:
        rvw = np.zeros_like(sgas)
    if read.unrst.count("RPORV", nrst):
        rpv = np.array(read.unrst["RPORV", nrst])
    else:
        rpv = read.pv
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
    return type_of_mass(name, co2_g, co2_d, h2o_l, h2o_v, x_l_co2, x_g_h2o)


def type_of_mass(
    name: str,
    co2_g: NDArray,
    co2_d: NDArray,
    h2o_l: NDArray,
    h2o_v: NDArray,
    x_l_co2: NDArray,
    x_g_h2o: NDArray,
) -> NDArray:
    """From the given variable return the associated mass"""
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


def handle_caprock(
    read: ReadData, name: str, nrst: int, stress: float
) -> tuple[NDArray, str]:
    """Compute quantities related to the caprock integrity"""
    init_dic = read.init
    unrst_dic = read.unrst
    dz = np.array(init_dic["DZ", 0])
    depth = np.array(init_dic["DEPTH", 0])
    dz_half = 0.5 * dz
    dz_corr = 0.5 * dz
    if unrst_dic.count("WAT_DEN", 0) and unrst_dic.count("WAT_DEN", nrst):
        den0 = np.array(unrst_dic["WAT_DEN", 0])
        den1 = np.array(unrst_dic["WAT_DEN", nrst])
    else:
        den0 = np.array(1000.0)
        den1 = np.array(1000.0)
    fac = 9.81 / 1e5
    pz_c0 = fac * dz_corr * den0
    pz_c1 = fac * dz_corr * den1
    pressure0 = np.array(unrst_dic["PRESSURE", 0])
    pressure1 = np.array(unrst_dic["PRESSURE", nrst])
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


def get_wells(cfg: ConfigPlopm, n: int) -> tuple[list, list]:
    """Using the input deck (.DATA) to read the i,j well locations"""
    wells: list[list[list[int]]] = []
    lwells: list[str] = []
    well_map = {}
    haswells = False
    sources = False
    with open(f"{cfg.name}.DATA", "r", encoding="utf8") as file:
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
    if not cfg.global_:
        sld_x = cfg.slide[n][0]
        sld_y = cfg.slide[n][1]
        sld_z = cfg.slide[n][2]
        whow = cfg.whow
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


def get_faults(cfg: ConfigPlopm, n: int) -> tuple[list, list]:
    """Using the input deck (.DATA) to read the i,j fault locations"""
    faults: list[list[list[int]]] = []
    lfaults: list[str] = []
    fault_map = {}
    hasfaults = False
    with open(f"{cfg.name}.DATA", "r", encoding="utf8") as file:
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
    if not cfg.global_:
        sld_x = cfg.slide[n][0]
        sld_y = cfg.slide[n][1]
        sld_z = cfg.slide[n][2]
        whow = cfg.whow
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
