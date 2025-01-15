"""Test the difference functionality"""

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
            "-o",
            "output",
            "-i",
            "SPE11B",
            "-v",
            "rsw",
            "-diff",
            "SPE11B",
            "-warnings",
            "1",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/spe11b_rsw_i,1,k_t5.png")
