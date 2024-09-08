"""Test the mask, gid, and subplot functionality"""

import os
import subprocess


def test_difference():
    """See examples/SPE11B"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/examples")
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
            "-interval",
            "1000",
            "-loop",
            "1",
            "-d",
            "8,5",
        ],
        check=True,
    )
    assert os.path.exists(f"{cwd}/examples/spe11b_xco2l.gif")
    os.chdir(cwd)
