WHR="test_outputs/opm-data/norne/NORNE_ATW2013"
OUT="test_outputs/docs_projections_subfigures"
INC="test_outputs/opm-data/norne/INCLUDE"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_opm_data.sh
. tests/scripts/run_norne_dryrun.sh
plopm -i $WHR -o $OUT -v 'index_k,permx,poro' -s ',,1:22 ,,1:22 ,,1:22' -agg 'first,arithmetic,max' -sg 1,3 -rot 65 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,8800]' -fs 24,10 -c 'PuOr,vanimo,jet' -cbf '.0f,.0f,.2f' -cbn '2,4,8' -st 0 -t "Top k values using first  Averaged permx using arithmetic  Values of porosity using max" -fz 18
