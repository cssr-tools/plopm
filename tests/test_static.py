"""Test the default settings"""

import os
from plopm.core.plopm import main


def test_static():
    """See examples/SPE11B"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/examples")
    main()
    for name in ["porv", "poro", "permx", "satnum", "fipnum"]:
        assert os.path.exists(f"{cwd}/examples/{name}_*,1,*.png")
    os.chdir(cwd)
