# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the filter functionality"""

from pathlib import Path

from plopm.core.plopm import main

mainpth: Path = Path(__file__).parents[1]


def test_filter(tmp_path):
    """See examples/SPE11B"""
    main(
        [
            "-flt",
            ",fipnum >= 2 & fipnum != 4,satnum == 5",
            "-cbp",
            "0.15,0.97,0.7,0.02",
            "-t",
            "No filter  fipnum >= 2 \\& fipnum != 4  satnum == 5",
            "-st",
            "0",
            "-o",
            str(tmp_path),
            "-i",
            f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
            "-v",
            "fipnum",
            "-sg",
            "3,1",
            "-rdl",
            "1",
            "-cbf",
            ".0f",
            "-fs",
            "7,4",
            "-fn",
            "filter",
        ]
    )
    assert (tmp_path / "filter.png").exists()
