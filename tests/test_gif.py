# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the mask, gid, and subplot functionality"""

from pathlib import Path
from plopm.core.plopm import main

mainpth: Path = Path(__file__).parents[1]


def test_gif(tmp_path):
    """See examples/SPE11B"""
    main(
        [
            "-v",
            "xco2l",
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-m",
            "gif",
            "-mask",
            "satnum",
            "-r",
            "0,1,2,3,4,5",
            "-interval",
            "1000",
            "-loop",
            "1",
            "-d",
            "8,5",
            "-o",
            str(tmp_path),
            "-save",
            "gif",
        ]
    )
    assert (tmp_path / "gif.gif").exists()
