# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the multislides functionality (projections)"""

from pathlib import Path

from plopm.core.plopm import main

mainpth: Path = Path(__file__).parents[1]


def test_static(tmp_path):
    """See examples/SPE11B"""
    main(
        [
            "-s",
            ",,1:58",
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "pressure - 0pressure",
            "-o",
            str(tmp_path),
            "-asp",
            "0",
            "-fn",
            "pres_incr",
        ]
    )
    assert (tmp_path / "pres_incr.png").exists()
    main(
        [
            "-o",
            str(tmp_path),
            "-v",
            "pressure - 0pressure",
            "-s",
            "1:83,, 1:10,,",
            "-asp",
            "0",
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-di",
            str(mainpth / "examples" / "SPE11B"),
            "-fn",
            "pres_diff",
        ]
    )
    assert (tmp_path / "pres_diff.png").exists()
    main(
        [
            "-v",
            "co2m",
            "-s",
            ",,1:58",
            "-asp",
            "0",
            "-sf",
            "1e-6",
            "-o",
            str(tmp_path),
            "-fn",
            "tco2m_alongz",
            "-i",
            str(mainpth / "examples" / "SPE11B"),
        ]
    )
    assert (tmp_path / "tco2m_alongz.png").exists()
    main(
        [
            "-v",
            "co2m",
            "-s",
            "1:83,,",
            "-asp",
            "0",
            "-sf",
            "1e-6",
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-fn",
            "tco2m_alongx",
            "-o",
            str(tmp_path),
        ]
    )
    assert (tmp_path / "tco2m_alongx.png").exists()
