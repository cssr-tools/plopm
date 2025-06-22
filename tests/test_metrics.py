"""Test the histograms, caprock integrity, and csvs"""

import os
import pathlib
import subprocess

dirname: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_metrics():
    """See examples/SPE11B"""
    os.chdir(f"{dirname}/examples")
    subprocess.run(
        [
            "plopm",
            "-i",
            "SPE11B SPE11B SPE11B",
            "-o",
            "output",
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
            "spe11b_histogram",
            "-warnings",
            "1",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/spe11b_histogram.png")
    for name in ["limipres", "overpres", "objepres"]:
        subprocess.run(
            [
                "plopm",
                "-i",
                "SPE11B",
                "-s",
                ",,1:58",
                "-o",
                "output",
                "-v",
                name,
                "-z",
                "0",
                "-save",
                f"spe11b_{name}",
                "-warnings",
                "1",
            ],
            check=True,
        )
        assert os.path.exists(f"{dirname}/examples/output/spe11b_{name}.png")
    subprocess.run(
        [
            "plopm",
            "-i",
            "SPE11B",
            "-m",
            "csv",
            "SPE11B",
            "-o",
            "output",
            "-v",
            "objepres",
            "-s",
            ",,1:58",
            "-z",
            "0",
            "-save",
            "spe11b_objepres",
            "-warnings",
            "1",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/spe11b_objepres.csv")
