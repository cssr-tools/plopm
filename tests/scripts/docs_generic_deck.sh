WHR="test_outputs/opm-data/spe10model2/SPE10_MODEL2"
OUT="test_outputs/docs_generic_deck"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_opm_data.sh
. tests/scripts/run_spe10_model2.sh
plopm -i $WHR -o $OUT -v permz -s ,4, -clog 1 -xu km -yu km -xnt 6 -yf .2f -t 'K$_z$ at the forth slide in the xz plane' -cl '[1e-7,1e3]'
plopm -i $WHR -o $OUT -s ,,1 -fs 3,4 -fz 8 -v grid -hide 0,0,1,0
plopm -i $WHR -o $OUT -s ,,1 -fs 3,4 -fz 8 -v wells -hide 0,0,0,1
