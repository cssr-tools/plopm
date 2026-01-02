# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the histograms, caprock integrity, and csvs"""

import os
import pathlib
import subprocess

testpth: pathlib.Path = pathlib.Path(__file__).parent
mainpth: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_metrics():
    """See examples/SPE11B"""
    if not os.path.exists(f"{testpth}/output"):
        os.system(f"mkdir {testpth}/output")
    subprocess.run(
        [
            "plopm",
            "-i",
            f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
            "-o",
            f"{testpth}/output",
            "-v",
            "depth,dz,tranz * 10",
            "-histogram",
            "50,norm 20,lognorm 100",
            "-c",
            "#7274b3,#cddb6e,#db6e8f",
            "-axgrid",
            "0",
            "-ylabel",
            "Histogram",
            "-save",
            "histogram",
        ],
        check=True,
    )
    assert os.path.exists(f"{testpth}/output/histogram.png")
    for name in ["limipres", "overpres", "objepres"]:
        subprocess.run(
            [
                "plopm",
                "-i",
                f"{mainpth}/examples/SPE11B",
                "-s",
                ",,1:58",
                "-o",
                f"{testpth}/output",
                "-v",
                name,
                "-z",
                "0",
                "-save",
                name,
            ],
            check=True,
        )
        assert os.path.exists(f"{testpth}/output/{name}.png")
    subprocess.run(
        [
            "plopm",
            "-i",
            f"{mainpth}/examples/SPE11B",
            "-m",
            "csv",
            "SPE11B",
            "-o",
            f"{testpth}/output",
            "-v",
            "objepres",
            "-s",
            ",,1:58",
            "-z",
            "0",
            "-save",
            "objepres",
        ],
        check=True,
    )
    assert os.path.exists(f"{testpth}/output/objepres.csv")
