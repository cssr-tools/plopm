"""Test the grid and wells functionality"""

import os
import pathlib
import subprocess

dirname: pathlib.Path = pathlib.Path(__file__).parent


def test_wells_grid():
    """See tests/generic_deck"""
    os.chdir(f"{dirname}/generic_deck")
    for name in ["grid", "wells"]:
        subprocess.run(
            ["plopm", "-i", "SPE10_MODEL2", "-o", ".", "-v", name, "-warnings", "1"],
            check=True,
        )
        assert os.path.exists(
            f"{dirname}/generic_deck/spe10_model2_{name}_*,1,*_t0.png"
        )
