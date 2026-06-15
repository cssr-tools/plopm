# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the default settings"""

from pathlib import Path
from plopm.core.plopm import main

mainpth: Path = Path(__file__).parents[1]


def test_dynamic(tmp_path):
    """See examples/SPE11B files"""
    main(
        [
            "-remove",
            "0,0,0,1",
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-o",
            str(tmp_path),
            "-v",
            "sgas",
            "-s",
            ",1,",
            "-c",
            "cet_CET_I2",
            "-r",
            "-1",
            "-clabel",
            "gas saturation [-]",
            "-save",
            "dynamic",
            "-f",
            "8",
        ]
    )
    assert (tmp_path / "dynamic.png").exists()
