# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the grid and wells functionality"""

import os
import pathlib
import subprocess

testpth: pathlib.Path = pathlib.Path(__file__).parent
mainpth: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_wells_grid():
    """See tests/generic_deck"""
    message = "Please run first test_generic_deck"
    assert os.path.exists(f"{testpth}/output/generic_deck"), message
    os.chdir(f"{testpth}/output/generic_deck")
    for name in ["grid", "wells"]:
        subprocess.run(
            ["plopm", "-i", "SPE10_MODEL2", "-o", ".", "-v", name],
            check=True,
        )
        assert os.path.exists(
            f"{testpth}/output/generic_deck/spe10_model2_{name}_i,1,k_t0.png"
        )
