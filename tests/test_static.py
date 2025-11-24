"""Test the default settings"""

import os
import pathlib
import subprocess
from plopm.core.plopm import main

dirname: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_static():
    """See examples/SPE11B"""
    os.chdir(f"{dirname}/examples")
    main()
    for name in ["porv", "poro", "permx", "permz", "satnum", "fipnum"]:
        assert os.path.exists(f"{dirname}/examples/spe11b_{name}_i,1,k_t5.png")
    subprocess.run(
        [
            "plopm",
            "-v",
            "sgas",
            "-r",
            "4",
            "-c",
            "cubehelix",
            "-cticks",
            "[0, middle, 0.9]",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/spe11b_sgas_i,1,k_t4.png")
