WHR="test_outputs/opm-data/norne/NORNE_ATW2013"
OUT="test_outputs/docs_rotation_translation_zoom"
INC="test_outputs/opm-data/norne/INCLUDE"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_opm_data.sh
. tests/scripts/run_norne_dryrun.sh
plopm -i $WHR -o $OUT -s ,,1 -rotate 65 -translate '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,7600]' -f 8
plopm -i $WHR -o $OUT -v faults -s ,,1 -rotate 65 -translate '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -f 8 -global 1
plopm -i $WHR -o $OUT -v faults -s ,,1:22 -rotate 65 -translate '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -f 8 -how max
plopm -i $WHR -o $OUT -v wells -s ,,1 -rotate 65 -translate '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -f 8 -global 1 -save "norne_wells_global"
plopm -i $WHR -o $OUT -v wells -s ,,1 -rotate 65 -translate '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -f 8 -save "norne_wells"
