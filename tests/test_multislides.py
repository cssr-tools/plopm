# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the multislides functionality (projections)"""

import os
import pathlib
import subprocess

testpth: pathlib.Path = pathlib.Path(__file__).parent
mainpth: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_static():
    """See examples/SPE11B"""
    if not os.path.exists(f"{testpth}/output"):
        os.system(f"mkdir {testpth}/output")
    subprocess.run(
        [
            "plopm",
            "-s",
            ",,1:58",
            "-i",
            f"{mainpth}/examples/SPE11B",
            "-v",
            "pressure - 0pressure",
            "-o",
            f"{testpth}/output",
            "-z",
            "0",
            "-save",
            "pres_incr",
        ],
        check=True,
    )
    assert os.path.exists(f"{testpth}/output/pres_incr.png")
    subprocess.run(
        [
            "plopm",
            "-o",
            f"{testpth}/output",
            "-v",
            "pressure - 0pressure",
            "-s",
            "1:83,, 1:10,,",
            "-z",
            "0",
            "-i",
            f"{mainpth}/examples/SPE11B",
            "-diff",
            f"{mainpth}/examples/SPE11B",
            "-save",
            "pres_diff",
        ],
        check=True,
    )
    assert os.path.exists(f"{testpth}/output/pres_diff.png")
    subprocess.run(
        [
            "plopm",
            "-v",
            "co2m",
            "-s",
            ",,1:58",
            "-z",
            "0",
            "-a",
            "1e-6",
            "-o",
            f"{testpth}/output",
            "-save",
            "tco2m_alongz",
            "-i",
            f"{mainpth}/examples/SPE11B",
        ],
        check=True,
    )
    assert os.path.exists(f"{testpth}/output/tco2m_alongz.png")
    subprocess.run(
        [
            "plopm",
            "-v",
            "co2m",
            "-s",
            "1:83,,",
            "-z",
            "0",
            "-a",
            "1e-6",
            "-i",
            f"{mainpth}/examples/SPE11B",
            "-save",
            "tco2m_alongx",
            "-o",
            f"{testpth}/output",
        ],
        check=True,
    )
    assert os.path.exists(f"{testpth}/output/tco2m_alongx.png")
