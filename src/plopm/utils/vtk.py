# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=W3301

"""
Utiliy functions to write the vtks.
"""

import os
import csv
from subprocess import PIPE, Popen
import numpy as np

try:
    from resdata.resfile import ResdataFile
except ImportError:
    print("The resdata Python package was not found, using opm")
try:
    from opm.io.ecl import EclFile as OpmFile
except ImportError:
    print("The Python package opm was not found, using resdata")


def make_vtks(dic):
    """
    Use OPM Flow to generate the vtk grid to populate with the given variables

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    dic["dry"] = "_DRYRUN"
    dic["UInt16"] = ["MPI_RANK", "SATNUM", "FIPNUM", "PVTNUM"]
    if not os.path.isfile(f"{dic['name']}-GRID.vtu"):
        cwd = os.getcwd()
        flags, thermal = get_flags()
        with Popen(args=f"{dic['flow']} --version", stdout=PIPE, shell=True) as process:
            dic["flow_version"] = str(process.communicate()[0])[7:-3]
        if dic["flow_version"] == "2024.04":
            make_dry_deck(dic)
        else:
            os.system(f"cp {dic['name']}.DATA {dic['name']+dic['dry']}.DATA")
            flags += " --enable-dry-run=1"
        os.system("mkdir plopm_vtks_temporal")
        deck = f" ../{dic['name']+dic['dry']}.DATA"
        os.chdir("plopm_vtks_temporal")
        if "SPE11B" in dic["name"] or "SPE11C" in dic["name"]:
            os.system(dic["flow"] + deck + flags + thermal)
        else:
            os.system(dic["flow"] + deck + flags)
        os.system(f"mv {dic['name']+dic['dry']}-00000.vtu ../{dic['name']}-GRID.vtu")
        os.system(f"cd .. && rm -rf plopm_vtks_temporal {deck[4:]}")
        os.chdir(cwd)
    for ext in ["init", "unrst"]:
        if os.path.isfile(f"{dic['name']}.{ext.upper()}"):
            if dic["use"] == "resdata":
                dic[ext] = ResdataFile(f"{dic['name']}.{ext.upper()}")
            else:
                dic[ext] = OpmFile(f"{dic['name']}.{ext.upper()}")
    if not "init" in dic.keys() or not "unrst" in dic.keys():
        return
    if dic["use"] == "resdata":
        opmtovtk_resdata(dic)
    else:
        opmtovtk_opm(dic)


def opmtovtk_resdata(dic):
    """
    Use resdata to generate the vtks

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    base_vtk = []
    skip = False
    with open(f"{dic['name']}-GRID.vtu", encoding="utf8") as file:
        for line in file:
            if skip and "CellData" in line:
                skip = False
                continue
            if "CellData" in line:
                skip = True
            if not skip:
                base_vtk.append(line)
    i, n, inc = int(dic["restart"][0]), 0, 0
    base_vtk.insert(4, "\t\t\t\t<CellData Scalars='porosity'>")
    for n, var in enumerate(dic["variable"].split(",")):
        if var.upper() in dic["UInt16"]:
            if var.upper() == "MPI_RANK":
                inc = 1
            base_vtk.insert(
                5 + 2 * n,
                f"\n\t\t\t\t\t<DataArray type='UInt16' Name='{var.lower()}' "
                + "NumberOfComponents='1' format='ascii'>\n",
            )
            if dic["init"].has_kw(var.upper()):
                base_vtk.insert(
                    6 + 2 * n,
                    " ".join(
                        ["\t\t\t\t\t "]
                        + [str(int(val) + inc) for val in dic["init"][var.upper()][0]]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    ),
                )
            else:
                base_vtk.insert(
                    6 + 2 * n,
                    " ".join(
                        ["\t\t\t\t\t "]
                        + [str(int(val) + inc) for val in dic["unrst"][var.upper()][i]]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    ),
                )
        else:
            base_vtk.insert(
                5 + 2 * n,
                f"\n\t\t\t\t\t<DataArray type='Float32' Name='{var.lower()}' "
                + "NumberOfComponents='1' format='ascii'>\n",
            )
            if dic["init"].has_kw(var.upper()):
                base_vtk.insert(
                    6 + 2 * n,
                    " ".join(
                        ["\t\t\t\t\t "]
                        + [str(np.float16(val)) for val in dic["init"][var.upper()][0]]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    ),
                )
            else:
                base_vtk.insert(
                    6 + 2 * n,
                    " ".join(
                        ["\t\t\t\t\t "]
                        + [str(np.float16(val)) for val in dic["unrst"][var.upper()][i]]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    ),
                )

    base_vtk.insert(7 + 2 * n, "\n\t\t\t\t</CellData>\n")
    with open(
        f"{dic['name']}-{0 if i<1000 else ''}{0 if i<100 else ''}{0 if i<10 else ''}{int(i)}.vtu",
        "w",
        encoding="utf8",
    ) as file:
        file.write("".join(base_vtk))
    additional_vtks_resdata(dic, base_vtk)


def additional_vtks_resdata(dic, base_vtk):
    """
    Use resdata to generate the additional vtks

    Args:
        dic (dict): Global dictionary
        base_vtk (list): Body text of the vtk template
        i (int):

    Returns:
        None

    """
    if int(dic["restart"][0]) == 0 and len(dic["restart"]) == 2:
        dic["restart"] = range(0, int(dic["restart"][1]) + 1)
    for i in dic["restart"][1:]:
        i_i = int(i)
        for n, var in enumerate(dic["variable"].split(",")):
            if var.upper() in dic["UInt16"]:
                if var.upper() == "MPI_RANK":
                    inc = 1
                base_vtk[5 + 2 * n] = (
                    f"\n\t\t\t\t\t<DataArray type='UInt16' Name='{var.lower()}' "
                    + "NumberOfComponents='1' format='ascii'>\n"
                )
                if dic["init"].has_kw(var.upper()):
                    base_vtk[6 + 2 * n] = " ".join(
                        ["\t\t\t\t\t "]
                        + [str(int(val) + inc) for val in dic["init"][var.upper()][0]]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    )
                else:
                    base_vtk[6 + 2 * n] = " ".join(
                        ["\t\t\t\t\t "]
                        + [
                            str(int(val) + inc)
                            for val in dic["unrst"][var.upper()][i_i]
                        ]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    )
            else:
                base_vtk[5 + 2 * n] = (
                    f"\n\t\t\t\t\t<DataArray type='Float32' Name='{var.lower()}' "
                    + "NumberOfComponents='1' format='ascii'>\n"
                )
                if dic["init"].has_kw(var.upper()):
                    base_vtk[6 + 2 * n] = " ".join(
                        ["\t\t\t\t\t "]
                        + [str(np.float16(val)) for val in dic["init"][var.upper()][0]]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    )
                else:
                    base_vtk[6 + 2 * n] = " ".join(
                        ["\t\t\t\t\t "]
                        + [
                            str(np.float16(val))
                            for val in dic["unrst"][var.upper()][i_i]
                        ]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    )
        with open(
            f"{dic['name']}-{0 if i_i<1000 else ''}{0 if i_i<100 else ''}"
            + f"{0 if i_i<10 else ''}{i_i}.vtu",
            "w",
            encoding="utf8",
        ) as file:
            file.write("".join(base_vtk))


def opmtovtk_opm(dic):
    """
    Use opm to generate the vtks

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    base_vtk = []
    skip = False
    with open(f"{dic['name']}-GRID.vtu", encoding="utf8") as file:
        for line in file:
            if skip and "CellData" in line:
                skip = False
                continue
            if "CellData" in line:
                skip = True
            if not skip:
                base_vtk.append(line)
    i, n, inc = int(dic["restart"][0]), 0, 0
    base_vtk.insert(4, "\t\t\t\t<CellData Scalars='porosity'>")
    for n, var in enumerate(dic["variable"].split(",")):
        if var.upper() in dic["UInt16"]:
            if var.upper() == "MPI_RANK":
                inc = 1
            base_vtk.insert(
                5 + 2 * n,
                f"\n\t\t\t\t\t<DataArray type='UInt16' Name='{var.lower()}' "
                + "NumberOfComponents='1' format='ascii'>\n",
            )
            if dic["init"].count(var.upper()):
                base_vtk.insert(
                    6 + 2 * n,
                    " ".join(
                        ["\t\t\t\t\t "]
                        + [str(int(val) + inc) for val in dic["init"][var.upper()]]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    ),
                )
            else:
                base_vtk.insert(
                    6 + 2 * n,
                    " ".join(
                        ["\t\t\t\t\t "]
                        + [str(int(val) + inc) for val in dic["unrst"][var.upper(), i]]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    ),
                )
        else:
            base_vtk.insert(
                5 + 2 * n,
                f"\n\t\t\t\t\t<DataArray type='Float32' Name='{var.lower()}' "
                + "NumberOfComponents='1' format='ascii'>\n",
            )
            if dic["init"].count(var.upper()):
                base_vtk.insert(
                    6 + 2 * n,
                    " ".join(
                        ["\t\t\t\t\t "]
                        + [str(np.float16(val)) for val in dic["init"][var.upper()]]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    ),
                )
            else:
                base_vtk.insert(
                    6 + 2 * n,
                    " ".join(
                        ["\t\t\t\t\t "]
                        + [str(np.float16(val)) for val in dic["unrst"][var.upper(), i]]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    ),
                )
    base_vtk.insert(7 + 2 * n, "\n\t\t\t\t</CellData>\n")
    with open(
        f"{dic['name']}-{0 if i<1000 else ''}{0 if i<100 else ''}{0 if i<10 else ''}{int(i)}.vtu",
        "w",
        encoding="utf8",
    ) as file:
        file.write("".join(base_vtk))
    additional_vtks_opm(dic, base_vtk)


def additional_vtks_opm(dic, base_vtk):
    """
    Use opm to generate the additional vtks

    Args:
        dic (dict): Global dictionary
        base_vtk (list): Body text of the vtk template
        i (int):

    Returns:
        None

    """
    if int(dic["restart"][0]) == 0 and len(dic["restart"]) == 2:
        dic["restart"] = range(0, int(dic["restart"][1]) + 1)
    for i in dic["restart"][1:]:
        i_i = int(i)
        for n, var in enumerate(dic["variable"].split(",")):
            if var.upper() in dic["UInt16"]:
                if var.upper() == "MPI_RANK":
                    inc = 1
                base_vtk[5 + 2 * n] = (
                    f"\n\t\t\t\t\t<DataArray type='UInt16' Name='{var.lower()}' "
                    + "NumberOfComponents='1' format='ascii'>\n"
                )
                if dic["init"].count(var.upper()):
                    base_vtk[6 + 2 * n] = " ".join(
                        ["\t\t\t\t\t "]
                        + [str(int(val) + inc) for val in dic["init"][var.upper()]]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    )
                else:
                    base_vtk[6 + 2 * n] = " ".join(
                        ["\t\t\t\t\t "]
                        + [
                            str(int(val) + inc)
                            for val in dic["unrst"][var.upper(), i_i]
                        ]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    )
            else:
                base_vtk[5 + 2 * n] = (
                    f"\n\t\t\t\t\t<DataArray type='Float32' Name='{var.lower()}' "
                    + "NumberOfComponents='1' format='ascii'>\n"
                )
                if dic["init"].count(var.upper()):
                    base_vtk[6 + 2 * n] = " ".join(
                        ["\t\t\t\t\t "]
                        + [str(np.float16(val)) for val in dic["init"][var.upper()]]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    )
                else:
                    base_vtk[6 + 2 * n] = " ".join(
                        ["\t\t\t\t\t "]
                        + [
                            str(np.float16(val))
                            for val in dic["unrst"][var.upper(), i_i]
                        ]
                        + ["\n\t\t\t\t\t</DataArray>"]
                    )
        with open(
            f"{dic['name']}-{0 if i_i<1000 else ''}{0 if i_i<100 else ''}"
            + f"{0 if i_i<10 else ''}{i_i}.vtu",
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
    with open(dic["name"] + ".DATA", "r", encoding="utf8") as file:
        for row in csv.reader(file):
            nrwo = str(row)[2:-2].strip()
            if nrwo == "SCHEDULE":
                dic["lol"].append(nrwo)
                dic["lol"].append("RPTRST\n'BASIC=2'/\n")
                dic["lol"].append("TSTEP\n1*0.0001/\n")
                break
            dic["lol"].append(nrwo)
    with open(
        dic["name"] + "_DRYRUN.DATA",
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
