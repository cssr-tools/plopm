# Run as . tests/scripts/docs_all.sh
. tests/scripts/initialize_output_folders.sh
. tests/scripts/get_pyopmnearwell.sh
. tests/scripts/get_pyopmspe11.sh
. tests/scripts/get_opm_data.sh

. tests/scripts/get_spe11b_benchmark.sh &
. tests/scripts/run_norne.sh &
wait

. tests/scripts/run_spe11b_larger_injection.sh &
. tests/scripts/run_spe11c.sh & 
. tests/scripts/run_spe10_model2.sh & 
. tests/scripts/run_ensemble.sh &
wait

. tests/scripts/docs_hello_world.sh &
. tests/scripts/docs_colormaps.sh &
. tests/scripts/docs_generic_deck.sh &
. tests/scripts/docs_rotation_translation_zoom.sh &
. tests/scripts/docs_projections_subfigures.sh &
. tests/scripts/docs_histograms.sh &
. tests/scripts/docs_caprock_integrity.sh &
. tests/scripts/docs_reading_csvs.sh &
. tests/scripts/docs_convert_to_vtk.sh &
. tests/scripts/docs_different_files_and_ensembles.sh &
. tests/scripts/docs_filters.sh &
. tests/scripts/docs_gif_mask.sh &
. tests/scripts/docs_graphical_abstract.sh &
wait
