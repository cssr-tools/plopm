WHR="test_outputs/opm-data/norne/NORNE_ATW2013"
OUT="test_outputs/docs_caprock_integrity"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_opm_data.sh
. tests/scripts/run_norne.sh
plopm -i $WHR -o $OUT -s ',,1:22 ,,1:22' -v limipres,overpres -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -fs 15,10 -c Spectral,spring -sg 1,2 -rdl 1
plopm -i $WHR -o $OUT -m csv -v objepres -s ',,1:22'
