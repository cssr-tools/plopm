WHR="examples/SPE11B"
OUT="test_outputs/docs_filters"
. tests/scripts/initialize_output_folders.sh $OUT
plopm -i "$WHR $WHR $WHR" -o $OUT -flt ',fipnum >= 2 & fipnum != 4,satnum == 5' -v fipnum -sg 3,1 -rdl 1 -cbf .0f -fs 7,4 -cbp 0.15,0.97,0.7,0.02 -t "No filter  fipnum >= 2 and fipnum != 4  satnum == 5" -st 0
