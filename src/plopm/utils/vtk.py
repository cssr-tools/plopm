# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W3301,R0912,R0915,E1102

"""
Utiliy functions to write the vtks.
"""

import os
import csv
import sys
from subprocess import PIPE, Popen
from alive_progress import alive_bar
import numpy as np
from plopm.utils.readers import get_quantity, get_readers


def make_vtks(dic):
    """
    Use OPM Flow to generate the vtk grid to populate with the given variables

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    for k, case in enumerate(dic["names"][0]):
        dic["deck"] = case
        if len(dic["deck"].split("/")) > 1:
            dic["deck"] = dic["deck"].split("/")[-1]
        if not os.path.isfile(f"{dic['output']}/{dic['deck']}-GRID.vtu"):
            cwd = os.getcwd()
            if len(case.split("/")) > 1:
                os.chdir("/".join(case.split("/")[:-1]))
            flags, thermal = get_flags()
            with Popen(
                args=f"{dic['flow']} --version", stdout=PIPE, shell=True
            ) as process:
                dic["flow_version"] = str(process.communicate()[0])[7:-3]
            # if dic["flow_version"] == "2025.04": OPM Flow dryrun+vtk is broken again ...
            make_dry_deck(dic)
            # else:
            #    os.system(f"cp {dic['deck']}.DATA {dic['deck']}_DRYRUN.DATA")
            #    flags += " --enable-dry-run=1"
            os.system("mkdir plopm_vtks_temporal")
            deck = f" ../{dic['deck']}_DRYRUN.DATA"
            os.chdir("plopm_vtks_temporal")
            if "SPE11B" in dic["deck"] or "SPE11C" in dic["deck"]:
                os.system(dic["flow"] + deck + flags + thermal)
            else:
                os.system(dic["flow"] + deck + flags)
            os.system(
                f"mv {dic['deck']}_DRYRUN-00000.vtu "
                + f"{dic['output']}/{dic['deck']}-GRID.vtu"
            )
            os.system(f"cd .. && rm -rf plopm_vtks_temporal {deck[4:]}")
            os.chdir(cwd)
        get_readers(dic)
        opmtovtk(dic, k)
        writepvd(dic, k)


def writepvd(dic, k):
    """
    Generate the pvd file\n
    k (int): Index of the geological model

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    where = dic["save"][k] if dic["save"][k] else dic["deck"]
    base_pvd = []
    base_pvd.append(
        "<?xml version='1.0'?>\n"
        + "<VTKFile type='Collection'\n"
        + "         version='0.1'\n"
        + "         byte_order='LittleEndian'\n"
        + "         compressor='vtkZLibDataCompressor'>\n"
        + " <Collection>\n"
    )
    for i in dic["restart"]:
        base_pvd.append(
            f"   <DataSet timestep='{dic['tnrst'][i]}' file='{where}-{0 if i<1000 else ''}"
            + f"{0 if i<100 else ''}{0 if i<10 else ''}{int(i)}.vtu'/>\n"
        )
    base_pvd.append(" </Collection>\n</VTKFile>")
    with open(
        f"{dic['output']}/{where}.pvd",
        "w",
        encoding="utf8",
    ) as file:
        file.write("".join(base_pvd))


def opmtovtk(dic, k):
    """
    Generate the vtks

    Args:
        dic (dict): Global dictionary\n
        k (int): Index of the geological model

    Returns:
        None

    """
    base_vtk = []
    skip = False
    with open(f"{dic['output']}/{dic['deck']}-GRID.vtu", encoding="utf8") as file:
        for line in file:
            if skip and "CellData" in line:
                skip = False
                continue
            if "CellData" in line:
                skip = True
            if not skip:
                base_vtk.append(line)
    base_vtk.insert(
        4,
        "\t\t\t\t<CellData Scalars='File created by https://github.com/cssr-tools/plopm'>",
    )
    with alive_bar(len(dic["restart"]) * len(dic["vrs"])) as bar_animation:
        for i in dic["restart"]:
            for n, var in enumerate(dic["vrs"]):
                bar_animation()
                unit, quan = get_quantity(dic, var.upper(), n, i, 0)
                if i == 0:
                    base_vtk.insert(
                        5 + 2 * n,
                        f"\n\t\t\t\t\t<DataArray type='{dic['vtkformat'][n]}' Name="
                        + f"'{dic['vtknames'][n] if dic['vtknames'][n] else var.lower()+unit}' "
                        + "NumberOfComponents='1' format='ascii'>\n",
                    )
                if dic["vtkformat"][n] == "Float64":
                    if i == 0:
                        base_vtk.insert(
                            6 + 2 * n,
                            " ".join(
                                ["\t\t\t\t\t "]
                                + [str(np.float32(val)) for val in quan]
                                + ["\n\t\t\t\t\t</DataArray>"]
                            ),
                        )
                    else:
                        base_vtk[6 + 2 * n] = " ".join(
                            ["\t\t\t\t\t "]
                            + [str(np.float32(val)) for val in quan]
                            + ["\n\t\t\t\t\t</DataArray>"]
                        )
                elif dic["vtkformat"][n] == "Float32":
                    if i == 0:
                        base_vtk.insert(
                            6 + 2 * n,
                            " ".join(
                                ["\t\t\t\t\t "]
                                + [str(np.float16(val)) for val in quan]
                                + ["\n\t\t\t\t\t</DataArray>"]
                            ),
                        )
                    else:
                        base_vtk[6 + 2 * n] = " ".join(
                            ["\t\t\t\t\t "]
                            + [str(np.float16(val)) for val in quan]
                            + ["\n\t\t\t\t\t</DataArray>"]
                        )
                elif dic["vtkformat"][n] == "UInt16":
                    if i == 0:
                        base_vtk.insert(
                            6 + 2 * n,
                            " ".join(
                                ["\t\t\t\t\t "]
                                + [str(int(val)) for val in quan]
                                + ["\n\t\t\t\t\t</DataArray>"]
                            ),
                        )
                    else:
                        base_vtk[6 + 2 * n] = " ".join(
                            ["\t\t\t\t\t "]
                            + [str(int(val)) for val in quan]
                            + ["\n\t\t\t\t\t</DataArray>"]
                        )
                else:
                    print(f"Unknow format ({dic['vtkformat'][n]}).")
                    sys.exit()
            if i == 0:
                base_vtk.insert(
                    7 + 2 * (len(dic["vrs"]) - 1), "\n\t\t\t\t</CellData>\n"
                )
            where = dic["save"][k] if dic["save"][k] else dic["deck"]
            with open(
                f"{dic['output']}/{where}-{0 if i<1000 else ''}"
                + f"{0 if i<100 else ''}{0 if i<10 else ''}{int(i)}.vtu",
                "w",
                encoding="utf8",
            ) as file:
                file.write("".join(base_vtk))


def make_dry_deck(dic):
    """
    Create a deck for the dry run

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    dic["lol"] = []
    with open(dic["deck"] + ".DATA", "r", encoding="utf8") as file:
        for row in csv.reader(file):
            nrwo = str(row)[2:-2].strip()
            if nrwo == "SCHEDULE":
                dic["lol"].append(nrwo)
                dic["lol"].append("RPTRST\n'BASIC=2'/\n")
                dic["lol"].append("TSTEP\n1*0.0001/\n")
                break
            dic["lol"].append(nrwo)
    with open(
        dic["deck"] + "_DRYRUN.DATA",
        "w",
        encoding="utf8",
    ) as file:
        for row in dic["lol"]:
            file.write(row + "\n")


def get_flags():
    """
    Load the flags to remove all vtk properties and perform a minimal run

    Args:
        None

    Returns:
        flags (str): Standard simulator flags for OPM Flow
        thermal (str): Special flags for thermal runs
        micp (str): Special flags for micp runs

    """
    flags = (
        " --enable-vtk-output=1 --enable-ecl-output=0 --output-mode=none"
        + " --vtk-write-temperature=0 --vtk-write-densities=0 --vtk-write-mole-fractions=0 "
        + "--vtk-write-relative-permeabilities=0 --vtk-write-pressures=0 "
        + "--vtk-write-saturations=0 --vtk-write-porosity=0"
    )
    # thermal = (
    #     "  --vtk-write-fluid-internal-energies=0 "
    #     + "--vtk-write-rock-internal-energy=0 --vtk-write-total-thermal-conductivity=0"
    # )
    thermal = ""
    return flags, thermal
