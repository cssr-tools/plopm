WHR="test_outputs/spe11b"
OUT="test_outputs/docs_gif_mask"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_pyopmspe11.sh
. tests/scripts/run_spe11b_larger_injection.sh
plopm -v xco2l -subfigs 1,2 -i "$WHR/spe11b_base/SPE11B_BASE $WHR/spe11b_larger_inj/SPE11B_LARGER_INJ" -o $OUT -d 16,2.5 -mask satnum -r 0,1,2,3,4,5 -m gif -dpi 1000 -t "spe11b  spe11b larger injection" -f 16 -interval 1000 -loop 1 -cformat .2f -cbsfax 0.30,0.01,0.4,0.02
plopm -i $WHR/spe11b_base/SPE11B_BASE -o $OUT -v sgas -tunits y -c cet_cwr  -grid 'black,5e-3' -d 16,5 -m gif -dpi 1000 -f 20 -interval 1000 -loop 1 -cformat .2f -z 0 -xunits km -yunits km -xformat .1f -yformat .1f -cnum 5 -clabel 'Gas saturation [-]'
