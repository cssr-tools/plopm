# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W3301,R0912,R0913,R0914,R0915,R0917,E1102

"""Utility methods to write the vtks"""

import os
import csv
import sys
import shlex
import shutil
from contextlib import nullcontext
from subprocess import run
from alive_progress import alive_bar
import numpy as np
from numpy.typing import NDArray
from plopm.utils.readers import get_quantity, get_readers
from plopm.config.config import ReadData

VTK_DTYPES = {
    "Float64": np.float64,
    "Float32": np.float32,
    "Float16": np.float16,
    "Int64": np.int64,
    "UInt64": np.uint64,
    "Int32": np.int32,
    "UInt32": np.uint32,
    "Int16": np.int16,
    "UInt16": np.uint16,
    "Int8": np.int8,
    "UInt8": np.uint8,
}


def make_vtks(
    flow: str,
    names: list,
    output: str,
    save: list,
    restart: list,
    vrs: list,
    vtkformat_list: list,
    vtknames: list,
    gif: bool,
    vtk: bool,
    filters: list,
    skl: list[str],
    mass: list[str],
    mass_all: list[str],
    caprock: list[str],
    stress: float,
    filterss: list[str],
) -> None:
    """Use OPM Flow to generate the vtk grid to populate with the given variables"""
    for k, case in enumerate(names[0]):
        deck = case
        dname = case.split("/")[-1]
        if not os.path.isfile(f"{deck}.DATA"):
            print(f"{deck}.DATA does not exist")
            sys.exit()
        if not os.path.isfile(f"{output}/{dname}-GRID.vtu"):
            cwd = os.getcwd()
            output_abs = os.path.abspath(output)
            dryrun_deck = ""
            dryrun_folder = ""
            dryrun_parent = cwd
            try:
                if len(case.split("/")) > 1:
                    os.chdir("/".join(case.split("/")[:-1]))
                dryrun_parent = os.getcwd()
                flags, thermal = get_flags()
                flow_command = shlex.split(flow)
                dryrun_deck = f"{dname}_DRYRUN_{os.getpid()}.DATA"
                dryrun_folder = f"plopm_{os.getpid()}"
                shutil.copyfile(f"{dname}.DATA", dryrun_deck)
                flags += " --enable-dry-run=1"
                os.makedirs(dryrun_folder, exist_ok=True)
                deck_rel = f"../{dryrun_deck}"
                os.chdir(dryrun_folder)
                if "SPE11B" in dname or "SPE11C" in dname:
                    run(
                        flow_command
                        + [deck_rel]
                        + shlex.split(flags)
                        + shlex.split(thermal),
                        check=False,
                    )
                else:
                    run(flow_command + [deck_rel] + shlex.split(flags), check=False)
                shutil.move(
                    f"{dname}_DRYRUN_{os.getpid()}-00000.vtu",
                    f"{output_abs}/{dname}-GRID.vtu",
                )
            finally:
                os.chdir(dryrun_parent)
                if dryrun_folder:
                    shutil.rmtree(dryrun_folder, ignore_errors=True)
                if dryrun_deck and os.path.isfile(dryrun_deck):
                    os.remove(dryrun_deck)
                os.chdir(cwd)
        read = get_readers(case, gif, vtk, vrs, restart, filters)
        opmtovtk(
            case,
            read,
            output,
            dname,
            save,
            restart,
            vrs,
            vtkformat_list,
            vtknames,
            k,
            skl,
            mass,
            mass_all,
            caprock,
            stress,
            filterss[k],
        )
        writepvd(
            save,
            dname,
            restart,
            read.tnrst,
            output,
            k,
        )


def writepvd(
    save: list, dname: str, restart: list, tnrst: list, output: str, k: int
) -> None:
    """Generate the pvd file"""
    where = save[k] if save[k] else dname
    base_pvd = []
    base_pvd.append(
        "<?xml version='1.0'?>\n"
        + "<VTKFile type='Collection'\n"
        + "         version='0.1'\n"
        + "         byte_order='LittleEndian'\n"
        + "         compressor='vtkZLibDataCompressor'>\n"
        + " <Collection>\n"
    )
    for i in restart:
        base_pvd.append(
            f"   <DataSet timestep='{tnrst[i]}' file='{where}-{int(i):04d}.vtu'/>\n"
        )
    base_pvd.append(" </Collection>\n</VTKFile>")
    with open(
        f"{output}/{where}.pvd",
        "w",
        encoding="utf8",
    ) as file:
        file.write("".join(base_pvd))


def warn_once(warning_keys: set, warning_key, message: str) -> None:
    """Print a warning once"""
    if warning_key not in warning_keys:
        print(message)
        warning_keys.add(warning_key)


def check_integer_conversion(
    quan: NDArray,
    var: str,
    vtkformat: str,
    target_dtype: type,
    warning_keys: set[tuple[str, str, str]],
) -> None:
    """Warn about risky integer conversions"""
    raw_quan = np.asarray(quan)
    if not raw_quan.size:
        return
    try:
        numeric_quan = np.asarray(quan, dtype=np.float64)
    except (TypeError, ValueError):
        warn_once(
            warning_keys,
            (var.upper(), vtkformat, "non_numeric"),
            f"Warning: {var.upper()} contains non-numeric values but is written as {vtkformat}.",
        )
        return
    finite_quan = numeric_quan[np.isfinite(numeric_quan)]
    if finite_quan.size != numeric_quan.size:
        warn_once(
            warning_keys,
            (var.upper(), vtkformat, "non_finite"),
            f"Warning: {var.upper()} contains non-finite values but is written as {vtkformat}.",
        )
    if not finite_quan.size:
        return
    dtype_info = np.iinfo(target_dtype)
    if np.issubdtype(target_dtype, np.unsignedinteger) and np.nanmin(finite_quan) < 0:
        warn_once(
            warning_keys,
            (var.upper(), vtkformat, "negative_unsigned"),
            f"Warning: {var.upper()} contains negative values but is written as {vtkformat}; "
            "NumPy may wrap them.",
        )
    if np.any(finite_quan != np.trunc(finite_quan)):
        warn_once(
            warning_keys,
            (var.upper(), vtkformat, "float_truncation"),
            f"Warning: {var.upper()} contains float values but is written as {vtkformat}; "
            "NumPy will truncate decimals.",
        )
    if (
        np.nanmin(finite_quan) < dtype_info.min
        or np.nanmax(finite_quan) > dtype_info.max
    ):
        warn_once(
            warning_keys,
            (var.upper(), vtkformat, "out_of_range"),
            f"Warning: {var.upper()} contains values outside {vtkformat} range [{dtype_info.min}, "
            f"{dtype_info.max}]; NumPy may wrap or fail depending on version.",
        )


def format_data_array(quan: NDArray, target_dtype: type) -> str:
    """Format values for an ascii VTK DataArray"""
    quan = np.ravel(np.asarray(quan, dtype=target_dtype))
    if np.dtype(target_dtype) == np.dtype(np.float32):
        quan = np.char.mod("%.8f", quan)
        quan = np.char.rstrip(np.char.rstrip(quan, "0"), ".")
        quan = np.where(quan == "-0", "0", quan)
    else:
        quan = quan.astype(str)
    return "\t\t\t\t\t " + " ".join(quan) + "\n\t\t\t\t\t</DataArray>"


def opmtovtk(
    case: str,
    read: ReadData,
    output: str,
    dname: str,
    save: list,
    restart,
    vrs: list,
    vtkformat_list: list,
    vtknames: list,
    k: int,
    skl: list[str],
    mass: list[str],
    mass_all: list[str],
    caprock: list[str],
    stress: float,
    filterss: str,
) -> None:
    """Generate the vtks"""
    base_vtk = []
    skip = False
    warning_keys: set[tuple[str, str, str]] = set()
    with open(f"{output}/{dname}-GRID.vtu", encoding="utf8") as file:
        for line in file:
            if skip and "CellData" in line:
                skip = False
                continue
            if "CellData" in line:
                skip = True
            if not skip:
                base_vtk.append(line)
    where = save[k] if save[k] else dname
    show_progress = sys.stdout.isatty()
    if show_progress:
        bar_ctx = alive_bar(len(restart) * len(vrs), bar="fish")
    else:
        bar_ctx = nullcontext()
    with bar_ctx as bar_animation:
        for i in restart:
            cell_data = [
                "\t\t\t\t<CellData Scalars='File created by https://github.com/cssr-tools/plopm'>",
            ]
            for n, var in enumerate(vrs):
                if show_progress:
                    bar_animation()
                unit, quan = get_quantity(
                    case,
                    read,
                    var,
                    i,
                    float(skl[n]),
                    mass,
                    mass_all,
                    caprock,
                    stress,
                    filterss,
                    False,
                    "",
                    "",
                    [False],
                )

                vtkformat = vtkformat_list[n]
                if vtkformat not in VTK_DTYPES:
                    print(f"Unknown format ({vtkformat}).")
                    sys.exit()
                target_dtype = VTK_DTYPES[vtkformat]
                if np.issubdtype(target_dtype, np.integer):
                    check_integer_conversion(
                        quan, var, vtkformat, target_dtype, warning_keys
                    )
                if vtkformat == "Float16":
                    vtkformat = "Float32"
                cell_data.append(
                    f"\n\t\t\t\t\t<DataArray type='{vtkformat}' Name="
                    + f"'{vtknames[n] if vtknames[n] else var+unit}' "
                    + "NumberOfComponents='1' format='ascii'>\n"
                )
                cell_data.append(format_data_array(quan, target_dtype))
            cell_data.append("\n\t\t\t\t</CellData>\n")
            with open(
                f"{output}/{where}-{int(i):04d}.vtu",
                "w",
                encoding="utf8",
            ) as file:
                file.write("".join(base_vtk[:4] + cell_data + base_vtk[4:]))


def make_dry_deck(dname: str) -> None:
    """Create a deck for the dry run"""
    lol = []
    with open(dname + ".DATA", "r", encoding="utf8") as file:
        for row in csv.reader(file):
            nrwo = str(row)[2:-2].strip()
            if nrwo == "SCHEDULE":
                lol.append(nrwo)
                lol.append("RPTRST\n'BASIC=2'/\n")
                lol.append("TSTEP\n0.0001/\n")
                break
            lol.append(nrwo)
    with open(
        dname + "_DRYRUN.DATA",
        "w",
        encoding="utf8",
    ) as file:
        for line in lol:
            file.write(line + "\n")


def get_flags() -> tuple[str, str]:
    """Load the flags to remove all vtk properties and perform a minimal run"""
    flags = (
        " --enable-vtk-output=1 --enable-ecl-output=0 --output-mode=none"
        + " --vtk-write-temperature=0 --vtk-write-densities=0 --vtk-write-mole-fractions=0 "
        + "--vtk-write-relative-permeabilities=0 --vtk-write-pressures=0 "
        + "--vtk-write-saturations=0 --vtk-write-porosity=0"
    )
    thermal = ""
    return flags, thermal
