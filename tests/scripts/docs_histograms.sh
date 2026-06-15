WHR="test_outputs/opm-data/norne/NORNE_ATW2013"
OUT="test_outputs/docs_histograms"
INC="test_outputs/opm-data/norne/INCLUDE"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_opm_data.sh
. tests/scripts/run_norne_dryrun.sh
plopm -i $WHR -o $OUT -v poro,permx -histogram '20,norm 20,lognorm' -axgrid 0 -subfigs 1,2 -d 15,5 -loc 'upper center' -y '[0,10000] [0,23000]' -c '#7274b3,#cddb6e'
