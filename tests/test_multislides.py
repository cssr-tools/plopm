"""Test the multislides functionality (projections)"""

import os
import subprocess


def test_static():
    """See examples/SPE11B"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/examples")
    subprocess.run(
        [
            "plopm",
            "-s",
            ",,1:58",
            "-v",
            "pressure - 0pressure",
            "-z",
            "0",
            "-save",
            "pres_incr",
        ],
        check=True,
    )
    subprocess.run(
        [
            "plopm",
            "-v",
            "pressure - 0pressure",
            "-s",
            "1:83,, 1:10,,",
            "-z",
            "0",
            "-diff",
            "SPE11B",
            "-save",
            "pres_diff",
        ],
        check=True,
    )
    subprocess.run(
        [
            "plopm",
            "-v",
            "co2m",
            "-s",
            ",,1:58",
            "-z",
            "0",
            "-a",
            "1e-6",
            "-save",
            "tco2m_alongz",
        ],
        check=True,
    )
    subprocess.run(
        [
            "plopm",
            "-v",
            "co2m",
            "-s",
            "1:83,,",
            "-z",
            "0",
            "-a",
            "1e-6",
            "-save",
            "tco2m_alongx",
        ],
        check=True,
    )
    assert os.path.exists(f"{cwd}/examples/pres_incr.png")
    assert os.path.exists(f"{cwd}/examples/pres_diff.png")
    assert os.path.exists(f"{cwd}/examples/tco2m_alongz.png")
    assert os.path.exists(f"{cwd}/examples/tco2m_alongx.png")
    os.chdir(cwd)
