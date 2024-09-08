"""Test the summary functionality"""

import os
import subprocess


def test_summary():
    """See examples/SPE11B"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/examples")
    subprocess.run(
        ["plopm", "-i", "SPE11B", "-o", ".", "-v", "fgip", "-c", "k"],
        check=True,
    )
    assert os.path.exists(f"{cwd}/examples/fgip.png")
    os.system(
        "plopm -i 'SPE11B SPE11B' -v 'fgip,fgipm,RGIP:3 / 2' "
        "-loc empty,empty,empty,center -subfigs 2,2 -save subfigs_summary -d 6,5"
    )
    assert os.path.exists(f"{cwd}/examples/subfigs_summary.png")
    os.chdir(cwd)
