"""Test the default settings"""

import os
import pathlib
from plopm.core.plopm import main

dirname: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_static():
    """See examples/SPE11B"""
    os.chdir(f"{dirname}/examples")
    main()
    for name in ["porv", "poro", "permx", "permz", "satnum", "fipnum"]:
        assert os.path.exists(f"{dirname}/examples/spe11b_{name}_*,1,*_t5.png")
