WHRB="examples/SPE11B"
WHRC="examples/SPE11C"
OUT="test_outputs/docs_tutorial"
. tests/scripts/initialize_output_folders.sh $OUT
plopm -i $WHRC -o $OUT -v satnum -s ,14,
plopm -i $WHRC -o $OUT -v sgas -s ,14, -r 2
plopm -i $WHRC -o $OUT -v sgas -s 55,, -r 2
plopm -i $WHRC -o $OUT -v sgas -s ,14, -r 2
plopm -i $WHRC -o $OUT -v sgas -s ,,14 -r 2
plopm -i $WHRC -o $OUT -v pressure -s ,,1:120 -agg pvmean -r 2
plopm -i $WHRC -o $OUT -fn sgas_beautiful -v sgas -s ,14, -c terrain_r -fz 14 -dpi 500 -cl "[0.1,0.8]" -cbn 5 -hide 0,0,0,1
plopm -i "$WHRC $WHRB" -o $OUT -v sgas -s ',14, ,1,' -sg 1,2 -fs 12,2.2 -t "SPE11C  SPE11B" -rdl 1
plopm -i $WHRC -o $OUT -v temp -s ,14, -r 0:2:1 -m gif -gi 500 -gl 1 -fs 9,1.5
plopm -i $WHRC -o $OUT -v pressure -s ,1, -r 2 -m csv -fn pressure_end_simulation
plopm -i $WHRB -o $OUT -v pressure,sgas -m vtk -fp flow -vn pressure,gas_saturation
