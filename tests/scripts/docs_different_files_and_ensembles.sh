WHR="test_outputs/spe11b"
ENS="test_outputs/ensemble"
OUT="test_outputs/docs_different_files_and_ensembles"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_pyopmnearwell.sh
. tests/scripts/get_pyopmspe11.sh
. tests/scripts/run_spe11b_larger_injection.sh
. tests/scripts/run_ensemble.sh
plopm -i "$WHR/spe11b_base/SPE11B_BASE $WHR/spe11b_larger_inj/SPE11B_LARGER_INJ" -o $OUT -v 'fgmip,fgmip / 1E6,RGMDS:5' -yl '[kg]  [Kt]  [kg]' -tu w -fs 10,5 -c r,b -ls 'solid,dashed' -t 'Field gas mass in place  Converted to kilotonns   Dissolved CO$_2$ in facie 5' -fz 14 -sg 2,2 -rdl 1 -ll empty,empty,empty,center -fn comparison
plopm -i $WHR/spe11b_larger_inj/SPE11B_LARGER_INJ -o $OUT -v sgas -r 3 -di $WHR/spe11b_base/SPE11B_BASE -hide 0,0,0,1
plopm -i $WHR/spe11b_larger_inj/SPE11B_LARGER_INJ -o $OUT -v sgas -r 3 -di $WHR/spe11b_base/SPE11B_BASE -hide 0,0,0,1 -c tab20c_r -cl '[0,0.8]' -cbn 9 -cbf 0.1 -fn formated
cp $ENS/example0.png $OUT/example0.png
cp $ENS/example3_formated.png $OUT/example3_formated.png
