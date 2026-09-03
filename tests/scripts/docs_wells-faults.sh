WHR="test_outputs/opm-data/norne/NORNE_ATW2013"
OUT="test_outputs/docs_wells-faults"
INC="test_outputs/opm-data/norne/INCLUDE"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_opm_data.sh
. tests/scripts/run_norne_dryrun.sh
plopm -i $WHR -o $OUT -v faults -s ,,1 -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -fz 8 -gr 1
plopm -i $WHR -o $OUT -v faults -s ,,1:22 -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -fz 8 -agg max
plopm -i $WHR -o $OUT -v wells -s ,,1 -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -fz 8 -gr 1 -fn "norne_wells_global"
plopm -i $WHR -o $OUT -v wells -s ,,1 -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -fz 8 -fn "norne_wells"
