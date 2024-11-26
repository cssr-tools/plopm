"""Test the generation of vtks from the restart files"""

import os
import pathlib
import subprocess

dirname: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_convert_to_vtk():
    """See examples/SPE11B"""
    os.chdir(f"{dirname}/examples")
    subprocess.run(
        [
            "plopm",
            "-warnings",
            "1",
            "-v",
            "temp",
            "-o",
            "output",
            "-i",
            "SPE11B",
            "-r",
            "0,5",
            "-m",
            "vtk",
            "-p",
            "flow",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/SPE11B-GRID.vtu")
    assert os.path.exists(f"{dirname}/examples/output/SPE11B-0005.vtu")
    assert os.path.exists(f"{dirname}/examples/output/SPE11B.pvd")
