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
                "-ens",
                str(i),
                "-o",
                str(tmp_path),
                "-fn",
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
            "-ll",
            "empty,empty,empty,center",
            "-sg",
            "2,2",
            "-o",
            str(tmp_path),
            "-fn",
            "subfigs_summary",
            "-fs",
            "6,5",
            "-yl",
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
            "-yl",
            "Field gas in place",
            "-fn",
            "summary",
            "-llb",
            "Reference  Times 2  Over 2",
            "-o",
            str(tmp_path),
            "-sp",
            "1",
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
            "-yl",
            "Pressure increase at the sensor locations [bar]",
            "-llb",
            "Left corner  Middle  Right corner",
            "-xf",
            ".0f",
            "-yf",
            ".0f",
            "-xnt",
            "11",
            "-tu",
            "y",
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
            "-yl",
            "Pressure increase at different layers [bar]",
            "-llb",
            "Left column  Top row  Middle row",
            "-xf",
            ".0f",
            "-yf",
            ".0f",
            "-xnt",
            "11",
            "-tu",
            "y",
            "-o",
            str(tmp_path),
            "-fn",
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
            "-dist",
            "max,sensor",
            "-s",
            "42,1,29",
            "-xnt",
            "11",
            "-xu",
            "km",
            "-o",
            str(tmp_path),
            "-fn",
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
            "-dist",
            "min,border",
            "-xnt",
            "11",
            "-xu",
            "km",
            "-o",
            str(tmp_path),
            "-fn",
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
            "-agg",
            "pvmean",
            "-o",
            str(tmp_path),
            "-fn",
            "projection_layer",
        ]
    )
    assert (tmp_path / "projection_layer.png").exists()
