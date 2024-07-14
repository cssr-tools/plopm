"""Test the single run functionality"""

import os
from plopm.core.plopm import main


def test():
    """See examples/SPE11B"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/examples")
    main()
    for name in ["porv", "poro", "permx", "satnum", "fipnum"]:
        assert os.path.exists(f"{cwd}/examples/{name}.png")
    cwd = os.getcwd()
