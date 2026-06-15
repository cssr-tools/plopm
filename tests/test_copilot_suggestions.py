# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0116,C0302

"""Test by iterating with Copilot looking at the pylint coverage report"""

from pathlib import Path
import numpy as np
from PIL import Image
import pytest

from plopm.core.plopm import main
from plopm.utils.readers import (
    get_unit,
    initialize_time,
    operate,
    handle_filter,
    project,
    get_indices,
)

testpth: Path = Path(__file__).parent
mainpth: Path = Path(__file__).parents[1]
boxpth: Path = testpth / "data" / "3dbox" / "3DBOX"


def assert_png_ok(path):
    assert path.exists()
    image = Image.open(path)
    pixels = np.array(image)
    assert pixels.mean() > 5
    assert pixels.std() > 1


def assert_file_ok(path):
    assert path.exists()
    assert path.stat().st_size > 0


def test_readers_histogram_expression_operands(tmp_path):
    for name, histogram, save in zip(
        ["pressure - 0pressure", "poro * 2", "sgas + swat", "co2m / 1e6"],
        ["10,norm", "10", "10,norm", "10,lognorm"],
        [
            "hist_restart_operand",
            "hist_scalar_operand",
            "hist_saturation_operand",
            "hist_mass_operand",
        ],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-histogram",
                histogram,
                "-axgrid",
                "0",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_readers_distance_indices_and_operations(tmp_path):
    for name, distance, slide, save in zip(
        ["index_i == 2", "index_j != 1", "index_k >= 2"],
        ["max,sensor", "min,border", "max,border"],
        ["2,2,2", ",2,", ",2,"],
        ["distance_index_i", "distance_index_j", "distance_index_k"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-distance",
                distance,
                "-s",
                slide,
                "-xunits",
                "m",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_readers_layer_operations_all_directions(tmp_path):
    for slide, name, how, save in zip(
        [":,2,2", "2,:,2", "2,2,:"],
        ["poro + 0.1", "permy / 2", "permz * 2"],
        ["mean", "mean", "mean"],
        ["layer_expr_i", "layer_expr_j", "layer_expr_k"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_readers_summary_time_and_minutes(tmp_path):
    for name, tunits, save in zip(
        ["time", "fgip"],
        ["d", "m"],
        ["summary_time_variable", "summary_minutes"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-tunits",
                tunits,
                "-xlnum",
                "4",
                "-ylnum",
                "4",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_readers_pcfact_from_data_and_include(tmp_path):
    (tmp_path / "PCFACT_DIRECT.DATA").write_text(
        "PCFACT\n0.0 1.0\n1.0 2.0 /\n",
        encoding="utf8",
    )
    main(
        [
            "-i",
            str(tmp_path / "PCFACT_DIRECT"),
            "-v",
            "pcfact1",
            "-o",
            str(tmp_path),
            "-save",
            "pcfact_direct",
        ]
    )
    assert_png_ok(tmp_path / "pcfact_direct.png")
    (tmp_path / "pcfact.inc").write_text(
        "PCFACT\n0.0 1.0\n1.0 2.0 /\nPCFACT\n0.0 3.0\n1.0 4.0 /\n",
        encoding="utf8",
    )
    (tmp_path / "PCFACT_INCLUDE.DATA").write_text(
        "INCLUDE\n'pcfact.inc' /\n",
        encoding="utf8",
    )
    main(
        [
            "-i",
            str(tmp_path / "PCFACT_INCLUDE"),
            "-v",
            "pcfact2",
            "-o",
            str(tmp_path),
            "-save",
            "pcfact_include",
        ]
    )
    assert_png_ok(tmp_path / "pcfact_include.png")


def test_readers_csv_input_gif_mode(tmp_path):
    for restart in ["0", "1"]:
        (tmp_path / f"csvgif{restart}.csv").write_text(
            "x,y,value\n"
            "1,1,1\n"
            "3,1,2\n"
            "5,1,3\n"
            "1,3,4\n"
            "3,3,5\n"
            "5,3,6\n"
            "1,5,7\n"
            "3,5,8\n"
            "5,5,9\n",
            encoding="utf8",
        )
    main(
        [
            "-i",
            str(tmp_path / "csvgifPLOPM"),
            "-csv",
            "1,2,3",
            "-v",
            "value",
            "-m",
            "gif",
            "-r",
            "0,1",
            "-interval",
            "200",
            "-loop",
            "0",
            "-o",
            str(tmp_path),
            "-save",
            "csv_gif_input",
        ]
    )
    assert_file_ok(tmp_path / "csv_gif_input.gif")


def test_readers_source_wells_and_faults_from_data(tmp_path):
    for suffix in [".DATA", ".INIT", ".EGRID"]:
        (tmp_path / f"BOXSRC{suffix}").write_bytes(
            (testpth / "data" / "3dbox" / f"3DBOX{suffix}").read_bytes()
        )
    with open(tmp_path / "BOXSRC.DATA", "a", encoding="utf8") as file:
        file.write("\nSOURCE\n1 1 1 /\n/\nFAULTS\nF1 1 1 1 3 1 3 /\n/\n")
    for name, slide, how, save in zip(
        ["wells", "faults", "wells", "faults"],
        ["2,,", "2,,", ",2,", ",,2"],
        ["min", "min", "max", "max"],
        ["source_wells_i", "faults_i", "source_wells_j", "faults_k"],
    ):
        main(
            [
                "-i",
                str(tmp_path / "BOXSRC"),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_readers_mass_type_variants(tmp_path):
    for name, save in zip(
        ["gasm", "dism", "liqm", "vapm", "xco2v", "xh2ol"],
        [
            "mass_gasm",
            "mass_dism",
            "mass_liqm",
            "mass_vapm",
            "mass_xco2v",
            "mass_xh2ol",
        ],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-s",
                ",,1:58",
                "-z",
                "0",
                "-a",
                "1e-6",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_readers_saturation_variants(tmp_path):
    for name, save in zip(
        ["soil", "swat", "sgas"],
        ["sat_soil", "sat_swat", "sat_sgas"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-r",
                "1",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_readers_index_arithmetic_in_quantity(tmp_path):
    for name, save in zip(
        ["index_i + index_j", "index_k * 2", "index_i != index_j"],
        ["index_add", "index_times", "index_compare"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                ",2,",
                "-cformat",
                ".0f",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_readers_direct_utility_functions():
    assert initialize_time("m")[1] == "Time [minutes]"
    assert get_unit("disperc") == " [m]"
    assert get_unit("rpr") == " [bar]"
    assert get_unit("fgit") == " [sm$^3$]"
    assert get_indices("index_i", 2, 2, 2) == [1, 2, 1, 2, 1, 2, 1, 2]
    assert get_indices("index_j", 2, 2, 2) == [1, 1, 2, 2, 1, 1, 2, 2]
    assert get_indices("index_k", 2, 2, 2) == [1, 1, 1, 1, 2, 2, 2, 2]


def test_readers_error_branches():
    with pytest.raises(SystemExit):
        operate(np.array([1.0]), 1.0, ["bad"][0])
    with pytest.raises(SystemExit):
        handle_filter([1.0], [1.0], "bad", 1.0)
    with pytest.raises(SystemExit):
        project(np.array([1.0]), "bad", np.array([1.0]))


def test_readers_missing_input_exits(tmp_path):
    with pytest.raises(SystemExit):
        main(
            [
                "-i",
                str(tmp_path / "missing_case"),
                "-v",
                "poro",
                "-o",
                str(tmp_path),
            ]
        )


def test_write_gif_subfigs_multiple_variables(tmp_path):
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "sgas,pressure",
            "-m",
            "gif",
            "-r",
            "0,1",
            "-subfigs",
            "1,2",
            "-interval",
            "200",
            "-loop",
            "0",
            "-d",
            "8,4",
            "-o",
            str(tmp_path),
            "-save",
            "gif_subfigs_vars",
        ]
    )
    assert_file_ok(tmp_path / "gif_subfigs_vars.gif")


def test_write_gif_subfigs_multiple_decks(tmp_path):
    main(
        [
            "-i",
            f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
            "-v",
            "sgas",
            "-m",
            "gif",
            "-r",
            "0,1",
            "-subfigs",
            "1,2",
            "-interval",
            "200",
            "-loop",
            "1",
            "-d",
            "8,4",
            "-o",
            str(tmp_path),
            "-save",
            "gif_subfigs_decks",
        ]
    )
    assert_file_ok(tmp_path / "gif_subfigs_decks.gif")


def test_write_png_subfigs_multiple_restarts(tmp_path):
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "sgas",
            "-r",
            "0,1,2",
            "-subfigs",
            "1,3",
            "-delax",
            "1",
            "-cbsfax",
            "0.25,0.92,0.5,0.03",
            "-d",
            "10,4",
            "-o",
            str(tmp_path),
            "-save",
            "png_subfigs_restarts",
        ]
    )
    assert_png_ok(tmp_path / "png_subfigs_restarts.png")


def test_write_dates_for_map_and_summary(tmp_path):
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "pressure",
            "-r",
            "1",
            "-tunits",
            "dates",
            "-o",
            str(tmp_path),
            "-save",
            "map_dates",
        ]
    )
    assert_png_ok(tmp_path / "map_dates.png")
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "fgip",
            "-tunits",
            "dates",
            "-xlnum",
            "3",
            "-o",
            str(tmp_path),
            "-save",
            "summary_dates",
        ]
    )
    assert_png_ok(tmp_path / "summary_dates.png")


def test_write_custom_rgb_listed_colormap(tmp_path):
    for colors, bounds, save in zip(
        ["255;0;0 0;255;0 0;0;255", "0;0;0 128;128;128 255;255;255"],
        ["[1,3]", "[1,3]"],
        ["rgb_listed", "gray_listed"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                "index_j",
                "-s",
                ",2,",
                "-c",
                colors,
                "-b",
                bounds,
                "-cnum",
                "3",
                "-cformat",
                ".0f",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_write_log_colorbar_subfigs_with_ticks(tmp_path):
    main(
        [
            "-i",
            str(boxpth),
            "-v",
            "permx,permy",
            "-s",
            ",2,",
            "-log",
            "1,1",
            "-clogthks",
            "[1,10,100]",
            "-subfigs",
            "1,2",
            "-cbsfax",
            "0.25,0.92,0.5,0.03",
            "-d",
            "8,4",
            "-o",
            str(tmp_path),
            "-save",
            "log_colorbar_subfigs",
        ]
    )
    assert_png_ok(tmp_path / "log_colorbar_subfigs.png")


def test_write_csv_input_spatial_map(tmp_path):
    csvpath = tmp_path / "csvmap.csv"
    csvpath.write_text(
        "x,y,value\n"
        "1,1,1\n"
        "3,1,2\n"
        "5,1,3\n"
        "1,3,4\n"
        "3,3,5\n"
        "5,3,6\n"
        "1,5,7\n"
        "3,5,8\n"
        "5,5,9\n",
        encoding="utf8",
    )
    main(
        [
            "-i",
            str(tmp_path / "csvmap"),
            "-csv",
            "1,2,3",
            "-v",
            "value",
            "-c",
            "viridis",
            "-xunits",
            "m",
            "-yunits",
            "m",
            "-o",
            str(tmp_path),
            "-save",
            "csv_input_map",
        ]
    )
    assert_png_ok(tmp_path / "csv_input_map.png")


def test_write_csv_input_summary(tmp_path):
    csvpath = tmp_path / "csvsummary.csv"
    csvpath.write_text(
        "time,value\n0,1\n1,2\n2,4\n3,8\n",
        encoding="utf8",
    )
    main(
        [
            "-i",
            str(tmp_path / "csvsummary"),
            "-csv",
            "1,2",
            "-v",
            "value",
            "-tunits",
            "d",
            "-ylabel",
            "CSV value",
            "-o",
            str(tmp_path),
            "-save",
            "csv_input_summary",
        ]
    )
    assert_png_ok(tmp_path / "csv_input_summary.png")


def test_write_summary_mode_csv_output(tmp_path):
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-m",
            "csv",
            "-v",
            "fgip",
            "-o",
            str(tmp_path),
            "-save",
            "summary_csv_output",
        ]
    )
    assert_file_ok(tmp_path / "summary_csv_output.csv")


def test_write_grid_wells_faults_colorbar_paths(tmp_path):
    for name, slide, globalflag, save in zip(
        ["grid", "wells", "faults"],
        [",2,", ",2,", ",2,"],
        ["0", "1", "1"],
        ["write_grid", "write_wells_global", "write_faults_global"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-global",
                globalflag,
                "-c",
                "tab20",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_write_remove_axes_combinations(tmp_path):
    for remove, title, save in zip(
        ["1,0,0,0", "0,1,0,0", "0,0,1,0", "0,0,0,1"],
        ["Left removed", "Bottom removed", "Colorbar removed", "Title removed"],
        ["remove_left", "remove_bottom", "remove_colorbar", "remove_title"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                "poro",
                "-s",
                ",2,",
                "-remove",
                remove,
                "-t",
                title,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_write_subfigs_multi_deck_single_variable_legend_axis(tmp_path):
    main(
        [
            "-i",
            f"{boxpth} {boxpth} {boxpth}",
            "-v",
            "poro",
            "-s",
            "2,, ,2, ,,2",
            "-subfigs",
            "1,3",
            "-suptitle",
            "0",
            "-cbsfax",
            "0.25,0.92,0.5,0.03",
            "-delax",
            "1",
            "-d",
            "10,4",
            "-o",
            str(tmp_path),
            "-save",
            "multi_deck_single_var_axes",
        ]
    )
    assert_png_ok(tmp_path / "multi_deck_single_var_axes.png")


def test_write_subfigs_multi_variable_single_deck_axis(tmp_path):
    main(
        [
            "-i",
            str(boxpth),
            "-v",
            "poro,index_i,index_j,index_k",
            "-s",
            ",2,",
            "-subfigs",
            "2,2",
            "-delax",
            "1",
            "-cformat",
            ".0f",
            "-d",
            "7,6",
            "-o",
            str(tmp_path),
            "-save",
            "multi_var_single_deck_axes",
        ]
    )
    assert_png_ok(tmp_path / "multi_var_single_deck_axes.png")


def test_3dbox_slide_parser_single_range_and_colon(tmp_path):
    for slide, name, save in zip(
        ["2,,", "1:3,,", ":,,"],
        ["permx", "permx", "permx"],
        ["box_slide_x_single", "box_slide_x_range", "box_slide_x_colon"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-grid",
                "black,1e-3",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")
    for slide, name, save in zip(
        [",2,", ",1:3,", ",:,"],
        ["permy", "permy", "permy"],
        ["box_slide_y_single", "box_slide_y_range", "box_slide_y_colon"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-grid",
                "black,1e-3",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")
    for slide, name, save in zip(
        [",,2", ",,1:3", ",,:"],
        ["permz", "permz", "permz"],
        ["box_slide_z_single", "box_slide_z_range", "box_slide_z_colon"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-grid",
                "black,1e-3",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_default_projection_branches_by_direction(tmp_path):
    for slide, name, save in zip(
        ["1:3,,", "1:3,,", "1:3,,", "1:3,,", "1:3,,"],
        ["permx", "permy", "permz", "dx", "trany"],
        [
            "box_yz_permx_default",
            "box_yz_permy_default",
            "box_yz_permz_default",
            "box_yz_dx_sum",
            "box_yz_trany_sum",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")
    for slide, name, save in zip(
        [",1:3,", ",1:3,", ",1:3,", ",1:3,", ",1:3,"],
        ["permx", "permy", "permz", "dy", "tranx"],
        [
            "box_xz_permx_default",
            "box_xz_permy_default",
            "box_xz_permz_default",
            "box_xz_dy_sum",
            "box_xz_tranx_sum",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")
    for slide, name, save in zip(
        [",,1:3", ",,1:3", ",,1:3", ",,1:3", ",,1:3"],
        ["permx", "permy", "permz", "dz", "trany"],
        [
            "box_xy_permx_default",
            "box_xy_permy_default",
            "box_xy_permz_default",
            "box_xy_dz_sum",
            "box_xy_trany_sum",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_how_all_operators_all_mapping_directions(tmp_path):
    for slide, name, how, save in zip(
        ["1:3,,", "1:3,,", "1:3,,", "1:3,,", "1:3,,", "1:3,,"],
        ["index_i", "index_i", "poro", "poro", "porv", "permx"],
        ["first", "last", "min", "max", "sum", "arithmetic"],
        [
            "box_yz_first",
            "box_yz_last",
            "box_yz_min",
            "box_yz_max",
            "box_yz_sum",
            "box_yz_arithmetic",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")
    for slide, name, how, save in zip(
        [",1:3,", ",1:3,", ",1:3,", ",1:3,", ",1:3,", ",1:3,"],
        ["index_j", "index_j", "poro", "poro", "porv", "permy"],
        ["first", "last", "min", "max", "sum", "arithmetic"],
        [
            "box_xz_first",
            "box_xz_last",
            "box_xz_min",
            "box_xz_max",
            "box_xz_sum",
            "box_xz_arithmetic",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")
    for slide, name, how, save in zip(
        [",,1:3", ",,1:3", ",,1:3", ",,1:3", ",,1:3", ",,1:3"],
        ["index_k", "index_k", "poro", "poro", "porv", "permz"],
        ["first", "last", "min", "max", "sum", "arithmetic"],
        [
            "box_xy_first",
            "box_xy_last",
            "box_xy_min",
            "box_xy_max",
            "box_xy_sum",
            "box_xy_arithmetic",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_harmonic_all_directions(tmp_path):
    for slide, name, save in zip(
        ["1:3,,", ",1:3,", ",,1:3"],
        ["permx", "permy", "permz"],
        [
            "box_harmonic_x_direction",
            "box_harmonic_y_direction",
            "box_harmonic_z_direction",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                "harmonic",
                "-log",
                "1",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_wells_and_faults_global_modes(tmp_path):
    for name, slide, how, globalflag, save in zip(
        ["wells", "wells", "wells", "faults", "faults", "faults"],
        ["1:3,,", ",1:3,", ",,1:3", "1:3,,", ",1:3,", ",,1:3"],
        ["min", "max", "min", "min", "max", "min"],
        ["0", "0", "1", "0", "0", "1"],
        [
            "box_wells_yz_local",
            "box_wells_xz_local",
            "box_wells_xy_global",
            "box_faults_yz_local",
            "box_faults_xz_local",
            "box_faults_xy_global",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-global",
                globalflag,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_dual_xy_mapping_branches(tmp_path):
    for name, how, save in zip(
        ["poro", "poro", "poro", "permz", "index_k"],
        ["mean", "pvmean", "sum", "harmonic", "max"],
        [
            "box_dual_mean",
            "box_dual_pvmean",
            "box_dual_sum",
            "box_dual_harmonic",
            "box_dual_index",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                ",,1:3",
                "-how",
                how,
                "-dual",
                "1",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_dual_xy_default_variable_branches(tmp_path):
    for name, save in zip(
        [
            "porv",
            "dz",
            "tranx",
            "trany",
            "permx",
            "permy",
            "permz",
            "grid",
            "index_i",
            "index_j",
            "index_k",
        ],
        [
            "box_dual_porv",
            "box_dual_dz",
            "box_dual_tranx",
            "box_dual_trany",
            "box_dual_permx",
            "box_dual_permy",
            "box_dual_permz",
            "box_dual_grid",
            "box_dual_index_i",
            "box_dual_index_j",
            "box_dual_index_k",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                ",,1:3",
                "-dual",
                "1",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_mapping_caprock_break_branches(tmp_path):
    for slide, name, save in zip(
        ["1:3,,", ",1:3,", ",,1:3"],
        ["limipres", "overpres", "objepres"],
        ["box_caprock_yz", "box_caprock_xz", "box_caprock_xy"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-stress",
                "0.2",
                "-z",
                "0",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_mapping_mass_branches_all_planes(tmp_path):
    for slide, name, save in zip(
        ["1:3,,", ",1:1,", ",,1:3"],
        ["co2m", "h2om", "gasm"],
        ["box_mass_yz", "box_mass_xz", "box_mass_xy"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-s",
                slide,
                "-a",
                "1e-6",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_rotation_translation_on_all_planes(tmp_path):
    for slide, rotate, translate, save in zip(
        ["2,,", ",2,", ",,2"],
        ["15", "30", "60"],
        ["[5,10]", "[-10,5]", "[20,-5]"],
        ["box_rotate_yz", "box_rotate_xz", "box_rotate_xy"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                "poro",
                "-s",
                slide,
                "-rotate",
                rotate,
                "-translate",
                translate,
                "-grid",
                "black,1e-3",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_slides_coordinates_all_planes(tmp_path):
    for slide, name, save in zip(
        ["2,,", ",2,", ",,2"],
        ["permx", "permy", "permz"],
        ["box_yz", "box_xz", "box_xy"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-log",
                "1",
                "-grid",
                "black,1e-3",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_y_direction_line_and_points(tmp_path):
    for slide, name, save in zip(
        ["2,:,2", ":,2,2", "2,2,:"],
        ["permy", "permx", "permz"],
        ["box_line_y", "box_line_x", "box_line_z"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-xformat",
                ".0f",
                "-yformat",
                ".2e",
                "-xlnum",
                "3",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")
    for slide, save in zip(
        ["1,1,1", "2,2,2", "3,3,3"],
        ["box_point_111", "box_point_222", "box_point_333"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                "poro",
                "-s",
                slide,
                "-xlabel",
                "Time",
                "-ylabel",
                "Porosity",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_projection_all_directions(tmp_path):
    for slide, name, how, save in zip(
        ["1:3,,", ",1:3,", ",,1:3"],
        ["permx", "permy", "permz"],
        ["harmonic", "harmonic", "harmonic"],
        ["box_harm_i", "box_harm_j", "box_harm_k"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-log",
                "1",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")
    for slide, name, how, save in zip(
        ["1:3,,", ",1:3,", ",,1:3"],
        ["permx", "poro", "porv"],
        ["arithmetic", "pvmean", "sum"],
        ["box_arithmetic_i", "box_pvmean_j", "box_sum_k"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_index_variables_and_projection(tmp_path):
    for name, slide, how, save in zip(
        ["index_i", "index_j", "index_k"],
        ["1:3,,", ",1:3,", ",,1:3"],
        ["max", "min", "max"],
        ["box_index_i", "box_index_j", "box_index_k"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-cformat",
                ".0f",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_filter_operators(tmp_path):
    for filt, save in zip(
        [
            "index_i < 3",
            "index_j <= 2",
            "index_k > 1",
            "index_i >= 2",
            "index_j != 1",
            "index_k == 2",
        ],
        [
            "box_filter_lt",
            "box_filter_le",
            "box_filter_gt",
            "box_filter_ge",
            "box_filter_ne",
            "box_filter_eq",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                "poro",
                "-s",
                ",2,",
                "-filter",
                filt,
                "-grid",
                "black,1e-3",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_formula_operators(tmp_path):
    for name, save in zip(
        [
            "index_i < 3",
            "index_j <= 2",
            "index_k > 1",
            "index_i >= 2",
            "index_j != 1",
            "index_k == 2",
        ],
        [
            "box_oper_lt",
            "box_oper_le",
            "box_oper_gt",
            "box_oper_ge",
            "box_oper_ne",
            "box_oper_eq",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                ",2,",
                "-cformat",
                ".0f",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_real_perms_subfigs_and_histograms(tmp_path):
    main(
        [
            "-i",
            str(boxpth),
            "-v",
            "permx,permy,permz",
            "-s",
            ",2,",
            "-log",
            "1,1,1",
            "-subfigs",
            "1,3",
            "-loc",
            "empty,empty,empty",
            "-d",
            "12,4",
            "-c",
            "viridis,plasma,cubehelix",
            "-o",
            str(tmp_path),
            "-save",
            "box_real_perms",
        ]
    )
    assert_png_ok(tmp_path / "box_real_perms.png")
    main(
        [
            "-i",
            str(boxpth),
            "-v",
            "permx,permy,permz",
            "-histogram",
            "10,lognorm 10,lognorm 10,lognorm",
            "-c",
            "#7274b3,#cddb6e,#db6e8f",
            "-subfigs",
            "1,3",
            "-d",
            "12,4",
            "-axgrid",
            "0",
            "-o",
            str(tmp_path),
            "-save",
            "box_perm_histograms",
        ]
    )
    assert_png_ok(tmp_path / "box_perm_histograms.png")


def test_3dbox_hysteresis_saturation_tables(tmp_path):
    for name, save in zip(
        ["krwh", "krgh", "krowh", "krogh", "pcowh", "pcogh", "pcwgh"],
        [
            "box_krwh",
            "box_krgh",
            "box_krowh",
            "box_krogh",
            "box_pcowh",
            "box_pcogh",
            "box_pcwgh",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-c",
                "k",
                "-lw",
                "2",
                "-axgrid",
                "1",
                "-xformat",
                ".2f",
                "-yformat",
                ".2e",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_saturation_tables_with_satnum_suffix(tmp_path):
    for name, save in zip(
        ["krw1", "krg1", "krow1", "krog1", "pcow1", "pcog1", "pcwg1"],
        [
            "box_krw1",
            "box_krg1",
            "box_krow1",
            "box_krog1",
            "box_pcow1",
            "box_pcog1",
            "box_pcwg1",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-c",
                "b",
                "-lw",
                "1.5",
                "-axgrid",
                "0",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_grid_wells_faults_all_directions(tmp_path):
    for name, slide, how, save in zip(
        ["grid", "wells", "wells", "faults", "faults"],
        ["2,,", ",2,", ",,2", ",2,", ",,2"],
        ["", "min", "max", "min", "max"],
        [
            "box_grid_i",
            "box_wells_j_min",
            "box_wells_k_max",
            "box_faults_j_min",
            "box_faults_k_max",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-global",
                "0",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_csv_y_direction_and_projection_outputs(tmp_path):
    for name, slide, how, save in zip(
        ["permy", "poro", "index_j"],
        [",2,", "2,:,2", ",1:3,"],
        ["", "", "max"],
        ["box_csv_permy_map", "box_csv_poro_line_y", "box_csv_index_j_projection"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-m",
                "csv",
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_file_ok(tmp_path / f"{save}.csv")


def test_3dbox_vtk_real_perms_indices_and_discrete(tmp_path):
    main(
        [
            "-i",
            str(boxpth),
            "-v",
            "permx,permy,permz,index_i,index_j,index_k,satnum,fipnum",
            "-m",
            "vtk",
            "-vtkformat",
            "Float32",
            "-vtknames",
            "permx,permy,permz,index_i,index_j,index_k,satnum,fipnum",
            "-p",
            "flow",
            "-o",
            str(tmp_path),
            "-save",
            "box_vtk",
        ]
    )
    assert_file_ok(tmp_path / "box_vtk.pvd")


def test_3dbox_distance_y_direction_sensor_and_border(tmp_path):
    for distance, slide, save in zip(
        ["max,sensor", "min,sensor", "max,border", "min,border"],
        ["2,2,2", "1,3,2", ",2,", ",2,"],
        [
            "box_distance_sensor_max",
            "box_distance_sensor_min",
            "box_distance_border_max",
            "box_distance_border_min",
        ],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                "index_j == 2",
                "-distance",
                distance,
                "-s",
                slide,
                "-xunits",
                "m",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_local_default_variables(tmp_path, monkeypatch):
    monkeypatch.chdir(testpth / "data" / "3dbox")
    main(
        [
            "-i",
            "3DBOX",
            "-o",
            str(tmp_path),
            "-s",
            ",2,",
        ]
    )
    for name in ["porv", "poro", "permx", "permz", "satnum", "fipnum"]:
        assert_png_ok(tmp_path / f"3dbox_{name}_i,2,k_t2.png")


def test_3dbox_slides_in_all_directions(tmp_path):
    for slide, name, logs, save in zip(
        ["2,,", ",2,", ",,2"],
        ["permx", "permy", "permz"],
        ["1", "1", "1"],
        ["box_slide_i", "box_slide_j", "box_slide_k"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-log",
                logs,
                "-grid",
                "black,1e-3",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_projection_ranges_in_all_directions(tmp_path):
    for slide, name, how, save in zip(
        ["1:3,,", ",1:3,", ",,1:3"],
        ["permx", "permy", "permz"],
        ["harmonic", "harmonic", "harmonic"],
        ["box_harm_i", "box_harm_j", "box_harm_k"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-log",
                "1",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_projection_arithmetic_and_pvmean(tmp_path):
    for slide, name, how, save in zip(
        ["1:3,,", ",1:3,", ",,1:3"],
        ["permx", "poro", "porv"],
        ["arithmetic", "pvmean", "sum"],
        ["box_arithmetic_i", "box_pvmean_j", "box_sum_k"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_line_extractions_in_all_directions(tmp_path):
    for slide, name, save in zip(
        [":,2,2", "2,:,2", "2,2,:"],
        ["poro", "permy", "permz"],
        ["box_line_i", "box_line_j", "box_line_k"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-xformat",
                ".0f",
                "-yformat",
                ".2e",
                "-xlnum",
                "3",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_point_extractions(tmp_path):
    for slide, name, save in zip(
        ["1,1,1", "2,2,2", "3,3,3"],
        ["poro", "permx", "permz"],
        ["box_point_111", "box_point_222", "box_point_333"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-xlabel",
                "time",
                "-ylabel",
                name,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_real_permeability_subfigures(tmp_path):
    main(
        [
            "-i",
            str(boxpth),
            "-v",
            "permx,permy,permz",
            "-s",
            ",2,",
            "-log",
            "1,1,1",
            "-subfigs",
            "1,3",
            "-loc",
            "empty,empty,empty",
            "-d",
            "12,4",
            "-c",
            "viridis,plasma,cubehelix",
            "-o",
            str(tmp_path),
            "-save",
            "box_real_perms",
        ]
    )
    assert_png_ok(tmp_path / "box_real_perms.png")


def test_3dbox_index_variables_and_filters(tmp_path):
    for name, filt, save in zip(
        ["index_i", "index_j", "index_k"],
        ["index_i == 2", "index_j == 2", "index_k == 2"],
        ["box_index_i", "box_index_j", "box_index_k"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-filter",
                filt,
                "-s",
                ",2,",
                "-cformat",
                ".0f",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_discrete_projection_min_max(tmp_path):
    for name, how, slide, save in zip(
        ["index_j", "index_j", "satnum", "fipnum"],
        ["min", "max", "first", "last"],
        [",1:3,", ",1:3,", ",1:3,", ",1:3,"],
        ["box_index_j_min", "box_index_j_max", "box_satnum_first", "box_fipnum_last"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-cformat",
                ".0f",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_blackoil_relperm_tables(tmp_path):
    for name, colors, save in zip(
        ["krw", "krg", "krow", "krog"],
        ["b", "g", "r", "k"],
        ["box_krw", "box_krg", "box_krow", "box_krog"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-c",
                colors,
                "-lw",
                "2",
                "-axgrid",
                "1",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_blackoil_capillary_pressure_tables(tmp_path):
    for name, save in zip(
        ["pcow", "pcog", "pcwg"],
        ["box_pcow", "box_pcog", "box_pcwg"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                name,
                "-c",
                "k",
                "-xformat",
                ".2f",
                "-yformat",
                ".2e",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_histograms_for_real_perms(tmp_path):
    main(
        [
            "-i",
            str(boxpth),
            "-v",
            "permx,permy,permz",
            "-histogram",
            "10,lognorm 10,lognorm 10,lognorm",
            "-c",
            "#7274b3,#cddb6e,#db6e8f",
            "-subfigs",
            "1,3",
            "-d",
            "12,4",
            "-axgrid",
            "0",
            "-o",
            str(tmp_path),
            "-save",
            "box_perm_histograms",
        ]
    )
    assert_png_ok(tmp_path / "box_perm_histograms.png")


def test_3dbox_csv_for_y_direction_outputs(tmp_path):
    for name, slide, save in zip(
        ["permy", "poro", "index_j"],
        [",2,", "2,:,2", ",1:3,"],
        ["box_csv_permy_map", "box_csv_poro_line", "box_csv_index_j_projection"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-m",
                "csv",
                "-v",
                name,
                "-s",
                slide,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_file_ok(tmp_path / f"{save}.csv")


def test_3dbox_vtk_real_perms_and_indices(tmp_path):
    main(
        [
            "-i",
            str(boxpth),
            "-v",
            "permx,permy,permz,index_i,index_j,index_k",
            "-m",
            "vtk",
            "-vtkformat",
            "Float32",
            "-vtknames",
            "permx_vtk,permy_vtk,permz_vtk,index_i_vtk,index_j_vtk,index_k_vtk",
            "-p",
            "flow",
            "-o",
            str(tmp_path),
            "-save",
            "box_vtk",
        ]
    )
    assert_file_ok(tmp_path / "box_vtk.pvd")


def test_3dbox_mask_filter_y_direction(tmp_path):
    for filt, mask, save in zip(
        ["index_j == 1", "index_j == 2", "index_j == 3"],
        ["index_i", "index_j", "index_k"],
        ["box_mask_j1", "box_mask_j2", "box_mask_j3"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                "poro",
                "-s",
                ",2,",
                "-filter",
                filt,
                "-mask",
                mask,
                "-maskthr",
                "1e-9",
                "-ncolor",
                "0.8",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_3dbox_geometry_controls_on_y_slice(tmp_path):
    for rotate, translate, xlim, ylim, save in zip(
        ["0", "30", "90"],
        ["[0,0]", "[10,20]", "[-10,5]"],
        ["", "[-100,200]", ""],
        ["", "[-100,200]", ""],
        ["box_geom_y0", "box_geom_y30", "box_geom_y90"],
    ):
        main(
            [
                "-i",
                str(boxpth),
                "-v",
                "poro",
                "-s",
                ",2,",
                "-rotate",
                rotate,
                "-translate",
                translate,
                "-x",
                xlim,
                "-y",
                ylim,
                "-grid",
                "black,1e-3",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_axes_scaling_and_units(tmp_path):
    for scale, xunits, yunits, save in zip(
        ["1", "0"],
        ["m", "km"],
        ["m", "km"],
        ["units1", "units2"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "poro",
                "-z",
                scale,
                "-xunits",
                xunits,
                "-yunits",
                yunits,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_bounds_ticks_and_formats(tmp_path):
    for bounds, fmt, ticks, save in zip(
        ["[0,1]", "[-1,10]", "[0,100]"],
        [".1f", ".2e", ".0f"],
        ["[0,0.5,1]", "[0,5,10]", "[0,50,100]"],
        ["fmt1", "fmt2", "fmt3"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "poro",
                "-b",
                bounds,
                "-cformat",
                fmt,
                "-cticks",
                ticks,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_remove_facecolor_and_grid(tmp_path):
    for remove, facecolor, grid, save in zip(
        ["1,1,1,1", "0,1,0,1"],
        ["k", "w"],
        ["black,1e-3", ""],
        ["clean1", "clean2"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "poro",
                "-remove",
                remove,
                "-facecolor",
                facecolor,
                "-grid",
                grid,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_rotation_translation_global(tmp_path):
    for rotate, translate, globalflag, save in zip(
        ["0", "45", "90"],
        ["[0,0]", "[100,50]", "[-50,20]"],
        ["0", "1", "0"],
        ["geom1", "geom2", "geom3"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "poro",
                "-rotate",
                rotate,
                "-translate",
                translate,
                "-global",
                globalflag,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_line_styles_and_widths(tmp_path):
    for linestyle, lw, colors, save in zip(
        ["solid", "dotted", "solid,dotted"],
        ["1", "2", "1,2"],
        ["b", "r", "b,r"],
        ["line1", "line2", "line3"],
    ):
        main(
            [
                "-i",
                f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
                "-v",
                "fgip",
                "-e",
                linestyle,
                "-lw",
                lw,
                "-c",
                colors,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_colorbar_and_logscale(tmp_path):
    for log, clog, save in zip(
        ["0", "1"],
        ["[1,2,5]", "[1,10,100]"],
        ["clog1", "clog2"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "pressure",
                "-log",
                log,
                "-clogthks",
                clog,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_thresholds_and_limits(tmp_path):
    for vmin, vmax, save in zip(
        ["0.1", ""],
        ["0.9", "10"],
        ["thr1", "thr2"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "poro",
                "-vmin",
                vmin,
                "-vmax",
                vmax,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_titles_labels_and_axes(tmp_path):
    for title, ylabel, xlabel, save in zip(
        ["Title", "0"],
        ["Y axis", ""],
        ["X axis", ""],
        ["label1", "label2"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "poro",
                "-t",
                title,
                "-ylabel",
                ylabel,
                "-xlabel",
                xlabel,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_restart_and_adjust(tmp_path):
    for restart, adjust, save in zip(
        ["0", "1", "0:2"],
        ["1", "1e-6", "1e-3"],
        ["rst1", "rst2", "rst3"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "co2m",
                "-r",
                restart,
                "-a",
                adjust,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        if restart == "0:2":
            assert_png_ok(tmp_path / f"{save}0.png")
            assert_png_ok(tmp_path / f"{save}1.png")
            assert_png_ok(tmp_path / f"{save}2.png")
        else:
            assert_png_ok(tmp_path / f"{save}.png")


def test_dual_printv_and_misc(tmp_path):
    for dual, printv, save in zip(
        ["0", "1"],
        ["0", "1"],
        ["misc1", "misc2"],
    ):
        if printv != "1":
            main(
                [
                    "-i",
                    str(mainpth / "examples" / "SPE11B"),
                    "-v",
                    "poro",
                    "-dual",
                    dual,
                    "-printv",
                    printv,
                    "-o",
                    str(tmp_path),
                    "-save",
                    save,
                ]
            )
            assert_png_ok(tmp_path / f"{save}.png")
        else:
            with pytest.raises(SystemExit) as excinfo:
                main(
                    [
                        "-i",
                        str(mainpth / "examples" / "SPE11B"),
                        "-v",
                        "poro",
                        "-dual",
                        dual,
                        "-printv",
                        printv,
                        "-o",
                        str(tmp_path),
                        "-save",
                        save,
                    ]
                )
            assert excinfo.value.code == 0


def test_gif_interval_loop(tmp_path):
    for interval, loop, save in zip(
        ["200", "1000"],
        ["0", "1"],
        ["gif1", "gif2"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "pressure",
                "-m",
                "gif",
                "-interval",
                interval,
                "-loop",
                loop,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_file_ok(tmp_path / f"{save}.gif")


def test_slides_logs_and_planes(tmp_path):
    for slide, name, logs, save in zip(
        ["4,,", ",1,", ",,20"],
        ["poro", "porv", "permx"],
        ["0", "0", "1"],
        ["slide_i", "slide_j", "slide_k"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-o",
                str(tmp_path),
                "-v",
                name,
                "-s",
                slide,
                "-log",
                logs,
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_projection_how_variants(tmp_path):
    for how, name, slide, save in zip(
        ["sum", "mean", "pvmean", "first", "last"],
        ["porv", "poro", "poro", "satnum", "fipnum"],
        [",,1:10", ",,1:10", ",,1:10", ",,1:10", ",,1:10"],
        ["how_sum", "how_mean", "how_pvmean", "how_first", "how_last"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_projection_permeability_averages(tmp_path):
    for how, name, slide, save in zip(
        ["harmonic", "arithmetic"],
        ["permz", "permx"],
        [",,1:10", ",,1:10"],
        ["how_harmonic", "how_arithmetic"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_summary_time_units_formats_and_grid(tmp_path):
    for tunits, axgrid, xformat, yformat, save in zip(
        ["s", "d", "y"],
        ["0", "1", "1"],
        [".1f", ".2e", ".0f"],
        [".1f", ".2e", ".0f"],
        ["time_s", "time_d", "time_y"],
    ):
        main(
            [
                "-i",
                f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
                "-v",
                "fgip,fgip * 2",
                "-tunits",
                tunits,
                "-axgrid",
                axgrid,
                "-xformat",
                xformat,
                "-yformat",
                yformat,
                "-labels",
                "Reference  Twice",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_subfigs_suptitle_cbsfax_and_loc(tmp_path):
    for subfigs, loc, suptitle, cbsfax, save in zip(
        ["2,2", "1,3"],
        ["empty,center,empty,best", "best,best,best"],
        ["0", "Custom title"],
        ["empty", "0.40,0.01,0.2,0.02"],
        ["subfigs_no_title", "subfigs_title"],
    ):
        main(
            [
                "-i",
                f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
                "-v",
                "poro,permx,permz",
                "-subfigs",
                subfigs,
                "-loc",
                loc,
                "-suptitle",
                suptitle,
                "-cbsfax",
                cbsfax,
                "-delax",
                "1",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_dimensions_dpi_labels_and_ticks(tmp_path):
    for dimensions, dpi, xlnum, ylnum, cnum, save in zip(
        ["5,4", "8,3"],
        ["80", "120"],
        ["3", "7"],
        ["3", "7"],
        ["3", "6"],
        ["figshape1", "figshape2"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "poro",
                "-d",
                dimensions,
                "-dpi",
                dpi,
                "-xlnum",
                xlnum,
                "-ylnum",
                ylnum,
                "-cnum",
                cnum,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_masks_filters_and_backgrounds(tmp_path):
    for name, mask, maskthr, filt, ncolor, save in zip(
        ["sgas", "sgas"],
        ["satnum", "fipnum"],
        ["1e-3", "1e-2"],
        ["fipnum >= 2 & satnum != 4", "satnum == 5"],
        ["w", "0.5"],
        ["mask_filter1", "mask_filter2"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-mask",
                mask,
                "-maskthr",
                maskthr,
                "-filter",
                filt,
                "-ncolor",
                ncolor,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_multiinput_filter_and_colorbar_axis(tmp_path):
    main(
        [
            "-i",
            f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
            "-v",
            "fipnum",
            "-filter",
            ",fipnum >= 2 & fipnum != 4,satnum == 5",
            "-cbsfax",
            "0.15,0.97,0.7,0.02",
            "-t",
            "No filter  fipnum >= 2 \\& fipnum != 4  satnum == 5",
            "-suptitle",
            "0",
            "-subfigs",
            "3,1",
            "-delax",
            "1",
            "-cformat",
            ".0f",
            "-d",
            "7,4",
            "-o",
            str(tmp_path),
            "-save",
            "multi_filter",
        ]
    )
    assert_png_ok(tmp_path / "multi_filter.png")


def test_histograms_multiple_distributions(tmp_path):
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "poro,permx",
            "-histogram",
            "20,norm 20,lognorm",
            "-c",
            "#7274b3,#cddb6e",
            "-ylabel",
            "Histogram",
            "-axgrid",
            "0",
            "-subfigs",
            "1,2",
            "-d",
            "15,5",
            "-loc",
            "upper center",
            "-y",
            "[0,10000] [0,23000]",
            "-o",
            str(tmp_path),
            "-save",
            "hist_two_vars",
        ]
    )
    assert_png_ok(tmp_path / "hist_two_vars.png")
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "depth,dz,tranz * 10",
            "-histogram",
            "50,norm 20,lognorm 100",
            "-c",
            "#7274b3,#cddb6e,#db6e8f",
            "-ylabel",
            "Histogram",
            "-axgrid",
            "0",
            "-subfigs",
            "1,3",
            "-d",
            "15,5",
            "-loc",
            "best",
            "-o",
            str(tmp_path),
            "-save",
            "hist_three_vars",
        ]
    )
    assert_png_ok(tmp_path / "hist_three_vars.png")


def test_distance_sensor_and_border(tmp_path):
    for distance, slide, xunits, save in zip(
        ["max,sensor", "min,border"],
        ["42,1,29", ",1,"],
        ["km", "m"],
        ["distance_sensor", "distance_border"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "sgas > 1e-2",
                "-distance",
                distance,
                "-s",
                slide,
                "-xlnum",
                "11",
                "-xunits",
                xunits,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_difference_dynamic_and_static(tmp_path):
    for name, slide, restart, save in zip(
        ["rsw", "pressure - 0pressure"],
        [",1,", "1:83,, 1:10,,"],
        ["-1", "0"],
        ["difference_dynamic", "difference_static"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-diff",
                str(mainpth / "examples" / "SPE11B"),
                "-s",
                slide,
                "-r",
                restart,
                "-z",
                "0",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_special_variables_and_stress(tmp_path):
    for name, stress, save in zip(
        ["limipres", "overpres", "objepres"],
        ["0.134", "0.2", "0.1"],
        ["limipres_stress", "overpres_stress", "objepres_stress"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-s",
                ",,1:58",
                "-v",
                name,
                "-stress",
                stress,
                "-z",
                "0",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_special_summary_variables(tmp_path):
    for name, save in zip(
        ["krw3", "krg2", "pcwg5"],
        ["krw3_special", "krg2_special", "pcwg5_special"],
    ):
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
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_ensemble_modes_and_bands(tmp_path):
    for ensemble, bandprop, save in zip(
        ["1", "2", "3"],
        ["r,0.1", "", "r,0.1,b,0.2"],
        ["ensemble1", "ensemble2", "ensemble3"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "tcpu",
                "-ensemble",
                ensemble,
                "-bandprop",
                bandprop,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_mode_csv_outputs(tmp_path):
    for name, slide, save in zip(
        ["objepres", "pressure", "poro"],
        [",,1:58", ",,:", ",1,"],
        ["objepres_csv", "pressure_csv", "poro_csv"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-m",
                "csv",
                "-v",
                name,
                "-s",
                slide,
                "-z",
                "0",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_file_ok(tmp_path / f"{save}.csv")


def test_mode_vtk_formats_and_names(tmp_path):
    for fmt, names, save in zip(
        [
            "Float64",
            "Float32",
            "Float16",
            "Int64",
            "UInt64",
            "Int32",
            "UInt32",
            "Int16",
            "UInt16",
            "Int8",
            "UInt8",
        ],
        [
            "satnum_vtk64",
            "satnum_vtk32",
            "satnum_vtk16",
            "satnum_int64",
            "satnum_uint64",
            "satnum_int32",
            "satnum_uint32",
            "satnum_int16",
            "satnum_uint16",
            "satnum_int8",
            "satnum_uint8",
        ],
        [
            "vtk64",
            "vtk32",
            "vtk16",
            "vtkint64",
            "vtkuint64",
            "vtkint32",
            "vtkuint32",
            "vtkint16",
            "vtkuint16",
            "vtkint8",
            "vtkuint8",
        ],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "satnum",
                "-m",
                "vtk",
                "-vtkformat",
                fmt,
                "-vtknames",
                names,
                "-p",
                "flow",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_file_ok(tmp_path / f"{save}.pvd")


def test_mode_gif_mask_restart_and_empty_time(tmp_path):
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "xco2l",
            "-m",
            "gif",
            "-mask",
            "satnum",
            "-r",
            "0,1,2",
            "-interval",
            "200",
            "-loop",
            "1",
            "-d",
            "6,4",
            "-tunits",
            "empty",
            "-o",
            str(tmp_path),
            "-save",
            "gif_mask",
        ]
    )
    assert_file_ok(tmp_path / "gif_mask.gif")


def test_map_colormap_customization(tmp_path):
    for colors, bounds, clabel, save in zip(
        ["cet_CET_I2", "cubehelix", "viridis"],
        ["", "[0,1]", ""],
        ["gas saturation [-]", "porosity [-]", ""],
        ["color_cet", "color_cubehelix", "color_viridis"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "sgas",
                "-r",
                "1",
                "-c",
                colors,
                "-b",
                bounds,
                "-clabel",
                clabel,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_point_and_line_extractions(tmp_path):
    for slide, name, ylabel, save in zip(
        ["1,1,1", "41,1,29", "83,1,58"],
        ["pressure - 0pressure", "pressure - 0pressure", "pressure - 0pressure"],
        ["Left corner", "Middle", "Right corner"],
        ["point_left", "point_middle", "point_right"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-s",
                slide,
                "-ylabel",
                ylabel,
                "-xformat",
                ".0f",
                "-yformat",
                ".0f",
                "-xlnum",
                "11",
                "-tunits",
                "y",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_grid_and_wells_variables(tmp_path):
    for name, how, save in zip(
        ["grid", "wells"],
        ["", "min"],
        ["grid_variable", "wells_variable"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-s",
                ",1,",
                "-how",
                how,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_help_exits_cleanly():
    with pytest.raises(SystemExit) as excinfo:
        main(["-h"])
    assert excinfo.value.code == 0


def test_default_static_variables_from_local_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "SPE11B.INIT").write_bytes(
        (mainpth / "examples" / "SPE11B.INIT").read_bytes()
    )
    (tmp_path / "SPE11B.EGRID").write_bytes(
        (mainpth / "examples" / "SPE11B.EGRID").read_bytes()
    )
    main(
        [
            "-o",
            str(tmp_path),
        ]
    )
    for name in ["porv", "poro", "permx", "permz", "satnum", "fipnum"]:
        assert_png_ok(tmp_path / f"spe11b_{name}_i,1,k_t0.png")


def test_restart_lists_and_steps(tmp_path):
    for restart, save, files in zip(
        ["0,2", "0:4:2"],
        ["restart_list", "restart_step"],
        [
            ["restart_list0.png", "restart_list2.png"],
            ["restart_step0.png", "restart_step2.png", "restart_step4.png"],
        ],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "sgas",
                "-r",
                restart,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        for file in files:
            assert_png_ok(tmp_path / file)


def test_summary_limits_log_legend_and_labels(tmp_path):
    for xlim, ylim, ylog, loc, save in zip(
        ["[0,2e9]", "[0,1e10]"],
        ["[1e-6,1e12]", ""],
        ["1", "0"],
        ["upper left", "empty"],
        ["summary_limits_log", "summary_no_legend"],
    ):
        main(
            [
                "-i",
                f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
                "-v",
                "fgip,fgip * 2",
                "-x",
                xlim,
                "-y",
                ylim,
                "-ylog",
                ylog,
                "-loc",
                loc,
                "-labels",
                "Base  Double",
                "-xlabel",
                "Time",
                "-ylabel",
                "Gas in place",
                "-tunits",
                "d",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_map_limits_title_remove_and_colorbar_positions(tmp_path):
    for xlim, ylim, remove, cbsfax, save in zip(
        ["[0,8400]", ""],
        ["[-1200,0]", ""],
        ["0,0,0,0", "0,0,1,0"],
        ["0.40,0.01,0.2,0.02", "empty"],
        ["map_limits_colorbar", "map_no_colorbar"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "poro",
                "-x",
                xlim,
                "-y",
                ylim,
                "-remove",
                remove,
                "-cbsfax",
                cbsfax,
                "-t",
                "Map limits",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_color_ticks_with_text_labels(tmp_path):
    for name, ticks, bounds, save in zip(
        ["sgas", "fipnum"],
        ["[0, middle, 0.9]", "[1, two, three, four, five]"],
        ["[0,1]", "[1,5]"],
        ["text_ticks_sgas", "text_ticks_fipnum"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-r",
                "1",
                "-b",
                bounds,
                "-cticks",
                ticks,
                "-cnum",
                "5",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_formula_variables_and_thresholds(tmp_path):
    for name, vmin, vmax, save in zip(
        ["sgas > 1e-2", "pressure - 0pressure", "poro * porv"],
        ["", "-10", ""],
        ["", "100", ""],
        ["formula_bool", "formula_pressure", "formula_static"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-vmin",
                vmin,
                "-vmax",
                vmax,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_projection_min_max_for_discrete_variables(tmp_path):
    for how, name, slide, save in zip(
        ["min", "max"],
        ["satnum", "fipnum"],
        [",,1:58", ",,1:58"],
        ["projection_min", "projection_max"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-s",
                slide,
                "-how",
                how,
                "-z",
                "0",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_mass_and_compositional_variables(tmp_path):
    for name, adjust, save in zip(
        ["co2m", "h2om", "xco2l", "xh2ov"],
        ["1e-6", "1e-6", "1", "1"],
        ["mass_co2", "mass_h2o", "comp_xco2l", "comp_xh2ov"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-s",
                ",,1:58",
                "-z",
                "0",
                "-a",
                adjust,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_summary_subfigs_with_mixed_variables(tmp_path):
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
            "-suptitle",
            "Summary subfigures",
            "-d",
            "6,5",
            "-ylabel",
            "gas in place  mass in place  halfmass region 3",
            "-o",
            str(tmp_path),
            "-save",
            "summary_mixed_subfigs",
        ]
    )
    assert_png_ok(tmp_path / "summary_mixed_subfigs.png")


def test_summary_sensor_and_layer_extractions(tmp_path):
    for slide, labels, save in zip(
        ["1,1,1 41,1,29 83,1,58", "1,1,: :,1,1 :,1,29"],
        ["Left corner  Middle  Right corner", "Left column  Top row  Middle row"],
        ["summary_sensors", "summary_layers"],
    ):
        main(
            [
                "-i",
                f"{mainpth}/examples/SPE11B {mainpth}/examples/SPE11B {mainpth}/examples/SPE11B",
                "-v",
                "pressure - 0pressure",
                "-s",
                slide,
                "-ylabel",
                "Pressure increase [bar]",
                "-labels",
                labels,
                "-xformat",
                ".0f",
                "-yformat",
                ".0f",
                "-xlnum",
                "11",
                "-tunits",
                "y",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_csv_outputs_have_content_and_headers(tmp_path):
    for name, slide, save in zip(
        ["objepres", "pressure", "poro"],
        [",,1:58", ",,:", ",1,"],
        ["csv_objepres_check", "csv_pressure_check", "csv_poro_check"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-m",
                "csv",
                "-v",
                name,
                "-s",
                slide,
                "-z",
                "0",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_file_ok(tmp_path / f"{save}.csv")
        assert len((tmp_path / f"{save}.csv").read_text().splitlines()) > 1


def test_vtk_multiple_variables_and_names(tmp_path):
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "poro,permx,permz",
            "-m",
            "vtk",
            "-vtkformat",
            "Float32",
            "-vtknames",
            "poro_vtk,permx_vtk,permz_vtk",
            "-p",
            "flow",
            "-o",
            str(tmp_path),
            "-save",
            "vtk_multi",
        ]
    )
    assert_file_ok(tmp_path / "vtk_multi.pvd")


def test_gif_restart_range_and_units(tmp_path):
    main(
        [
            "-i",
            str(mainpth / "examples" / "SPE11B"),
            "-v",
            "sgas",
            "-m",
            "gif",
            "-r",
            "0:2",
            "-interval",
            "300",
            "-loop",
            "0",
            "-tunits",
            "empty",
            "-xunits",
            "km",
            "-yunits",
            "km",
            "-o",
            str(tmp_path),
            "-save",
            "gif_range_units",
        ]
    )
    assert_file_ok(tmp_path / "gif_range_units0.gif")


def test_map_static_dynamic_mask_and_grid(tmp_path):
    for name, mask, grid, save in zip(
        ["sgas", "xco2l"],
        ["satnum", "fipnum"],
        ["black,5e-4", "gray,1e-3"],
        ["masked_grid_sgas", "masked_grid_xco2l"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                name,
                "-mask",
                mask,
                "-maskthr",
                "1e-3",
                "-grid",
                grid,
                "-r",
                "1",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_summary_dates_empty_and_time_units(tmp_path):
    for tunits, save in zip(
        ["h", "w"],
        ["summary_hours", "summary_weeks"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "fgip",
                "-tunits",
                tunits,
                "-xlnum",
                "4",
                "-ylnum",
                "4",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_colormap_bounds_global_and_inactive_color(tmp_path):
    for globalflag, ncolor, colors, save in zip(
        ["0", "1"],
        ["w", "0.8"],
        ["viridis", "plasma"],
        ["global_local", "global_full"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "poro",
                "-global",
                globalflag,
                "-ncolor",
                ncolor,
                "-c",
                colors,
                "-b",
                "[0,1]",
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")


def test_map_font_size_dimensions_and_dpi(tmp_path):
    for size, dimensions, dpi, save in zip(
        ["8", "16"],
        ["4,3", "9,6"],
        ["60", "100"],
        ["small_font", "large_font"],
    ):
        main(
            [
                "-i",
                str(mainpth / "examples" / "SPE11B"),
                "-v",
                "poro",
                "-f",
                size,
                "-d",
                dimensions,
                "-dpi",
                dpi,
                "-o",
                str(tmp_path),
                "-save",
                save,
            ]
        )
        assert_png_ok(tmp_path / f"{save}.png")
