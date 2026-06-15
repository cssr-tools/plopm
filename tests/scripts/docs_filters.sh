WHR="examples/SPE11B"
OUT="test_outputs/docs_filters"
. tests/scripts/initialize_output_folders.sh $OUT
plopm -i "$WHR $WHR $WHR" -o $OUT -filter ',fipnum >= 2 & fipnum != 4,satnum == 5' -v fipnum -subfigs 3,1 -delax 1 -cformat .0f -d 7,4 -u resdata -cbsfax 0.15,0.97,0.7,0.02 -t "No filter  fipnum >= 2 and fipnum != 4  satnum == 5" -suptitle 0
