# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the plopm generic functionality"""

import os
import pathlib
import subprocess

dirname: pathlib.Path = pathlib.Path(__file__).parent


def test_generic_deck():
    """plopm application given an input deck"""
    os.chdir(dirname)
    os.system("mkdir generic_deck")
    os.chdir(f"{dirname}/generic_deck")
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
        "flow SPE10_MODEL2.DATA --parsing-strictness=low --enable-dry-run=1 "
        "--check-satfunc-consistency=0"
    )
    for slide, name, nslide, logs in zip(
        ["4,,", ",8,", ",,20"],
        ["poro", "porv", "permx"],
        ["4,j,k", "i,8,k", "i,j,20"],
        ["0", "0", "1"],
    ):
        subprocess.run(
            [
                "plopm",
                "-i",
                "SPE10_MODEL2",
                "-v",
                name,
                "-s",
                slide,
                "-u",
                "resdata",
                "-log",
                logs,
                "-warnings",
                "1",
            ],
            check=True,
        )
        assert os.path.exists(
            f"{dirname}/generic_deck/spe10_model2_{name}_{nslide}_t0.png"
        )
