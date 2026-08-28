# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W3301,R0912,R0913,R0914,R0915,R0917,E1102

"""Create VTK files from OPM Flow simulation results.

The module runs a minimal OPM Flow job when grid geometry is unavailable,
populates VTU cell-data arrays for selected restart steps, and writes the PVD
collection used to open the resulting time series.
"""

import os
import shlex
import shutil
import sys
from contextlib import nullcontext
from subprocess import run

import numpy as np
from alive_progress import alive_bar
from numpy.typing import NDArray

from plopm.config.config import SimData
from plopm.utils.readers import read_case, read_quantity
from plopm.utils.terminal import cli_error_value, plopm_error, plopm_warning

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
    variables: list,
    vtkformat_list: list,
    vtknames: list,
    gif: bool,
    vtk: bool,
    filters: list,
    scales: list[str],
    mass: list[str],
    mass_all: list[str],
    caprock: list[str],
    stress: float,
    filterss: list[str],
) -> list:
    """Create VTK time-series output for the configured cases.

    A minimal OPM Flow run creates the grid-only VTU file when needed. Selected
    properties are then read from INIT or UNRST output and written to one VTU
    file per restart step.

    Parameters
    ----------
    flow : str
        Command used to run OPM Flow.
    names : list
        Simulation-case stems grouped by the CLI input.
    output : str
        Directory in which VTK files are written.
    save : list
        Optional output stems for each case.
    restart : list
        Restart report steps to export.
    variables : list
        Variables or expressions written as cell data.
    vtkformat_list : list
        VTK data type selected for each variable.
    vtknames : list
        Optional VTK array names for each variable.
    gif, vtk : bool
        Output-mode flags passed to the simulation readers.
    filters : list
        Property filters used while loading each case.
    scales : list[str]
        Scale factor applied to each variable.
    mass, mass_all : list[str]
        Mass variables and all supported mass-related variables.
    caprock : list[str]
        Supported caprock-integrity variables.
    stress : float
        Vertical stress coefficient used for caprock quantities.
    filterss : list[str]
        Filter expressions applied while reading exported quantities.

    Returns
    -------
    list[str]
        Names of the generated PVD collection files.

    """
    generated_files: list[str] = []

    for k, case in enumerate(names[0]):
        deck = case
        dname = case.split("/")[-1]
        grid_name = f"{dname}-GRID.vtu"
        grid_path = os.path.join(output, grid_name)

        if not os.path.isfile(f"{deck}.DATA"):
            plopm_error(f"unable to find {cli_error_value(f'{deck}.DATA')}.")

        if not os.path.isfile(grid_path):
            cwd = os.getcwd()
            output_abs = os.path.abspath(output)
            dryrun_deck = ""
            dryrun_folder = ""
            dryrun_parent = cwd
            try:
                if len(case.split("/")) > 1:
                    os.chdir("/".join(case.split("/")[:-1]))
                dryrun_parent = os.getcwd()
                flags, thermal = _vtk_flags()
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
                    os.path.join(output_abs, grid_name),
                )
            finally:
                os.chdir(dryrun_parent)
                if dryrun_folder:
                    shutil.rmtree(dryrun_folder, ignore_errors=True)
                if dryrun_deck and os.path.isfile(dryrun_deck):
                    os.remove(dryrun_deck)
                os.chdir(cwd)

        generated_files.append(grid_name)

        data = read_case(case, gif, vtk, variables, restart, filters)
        _write_vtk_data(
            case,
            data,
            output,
            dname,
            save,
            variables,
            vtkformat_list,
            vtknames,
            k,
            scales,
            mass,
            mass_all,
            caprock,
            stress,
            filterss[k],
        )

        where = save[k] if save[k] else dname
        generated_files.extend(
            f"{where}-{int(restart_index):04d}.vtu" for restart_index in data.steps
        )

        _write_pvd(
            save,
            dname,
            data.steps,
            data.times,
            output,
            k,
        )
        generated_files.append(f"{where}.pvd")

    return list(dict.fromkeys(generated_files))


def _write_pvd(
    save: list, dname: str, restart: list, tnrst: list, output: str, k: int
) -> None:
    """Write a PVD collection for a VTU time series.

    Parameters
    ----------
    save : list
        Optional output stems for each case.
    dname : str
        Default case name.
    restart : list
        Restart report steps included in the collection.
    tnrst : list
        Simulation times indexed by restart report step.
    output : str
        Output directory.
    k : int
        Case index used to select the output stem.

    """
    where = save[k] if save[k] else dname
    pvd_lines = []
    pvd_lines.append(
        "<?xml version='1.0'?>\n"
        + "<VTKFile type='Collection'\n"
        + "         version='0.1'\n"
        + "         byte_order='LittleEndian'\n"
        + "         compressor='vtkZLibDataCompressor'>\n"
        + " <Collection>\n"
    )
    for i in restart:
        pvd_lines.append(
            f"   <DataSet timestep='{tnrst[i]}' file='{where}-{int(i):04d}.vtu'/>\n"
        )
    pvd_lines.append(" </Collection>\n</VTKFile>")
    with open(
        f"{output}/{where}.pvd",
        "w",
        encoding="utf8",
    ) as file:
        file.write("".join(pvd_lines))


def _warn_once(warning_keys: set, warning_key, message: str) -> None:
    """Emit a warning once for a unique key.

    Parameters
    ----------
    warning_keys : set
        Keys for warnings already emitted.
    warning_key
        Hashable key identifying the warning condition.
    message : str
        Warning message.

    """
    if warning_key not in warning_keys:
        plopm_warning(message)
        warning_keys.add(warning_key)


def _check_integer_conversion(
    values: NDArray,
    var: str,
    vtkformat: str,
    target_dtype: type,
    warning_keys: set[tuple[str, str, str]],
) -> None:
    """Warn about unsafe conversion to an integer VTK type.

    Warnings cover non-numeric or non-finite values, negative values converted
    to unsigned integers, decimal truncation, and values outside the target
    integer range.

    Parameters
    ----------
    values : np.ndarray
        Quantity values to inspect.
    var : str
        Variable name used in warning messages.
    vtkformat : str
        Requested VTK data type.
    target_dtype : type
        NumPy dtype used for conversion.
    warning_keys : set[tuple[str, str, str]]
        Keys for warnings already emitted.

    """
    try:
        numeric_values = np.asarray(values, dtype=np.float64)
    except TypeError:
        _warn_once(
            warning_keys,
            (var.upper(), vtkformat, "non_numeric"),
            f"{var.upper()} contains non-numeric values but is written as {vtkformat}.",
        )
        return
    if not numeric_values.size:
        return
    finite_mask = np.isfinite(numeric_values)
    finite_values = numeric_values[finite_mask]
    if finite_values.size != numeric_values.size:
        _warn_once(
            warning_keys,
            (var.upper(), vtkformat, "non_finite"),
            f"{var.upper()} contains non-finite values but is written as {vtkformat}.",
        )
    if not finite_values.size:
        return
    dtype_info = np.iinfo(target_dtype)
    min_val = finite_values.min()
    max_val = finite_values.max()
    if np.issubdtype(target_dtype, np.unsignedinteger) and min_val < 0:
        _warn_once(
            warning_keys,
            (var.upper(), vtkformat, "negative_unsigned"),
            f"{var.upper()} contains negative values but is written as {vtkformat}; "
            "NumPy may wrap them.",
        )
    if np.any(finite_values != np.trunc(finite_values)):
        _warn_once(
            warning_keys,
            (var.upper(), vtkformat, "float_truncation"),
            f"{var.upper()} contains float values but is written as {vtkformat}; "
            "NumPy will truncate decimals.",
        )
    if min_val < dtype_info.min or max_val > dtype_info.max:
        _warn_once(
            warning_keys,
            (var.upper(), vtkformat, "out_of_range"),
            f"{var.upper()} contains values outside {vtkformat} range [{dtype_info.min}, "
            f"{dtype_info.max}]; NumPy may wrap or fail depending on version.",
        )


def _format_vtk_array(values: NDArray, target_dtype: type) -> str:
    """Format values for an ASCII VTK DataArray.

    Parameters
    ----------
    values : np.ndarray
        Values to flatten and convert.
    target_dtype : type
        NumPy dtype used for the output values.

    Returns
    -------
    str
        Tab-indented values ready for insertion into a VTU file.

    """
    values = np.ravel(np.asarray(values, dtype=target_dtype))
    if np.issubdtype(np.dtype(target_dtype), np.floating):
        values = np.char.mod("%.8f", values)
        values = np.char.rstrip(np.char.rstrip(values, "0"), ".")
        values = np.where(values == "-0", "0", values)
    else:
        values = values.astype(str)
    return "\t\t\t\t\t " + " ".join(values) + "\n\t\t\t\t\t</DataArray>"


def _write_vtk_data(
    case: str,
    data: SimData,
    output: str,
    dname: str,
    save: list,
    variables: list,
    vtkformat_list: list,
    vtknames: list,
    k: int,
    scales: list[str],
    mass: list[str],
    mass_all: list[str],
    caprock: list[str],
    stress: float,
    filterss: str,
) -> None:
    """Populate grid VTU files with simulation cell data.

    Parameters
    ----------
    case : str
        Simulation-case stem.
    data : SimData
        Loaded OPM simulation data.
    output : str
        Output directory.
    dname : str
        Default case name.
    save : list
        Optional output stems for each case.
    variables : list
        Variables or expressions written as cell data.
    vtkformat_list : list
        VTK data type selected for each variable.
    vtknames : list
        Optional VTK array names.
    k : int
        Case index used to select output settings.
    scales : list[str]
        Scale factor applied to each variable.
    mass, mass_all : list[str]
        Mass variables and all supported mass-related variables.
    caprock : list[str]
        Supported caprock-integrity variables.
    stress : float
        Vertical stress coefficient used for caprock quantities.
    filterss : str
        Filter expression applied while reading quantities.

    """
    restart = data.steps
    vtk_lines = []
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
                vtk_lines.append(line)
    where = save[k] if save[k] else dname
    show_progress = sys.stdout.isatty()
    if show_progress:
        bar_ctx = alive_bar(len(restart) * len(variables), bar="fish")
    else:
        bar_ctx = nullcontext()
    with bar_ctx as bar_animation:
        for i in restart:
            cell_data = [
                "\t\t\t\t<CellData Scalars='File created by https://github.com/cssr-tools/plopm'>",
            ]
            for n, var in enumerate(variables):
                if show_progress:
                    bar_animation()
                unit, values = read_quantity(
                    case,
                    data,
                    var,
                    i,
                    float(scales[n]),
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
                target_dtype = VTK_DTYPES[vtkformat]
                if np.issubdtype(target_dtype, np.integer):
                    _check_integer_conversion(
                        values, var, vtkformat, target_dtype, warning_keys
                    )
                # VTK XML interoperability for Float16 is limited in many readers,
                # so we emit Float32 in the DataArray type while preserving values.
                if vtkformat == "Float16":
                    vtkformat = "Float32"
                cell_data.append(
                    f"\n\t\t\t\t\t<DataArray type='{vtkformat}' Name="
                    + f"'{vtknames[n] if vtknames[n] else var+unit}' "
                    + "NumberOfComponents='1' format='ascii'>\n"
                )
                cell_data.append(_format_vtk_array(values, target_dtype))
            cell_data.append("\n\t\t\t\t</CellData>\n")
            with open(
                f"{output}/{where}-{int(i):04d}.vtu",
                "w",
                encoding="utf8",
            ) as file:
                file.write("".join(vtk_lines[:4] + cell_data + vtk_lines[4:]))


def _vtk_flags() -> tuple[str, str]:
    """Build OPM Flow options for a minimal VTK run.

    Returns
    -------
    tuple[str, str]
        General VTK options and optional thermal-model options.

    """
    flags = (
        " --enable-vtk-output=1 --enable-ecl-output=0 --output-mode=none"
        + " --vtk-write-temperature=0 --vtk-write-densities=0 --vtk-write-mole-fractions=0 "
        + "--vtk-write-relative-permeabilities=0 --vtk-write-pressures=0 "
        + "--vtk-write-saturations=0 --vtk-write-porosity=0"
    )
    thermal = ""
    return flags, thermal
