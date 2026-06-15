# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the histograms, caprock integrity, and csvs"""

from pathlib import Path
from plopm.core.plopm import main

mainpth: Path = Path(__file__).parents[1]


def test_metrics(tmp_path):
    """See examples/SPE11B"""
    main(
        [
            "-i",
            f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
            "-o",
            str(tmp_path),
            "-v",
            "depth,dz,tranz * 10",
            "-histogram",
            "50,norm 20,lognorm 100",
            "-c",
            "#7274b3,#cddb6e,#db6e8f",
            "-axgrid",
            "0",
            "-ylabel",
            "Histogram",
            "-save",
            "histogram",
        ]
    )
    assert (tmp_path / "histogram.png").exists()
    for name in ["limipres", "overpres", "objepres"]:
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-s",
                ",,1:58",
                "-o",
                str(tmp_path),
                "-v",
                name,
                "-z",
                "0",
                "-save",
                name,
            ]
        )
        assert (tmp_path / f"{name}.png").exists()
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-m",
            "csv",
            "SPE11B",
            "-o",
            str(tmp_path),
            "-v",
            "objepres",
            "-s",
            ",,1:58",
            "-z",
            "0",
            "-save",
            "objepres",
        ]
    )
    assert (tmp_path / "objepres.csv").exists()
