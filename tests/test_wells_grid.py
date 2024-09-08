"""Test the grid and wells functionality"""

import os
import subprocess


def test_wells_grid():
    """See tests/generic_deck"""
    cwd = os.getcwd()
    os.chdir(f"{cwd}/tests/generic_deck")
    for name in ["grid", "wells"]:
        subprocess.run(
            ["plopm", "-i", "SPE10_MODEL2", "-o", ".", "-v", name],
            check=True,
        )
        assert os.path.exists(
            f"{cwd}/tests/generic_deck/spe10_model2_{name}_*,1,*_t0.png"
        )
    os.chdir(cwd)
