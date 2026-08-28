WHR="examples/SPE11B"
OUT="test_outputs/docs_hello_world"
. tests/scripts/initialize_output_folders.sh $OUT
plopm -i $WHR -o $OUT
plopm -i $WHR -o $OUT -v sgas -r 4 -cbn 3 -c cubehelix -cbt '[0, middle, 0.9]'
plopm -i $WHR -o $OUT -v fgip -c b -ls dotted -fz 12 -fs 5,5 -lw 4 -tu dates
plopm -i "$WHR $WHR $WHR" -o $OUT -v 'pressure - 0pressure' -s '1,1,1 41,1,29 83,1,58' -llb 'Top left corner  Middle  Right lower corner' -yl 'Pressure increase at the sensor locations [bar]' -yf .0f -xnt 11 -tu dates
