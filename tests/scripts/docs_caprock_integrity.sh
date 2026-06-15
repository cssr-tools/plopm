WHR="test_outputs/opm-data/norne/NORNE_ATW2013"
OUT="test_outputs/docs_caprock_integrity"
INC="test_outputs/opm-data/norne/INCLUDE"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_opm_data.sh
. tests/scripts/run_norne.sh
plopm -i $WHR -o $OUT -s ',,1:22 ,,1:22' -v limipres,overpres -rotate 65 -translate '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -d 15,10 -c Spectral,spring, -subfigs 1,2 -delax 1
plopm -i $WHR -o $OUT -m csv -v objepres -s ',,1:22'
