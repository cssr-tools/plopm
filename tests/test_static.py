"""Test the default settings"""

import os
from plopm.core.plopm import main


def test_static():
    """See examples/SPE11B"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/examples")
    main()
    for name in ["porv", "poro", "permx", "permz", "satnum", "fipnum"]:
        assert os.path.exists(f"{cwd}/examples/spe11b_{name}_*,1,*_t5.png")
    os.chdir(cwd)
