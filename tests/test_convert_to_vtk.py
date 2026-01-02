# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the generation of vtks from the restart files"""

import os
import pathlib
import subprocess

testpth: pathlib.Path = pathlib.Path(__file__).parent
mainpth: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_convert_to_vtk():
    """See examples/SPE11B"""
    if not os.path.exists(f"{testpth}/output"):
        os.system(f"mkdir {testpth}/output")
    os.chdir(f"{testpth}/output")
    for name in ["PVBOUNDARIES", "GRID", "FLUXNUM", "FIPNUM", "TABLES"]:
        os.system(f"cp {mainpth}/examples/{name}.INC .")
    for name in ["DATA", "EGRID", "INIT", "UNRST"]:
        os.system(f"cp {mainpth}/examples/SPE11B.{name} .")
    subprocess.run(
        [
            "plopm",
            "-v",
            "temp",
            "-i",
            "SPE11B",
            "-r",
            "0,5",
            "-m",
            "vtk",
            "-p",
            "flow",
        ],
        check=True,
    )
    for file in ["-GRID.vtu", "-0005.vtu", ".pvd"]:
        assert os.path.exists(f"{testpth}/output/SPE11B{file}")
