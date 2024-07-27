"""Test the difference functionality"""

import os
import subprocess


def test_difference():
    """See examples/SPE11B"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/examples")
    subprocess.run(
        ["plopm", "-i", "SPE11B,SPE11B", "-o", ".", "-v", "rsw"],
        check=True,
    )
    assert os.path.exists(f"{cwd}/examples/rsw_*,1,*.png")
    os.chdir(cwd)
