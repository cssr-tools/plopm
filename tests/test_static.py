# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the default settings"""

from pathlib import Path
from plopm.core.plopm import main

mainpth: Path = Path(__file__).parents[1]


def test_static(tmp_path, monkeypatch):
    """See examples/SPE11B"""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "SPE11B.INIT").write_bytes(
        (mainpth / "examples" / "SPE11B.INIT").read_bytes()
    )
    (tmp_path / "SPE11B.EGRID").write_bytes(
        (mainpth / "examples" / "SPE11B.EGRID").read_bytes()
    )
    (tmp_path / "SPE11B.UNRST").write_bytes(
        (mainpth / "examples" / "SPE11B.UNRST").read_bytes()
    )
    main()
    for name in ["porv", "poro", "permx", "permz", "satnum", "fipnum"]:
        assert (tmp_path / f"spe11b_{name}_i,1,k_t5.png").exists()
    main(
        [
            "-v",
            "sgas",
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-r",
            "4",
            "-o",
            str(tmp_path),
            "-c",
            "cubehelix",
            "-cticks",
            "[0, middle, 0.9]",
        ]
    )
    assert (tmp_path / "spe11b_sgas_i,1,k_t4.png").exists()
