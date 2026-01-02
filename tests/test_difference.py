# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the difference functionality"""

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
            "-o",
            f"{testpth}/output",
            "-i",
            f"{mainpth}/examples/SPE11B",
            "-v",
            "rsw",
            "-diff",
            f"{mainpth}/examples/SPE11B",
            "-save",
            "difference",
        ],
        check=True,
    )
    assert os.path.exists(f"{testpth}/output/difference.png")
