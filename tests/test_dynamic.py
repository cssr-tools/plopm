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
            "r",
            "-1",
            "l",
            "[-]",
        ],
        check=True,
    )
    assert os.path.exists(f"{cwd}/examples/sgas_*,1,*.png")
    os.chdir(cwd)
