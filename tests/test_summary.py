"""Test the summary functionality"""

import os
import pathlib
import subprocess

dirname: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_summary():
    """See examples/SPE11B"""
    os.chdir(f"{dirname}/examples")
    subprocess.run(
        [
            "plopm",
            "-i",
            "SPE11B",
            "-v",
            "fgip",
            "-c",
            "k",
            "-warnings",
            "1",
            "-o",
            "output",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/fgip.png")
    subprocess.run(
        [
            "plopm",
            "-i",
            "SPE11B SPE11B",
            "-v",
            "fgip,fgipm,RGIP:3 / 2",
            "-loc",
            "empty,empty,empty,center",
            "-subfigs",
            "2,2",
            "-o",
            "output",
            "-save",
            "subfigs_summary",
            "-d",
            "6,5",
            "-ylabel",
            "gas in place  mass in place  halfmass region 3",
            "-warnings",
            "1",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/subfigs_summary.png")
    subprocess.run(
        [
            "plopm",
            "-i",
            "SPE11B SPE11B SPE11B",
            "-v",
            "fgip,fgip * 2,fgip / 2",
            "-ylog",
            "1",
            "-ylabel",
            "Field gas in place",
            "-save",
            "summary",
            "-labels",
            "Reference  Times 2  Over 2",
            "-warnings",
            "1",
            "-o",
            "output",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/summary.png")
