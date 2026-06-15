# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the difference functionality"""

from pathlib import Path

from plopm.core.plopm import main

mainpth: Path = Path(__file__).parents[1]


def test_difference(tmp_path):
    """See examples/SPE11B"""
    main(
        [
            "-o",
            str(tmp_path),
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "rsw",
            "-diff",
            str(mainpth / "examples" / "SPE11B"),
            "-save",
            "difference",
        ]
    )
    assert (tmp_path / "difference.png").exists()
