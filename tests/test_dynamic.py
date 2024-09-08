"""Test the default settings"""

import os
import subprocess


def test_dynamic():
    """See examples/SPE11B"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/examples")
    subprocess.run(
        [
            "plopm",
            "-i",
            "SPE11B",
            "-o",
            ".",
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
            "-remove",
            "0,0,0,1",
        ],
        check=True,
    )
    assert os.path.exists(f"{cwd}/examples/spe11b_sgas_*,1,*_t5.png")
    os.chdir(cwd)
