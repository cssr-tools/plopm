# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the summary functionality"""

from pathlib import Path
from plopm.core.plopm import main

mainpth: Path = Path(__file__).parents[1]


def test_summary(tmp_path):
    """See examples/SPE11B"""
    for name in ["krw3", "krg2", "pcwg5"]:
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-c",
                "k",
                "-o",
                str(tmp_path),
            ]
        )
        assert (tmp_path / f"spe11b_{name}.png").exists()
    for i in range(1, 4):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "tcpu",
                "-ensemble",
                str(i),
                "-o",
                str(tmp_path),
                "-save",
                f"spe11b_ens{i}",
            ]
        )
        assert (tmp_path / f"spe11b_ens{i}.png").exists()
    main(
        [
            "-i",
            f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
            "-v",
            "fgip,fgipm,RGIP:3 / 2",
            "-loc",
            "empty,empty,empty,center",
            "-subfigs",
            "2,2",
            "-o",
            str(tmp_path),
            "-save",
            "subfigs_summary",
            "-d",
            "6,5",
            "-ylabel",
            "gas in place  mass in place  halfmass region 3",
        ]
    )
    assert (tmp_path / "subfigs_summary.png").exists()
    main(
        [
            "-i",
            f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
            "-v",
            "fgip,fgip * 2,fgip / 2",
            "-ylog",
            "1",
            "-ylabel",
            "Field gas in place",
            "-save",
            "summary",
            "-labels",
            "Reference  Times 2  Over 2",
            "-o",
            str(tmp_path),
        ]
    )
    assert (tmp_path / "summary.png").exists()
    main(
        [
            "-i",
            f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
            "-v",
            "pressure - 0pressure",
            "-s",
            "1,1,1 41,1,29 83,1,58",
            "-ylabel",
            "Pressure increase at the sensor locations [bar]",
            "-labels",
            "Left corner  Middle  Right corner",
            "-xformat",
            ".0f",
            "-yformat",
            ".0f",
            "-xlnum",
            "11",
            "-tunits",
            "y",
            "-u",
            "opm",
            "-o",
            str(tmp_path),
        ]
    )
    assert (tmp_path / "spe11b_pressure-0pressure.png").exists()
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "pressure - 0pressure",
            "-s",
            "1,1,: :,1,1 :,1,29",
            "-ylabel",
            "Pressure increase at different layers [bar]",
            "-labels",
            "Left column  Top row  Middle row",
            "-xformat",
            ".0f",
            "-yformat",
            ".0f",
            "-xlnum",
            "11",
            "-tunits",
            "y",
            "-u",
            "opm",
            "-o",
            str(tmp_path),
            "-save",
            "layers",
        ]
    )
    assert (tmp_path / "layers.png").exists()
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "sgas > 1e-2",
            "-distance",
            "max,sensor",
            "-s",
            "42,1,29",
            "-xlnum",
            "11",
            "-xunits",
            "km",
            "-o",
            str(tmp_path),
            "-save",
            "distance_sensor",
        ]
    )
    assert (tmp_path / "distance_sensor.png").exists()
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "sgas > 1e-2",
            "-distance",
            "min,border",
            "-xlnum",
            "11",
            "-xunits",
            "km",
            "-u",
            "opm",
            "-o",
            str(tmp_path),
            "-save",
            "distance_border",
        ]
    )
    assert (tmp_path / "distance_border.png").exists()
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "pressure",
            "-s",
            "1,1,:",
            "-how",
            "pvmean",
            "-o",
            str(tmp_path),
            "-save",
            "projection_layer",
        ]
    )
    assert (tmp_path / "projection_layer.png").exists()
