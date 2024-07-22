"""Test the summary functionality"""

import os
import subprocess


def test_summary():
    """See examples/SPE11B"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/examples")
    subprocess.run(
        ["plopm", "-i", "SPE11B", "-o", ".", "-v", "fgip", "-c", "k"],
        check=True,
    )
    assert os.path.exists(f"{cwd}/examples/fgip.png")
    os.chdir(cwd)
