"""Test the difference functionality"""

import os
import subprocess


def test_difference():
    """See examples/SPE11B"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/examples")
    subprocess.run(
        ["plopm", "-i", "SPE11B", "-o", ".", "-v", "rsw", "-diff", "SPE11B"],
        check=True,
    )
    assert os.path.exists(f"{cwd}/examples/spe11b_rsw_*,1,*_t5.png")
    os.chdir(cwd)
