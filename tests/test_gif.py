"""Test the mask, gid, and subplot functionality"""

import os
import pathlib
import subprocess

dirname: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_difference():
    """See examples/SPE11B"""
    os.chdir(f"{dirname}/examples")
    subprocess.run(
        [
            "plopm",
            "-v",
            "xco2l",
            "-i",
            "SPE11B",
            "-m",
            "gif",
            "-mask",
            "satnum",
            "-r",
            "0,5",
            "-warnings",
            "1",
            "-interval",
            "1000",
            "-loop",
            "1",
            "-d",
            "8,5",
            "-o",
            "output",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/spe11b_xco2l.gif")
