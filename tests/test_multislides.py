"""Test the multislides functionality (projections)"""

import os
import pathlib
import subprocess

dirname: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_static():
    """See examples/SPE11B"""
    os.chdir(f"{dirname}/examples")
    subprocess.run(
        [
            "plopm",
            "-s",
            ",,1:58",
            "-v",
            "pressure - 0pressure",
            "-o",
            "output",
            "-z",
            "0",
            "-save",
            "pres_incr",
            "-warnings",
            "1",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/pres_incr.png")
    subprocess.run(
        [
            "plopm",
            "-o",
            "output",
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
            "-warnings",
            "1",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/pres_diff.png")
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
            "-o",
            "output",
            "-save",
            "tco2m_alongz",
            "-warnings",
            "1",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/tco2m_alongz.png")
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
            "-o",
            "output",
            "-warnings",
            "1",
        ],
        check=True,
    )
    assert os.path.exists(f"{dirname}/examples/output/tco2m_alongx.png")
