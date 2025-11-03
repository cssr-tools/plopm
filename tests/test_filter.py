"""Test the filter functionality"""

import os
import pathlib
import subprocess

dirname: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_filter():
    """See examples/SPE11B"""
    os.chdir(f"{dirname}/examples")
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
            "output",
            "-i",
            "SPE11B SPE11B SPE11B",
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
            "-warnings",
            "1",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/filter.png")
