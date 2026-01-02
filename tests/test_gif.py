# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the mask, gid, and subplot functionality"""

import os
import pathlib
import subprocess

testpth: pathlib.Path = pathlib.Path(__file__).parent
mainpth: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_difference():
    """See examples/SPE11B"""
    if not os.path.exists(f"{testpth}/output"):
        os.system(f"mkdir {testpth}/output")
    subprocess.run(
        [
            "plopm",
            "-v",
            "xco2l",
            "-i",
            f"{mainpth}/examples/SPE11B",
            "-m",
            "gif",
            "-mask",
            "satnum",
            "-r",
            "0,1,2,3,4,5",
            "-interval",
            "1000",
            "-loop",
            "1",
            "-d",
            "8,5",
            "-o",
            f"{testpth}/output",
            "-save",
            "gif",
        ],
        check=True,
    )
    assert os.path.exists(f"{testpth}/output/gif.gif")
