WHR="test_outputs/opm-data/spe10model2/SPE10_MODEL2"
OUT="test_outputs/docs_generic_deck"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_opm_data.sh
. tests/scripts/run_spe10_model2.sh
plopm -i $WHR -o $OUT -v permz -s ,4, -log 1 -xunits km -yunits km -xlnum 6 -yformat .2f -t 'K$_z$ at the forth slide in the xz plane' -b '[1e-7,1e3]'
plopm -i $WHR -o $OUT -s ,,1 -d 3,4 -f 8 -v grid -remove 0,0,1,0
plopm -i $WHR -o $OUT -s ,,1 -d 3,4 -f 8 -v wells -remove 0,0,0,1
