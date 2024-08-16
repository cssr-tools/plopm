# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the plopm generic functionality"""

import os
import subprocess


def test_generic_deck():
    """plopm application given an input deck"""
    cwd = os.getcwd()
    os.chdir(f"{cwd}/tests")
    os.system("mkdir generic_deck")
    os.chdir(f"{cwd}/tests/generic_deck")
    for name in ["PERM", "PHI", "TOPS"]:
        subprocess.run(
            [
                "curl",
                "-o",
                f"./SPE10MODEL2_{name}.INC",
                "https://raw.githubusercontent.com/OPM/opm-data/master/spe10model2/"
                + f"SPE10MODEL2_{name}.INC",
            ],
            check=True,
        )
    subprocess.run(
        [
            "curl",
            "-o",
            "./SPE10_MODEL2.DATA",
            "https://raw.githubusercontent.com/OPM/opm-data/master/spe10model2/"
            + "SPE10_MODEL2.DATA",
        ],
        check=True,
    )
    os.system(
        "flow SPE10_MODEL2.DATA --parsing-strictness=low --enable-dry-run=true & wait\n"
    )
    for slide, name, nslide in zip(
        ["4,,", ",8,", ",,20"], ["poro", "porv", "permx"], ["4,*,*", "*,8,*", "*,*,20"]
    ):
        subprocess.run(
            ["plopm", "-i", "SPE10_MODEL2", "-s", slide, "-u", "opm"],
            check=True,
        )
        assert os.path.exists(f"{cwd}/tests/generic_deck/{name}_{nslide}.png")
    os.chdir(cwd)
