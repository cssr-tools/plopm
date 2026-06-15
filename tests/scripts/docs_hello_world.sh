WHR="examples/SPE11B"
OUT="test_outputs/docs_hello_world"
. tests/scripts/initialize_output_folders.sh $OUT
plopm -i $WHR -o $OUT
plopm -i $WHR -o $OUT -v sgas -r 4 -cnum 3 -c cubehelix -cticks '[0, middle, 0.9]'
plopm -i $WHR -o $OUT -v fgip -c b -e dotted -f 12 -d 5,5 -lw 4 -tunits dates
plopm -i "$WHR $WHR $WHR" -o $OUT -v 'pressure - 0pressure' -s '1,1,1 41,1,29 83,1,58' -labels 'Top left corner  Middle  Right lower corner' -ylabel 'Pressure increase at the sensor locations [bar]' -yformat .0f -xlnum 11 -tunits dates
