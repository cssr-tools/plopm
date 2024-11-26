"""Test the default settings"""

import os
import pathlib
import subprocess

dirname: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_dynamic():
    """See examples/SPE11B files"""
    os.chdir(f"{dirname}/examples")
    subprocess.run(
        [
            "plopm",
            "-remove",
            "0,0,0,1",
            "-i",
            "SPE11B",
            "-o",
            "output",
            "-v",
            "sgas",
            "-s",
            ",1,",
            "-r",
            "-1",
            "-clabel",
            "gas saturation [-]",
            "-f",
            "8",
            "-warnings",
            "1",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/spe11b_sgas_*,1,*_t5.png")
