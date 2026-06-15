# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the plopm generic functionality"""

import subprocess
from plopm.core.plopm import main


def test_generic_deck(tmp_path):
    """plopm application given an input deck"""
    for name in ["PERM", "PHI", "TOPS"]:
        subprocess.run(
            [
                "curl",
                "-o",
                str(tmp_path / f"SPE10MODEL2_{name}.INC"),
                "https://raw.githubusercontent.com/OPM/opm-data/master/spe10model2/"
                + f"SPE10MODEL2_{name}.INC",
            ],
            check=True,
        )
    subprocess.run(
        [
            "curl",
            "-o",
            str(tmp_path / "SPE10_MODEL2.DATA"),
            "https://raw.githubusercontent.com/OPM/opm-data/master/spe10model2/"
            + "SPE10_MODEL2.DATA",
        ],
        check=True,
    )
    subprocess.run(
        [
            "flow",
            "SPE10_MODEL2.DATA",
            "--parsing-strictness=low",
            "--enable-dry-run=1",
            "--check-satfunc-consistency=0",
        ],
        cwd=tmp_path,
        check=True,
    )
    for slide, name, nslide, logs in zip(
        ["4,,", ",8,", ",,20"],
        ["poro", "porv", "permx"],
        ["4,j,k", "i,8,k", "i,j,20"],
        ["0", "0", "1"],
    ):
        main(
            [
                "-i",
                f"{tmp_path}/SPE10_MODEL2",
                "-o",
                str(tmp_path),
                "-v",
                name,
                "-s",
                slide,
                "-log",
                logs,
            ]
        )
        assert (tmp_path / f"spe10_model2_{name}_{nslide}_t0.png").exists()
    for name in ["grid", "wells"]:
        main(
            ["-i", f"{tmp_path}/SPE10_MODEL2", "-o", str(tmp_path), "-v", name],
        )
        assert (tmp_path / f"spe10_model2_{name}_i,1,k_t0.png").exists()
