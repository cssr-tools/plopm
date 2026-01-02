# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the filter functionality"""

import os
import pathlib
import subprocess

testpth: pathlib.Path = pathlib.Path(__file__).parent
mainpth: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_filter():
    """See examples/SPE11B"""
    if not os.path.exists(f"{testpth}/output"):
        os.system(f"mkdir {testpth}/output")
    subprocess.run(
        [
            "plopm",
            "-filter",
            ",fipnum >= 2 & fipnum != 4,satnum == 5",
            "-cbsfax",
            "0.15,0.97,0.7,0.02",
            "-t",
            "No filter  fipnum >= 2 \\& fipnum != 4  satnum == 5",
            "-suptitle",
            "0",
            "-o",
            f"{testpth}/output",
            "-i",
            f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
            "-v",
            "fipnum",
            "-subfigs",
            "3,1",
            "-delax",
            "1",
            "-cformat",
            ".0f",
            "-d",
            "7,4",
            "-save",
            "filter",
        ],
        check=True,
    )
    assert os.path.exists(f"{testpth}/output/filter.png")
