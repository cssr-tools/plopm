"""Test the summary functionality"""

import os
import subprocess


def test_wells():
    """See tests/generic_deck"""
    cwd = os.getcwd()
    os.chdir(f"{cwd}/tests/generic_deck")
    subprocess.run(
        ["plopm", "-i", "SPE10_MODEL2", "-o", ".", "-w", "1"],
        check=True,
    )
    assert os.path.exists(f"{cwd}/tests/generic_deck/wells.png")
    os.chdir(cwd)
