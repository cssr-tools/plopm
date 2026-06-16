# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the generation of vtks from the restart files"""

from pathlib import Path

from plopm.core.plopm import main

mainpth: Path = Path(__file__).parents[1]


def test_convert_to_vtk(tmp_path):
    """See examples/SPE11B"""
    main(
        [
            "-v",
            "temp",
            "-o",
            str(tmp_path),
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-m",
            "vtk",
            "-p",
            "flow",
        ]
    )
    for file in ["-GRID.vtu", "-0005.vtu", ".pvd"]:
        assert (tmp_path / f"SPE11B{file}").exists()
