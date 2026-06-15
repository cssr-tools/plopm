WHR="test_outputs/opm-data/norne/NORNE_ATW2013"
OUT="test_outputs/docs_projections_subfigures"
INC="test_outputs/opm-data/norne/INCLUDE"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_opm_data.sh
. tests/scripts/run_norne_dryrun.sh
plopm -i $WHR -o $OUT -v 'index_k,permx,poro' -s ',,1:22 ,,1:22 ,,1:22' -how 'first,arithmetic,max' -subfigs 1,3 -rotate 65 -translate '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -d 24,10 -c 'PuOr,vanimo,jet' -cformat '.0f,.0f,.2f' -cnum '2,4,8' -suptitle 0 -t "Top k values using first  Averaged permx using arithmetic  Values of porosity using max" -f 18
