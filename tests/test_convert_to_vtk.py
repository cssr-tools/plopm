"""Test the generation of vtks from the restart files"""

import os
import subprocess


def test_convert_to_vtk():
    """See examples/SPE11B"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/examples")
    subprocess.run(
        [
            "plopm",
            "-o",
            ".",
            "-i",
            "SPE11B",
            "-v",
            "temp",
            "-r",
            "0,5",
            "-m",
            "vtk",
            "-p",
            "flow",
        ],
        check=True,
    )
    assert os.path.exists(f"{cwd}/examples/SPE11B-GRID.vtu")
    assert os.path.exists(f"{cwd}/examples/SPE11B-0005.vtu")
    os.chdir(cwd)
