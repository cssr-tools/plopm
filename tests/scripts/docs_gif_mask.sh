WHR="test_outputs/spe11b"
OUT="test_outputs/docs_gif_mask"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_pyopmspe11.sh
. tests/scripts/run_spe11b_larger_injection.sh
plopm -v xco2l -sg 1,2 -i "$WHR/spe11b_base/SPE11B_BASE $WHR/spe11b_larger_inj/SPE11B_LARGER_INJ" -o $OUT -fs 16,2.5 -mv satnum -r 0,1,2,3,4,5 -m gif -dpi 1000 -t "spe11b  spe11b larger injection" -fz 16 -gi 1000 -gl 1 -cbf .2f -cbp 0.30,0.01,0.4,0.02
plopm -i $WHR/spe11b_base/SPE11B_BASE -o $OUT -v sgas -tu y -c cet_cwr  -ge 'black,5e-3' -fs 16,5 -m gif -dpi 1000 -fz 20 -gi 1000 -gl 1 -cbf .2f -asp 0 -xu km -yu km -xf .1f -yf .1f -cbn 5 -cbl 'Gas saturation [-]'
