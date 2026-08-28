WHR="examples/SPE11B"
OUT="test_outputs/docs_colormaps"
. tests/scripts/initialize_output_folders.sh $OUT
plopm -i $WHR -o $OUT -v satnum,fipnum,disperc -c '193;147;56 127;148;191 193;127;97 181;73;57 81;124;66 101;64;147 134;133;130',cet_glasbey_bw,'#b6c406 #fffa86' -sg 3,1 -rdl 1 -cbn 3,6,2 -cbf .0f,.0f,.1f -fs 7,4
