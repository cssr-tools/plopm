# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the default settings"""

import os
import pathlib
import subprocess

testpth: pathlib.Path = pathlib.Path(__file__).parent
mainpth: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_dynamic():
    """See examples/SPE11B files"""
    if not os.path.exists(f"{testpth}/output"):
        os.system(f"mkdir {testpth}/output")
    subprocess.run(
        [
            "plopm",
            "-remove",
            "0,0,0,1",
            "-i",
            f"{mainpth}/examples/SPE11B",
            "-o",
            f"{testpth}/output",
            "-v",
            "sgas",
            "-s",
            ",1,",
            "-r",
            "-1",
            "-clabel",
            "gas saturation [-]",
            "-save",
            "dynamic",
            "-f",
            "8",
        ],
        check=True,
    )
    assert os.path.exists(f"{testpth}/output/dynamic.png")
