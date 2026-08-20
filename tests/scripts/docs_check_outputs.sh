files="
test_outputs/docs_caprock_integrity/norne_atw2013_overpres_i,j,1:22_t241.png
test_outputs/docs_caprock_integrity/norne_atw2013_objepres_i,j,1:22_t241.csv
test_outputs/docs_colormaps/spe11b_disperc_i,1,k_t5.png
test_outputs/docs_projections_subfigures/norne_atw2013_poro_i,j,1:22_t241.png
test_outputs/docs_graphical_abstract/SPE11C-0000.vtu
test_outputs/docs_graphical_abstract/SPE11C-GRID.vtu
test_outputs/docs_graphical_abstract/SPE11C-0005.vtu
test_outputs/docs_graphical_abstract/norne_atw2013_permx_i,j,1_t241.png
test_outputs/docs_graphical_abstract/SPE11C.pvd
test_outputs/docs_graphical_abstract/spe11b_base_fgmip*1e-6.png
test_outputs/docs_different_files_and_ensembles/example3_formated.png
test_outputs/docs_different_files_and_ensembles/example0.png
test_outputs/docs_different_files_and_ensembles/comparison.png
test_outputs/docs_different_files_and_ensembles/spe11b_larger_inj_sgas_i,1,k_t3.png
test_outputs/docs_different_files_and_ensembles/formated.png
test_outputs/docs_histograms/norne_atw2013_permx.png
test_outputs/docs_reading_csvs/spe11b_time_series_bwpr-256,1,5.png
test_outputs/docs_reading_csvs/spe11b_spatial_map_500y_xco2l__t100.png
test_outputs/docs_reading_csvs/spe11b_spatial_map_250y_csv__t-1.png
test_outputs/docs_reading_csvs/spe11b_time_series_csv.png
test_outputs/docs_rotation_translation_zoom/norne_atw2013_permz_i,j,1_t241.png
test_outputs/docs_rotation_translation_zoom/norne_atw2013_poro_i,j,1_t241.png
test_outputs/docs_rotation_translation_zoom/norne_atw2013_permx_i,j,1_t241.png
test_outputs/docs_rotation_translation_zoom/norne_wells_global.png
test_outputs/docs_rotation_translation_zoom/norne_wells.png
test_outputs/docs_rotation_translation_zoom/norne_atw2013_faults_i,j,1:22_t241.png
test_outputs/docs_rotation_translation_zoom/norne_atw2013_satnum_i,j,1_t241.png
test_outputs/docs_rotation_translation_zoom/norne_atw2013_fipnum_i,j,1_t241.png
test_outputs/docs_rotation_translation_zoom/norne_atw2013_porv_i,j,1_t241.png
test_outputs/docs_rotation_translation_zoom/norne_atw2013_faults_i,j,1_t241.png
test_outputs/docs_convert_to_vtk/SPE11B-0000.vtu
test_outputs/docs_convert_to_vtk/SPE11B-GRID.vtu
test_outputs/docs_convert_to_vtk/SPE11B-0005.vtu
test_outputs/docs_convert_to_vtk/SPE11B.pvd
test_outputs/docs_gif_mask/xco2l.gif
test_outputs/docs_gif_mask/spe11b_base_sgas.gif
test_outputs/docs_hello_world/spe11b_satnum_i,1,k_t5.png
test_outputs/docs_hello_world/spe11b_permz_i,1,k_t5.png
test_outputs/docs_hello_world/spe11b_porv_i,1,k_t5.png
test_outputs/docs_hello_world/spe11b_poro_i,1,k_t5.png
test_outputs/docs_hello_world/spe11b_pressure-0pressure.png
test_outputs/docs_hello_world/spe11b_fgip.png
test_outputs/docs_hello_world/spe11b_permx_i,1,k_t5.png
test_outputs/docs_hello_world/spe11b_fipnum_i,1,k_t5.png
test_outputs/docs_hello_world/spe11b_sgas_i,1,k_t4.png
test_outputs/docs_filters/spe11b_fipnum_i,1,k_t5.png
test_outputs/docs_generic_deck/spe10_model2_grid_i,j,1_t0.png
test_outputs/docs_generic_deck/spe10_model2_wells_i,j,1_t0.png
test_outputs/docs_generic_deck/spe10_model2_permz_i,4,k_t0.png
test_outputs/docs_rel_perms_and_capillary_pressure/h2hysteresis_krwh.png
test_outputs/docs_rel_perms_and_capillary_pressure/h2hysteresis_krw2.png
test_outputs/docs_rel_perms_and_capillary_pressure/h2hysteresis_pcwg.png
"

missing_file="test_outputs/missing_docs_files.txt"
missing=0

rm -f "$missing_file"

printf '%s\n' "$files" | while IFS= read -r f; do
    [ -z "$f" ] && continue
    if [ ! -f "$f" ]; then
        echo "$f" >> "$missing_file"
        missing=$((missing + 1))
    fi
done

if [ "$missing" -eq 0 ]; then
    echo "All figures and files exist."
    return 0
else
    echo "$missing figure(s) or file(s) missing."
    echo "See $missing_file"
    return 1
fi
