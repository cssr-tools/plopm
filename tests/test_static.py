# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the default settings"""

import os
import pathlib
import subprocess
from plopm.core.plopm import main

testpth: pathlib.Path = pathlib.Path(__file__).parent
mainpth: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_static():
    """See examples/SPE11B"""
    if not os.path.exists(f"{testpth}/output"):
        os.system(f"mkdir {testpth}/output")
    os.chdir(f"{testpth}/output")
    os.system(f"cp {mainpth}/examples/SPE11B.INIT .")
    os.system(f"cp {mainpth}/examples/SPE11B.EGRID .")
    main()
    for name in ["porv", "poro", "permx", "permz", "satnum", "fipnum"]:
        assert os.path.exists(f"{testpth}/output/spe11b_{name}_i,1,k_t5.png")
    subprocess.run(
        [
            "plopm",
            "-v",
            "sgas",
            "-i",
            f"{mainpth}/examples/SPE11B",
            "-r",
            "4",
            "-c",
            "cubehelix",
            "-cticks",
            "[0, middle, 0.9]",
        ],
        check=True,
    )
    assert os.path.exists(f"{testpth}/output/spe11b_sgas_i,1,k_t4.png")
