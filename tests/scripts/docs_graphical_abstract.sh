
OUT="test_outputs/docs_graphical_abstract"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_opm_data.sh
. tests/scripts/get_pyopmspe11.sh
. tests/scripts/run_norne_dryrun.sh
. tests/scripts/run_spe11b_larger_injection.sh
. tests/scripts/run_spe11c.sh
WHC="test_outputs/spe11c"
NORNE="test_outputs/opm-data/norne/NORNE_ATW2013"
WHR="test_outputs/spe11b"
plopm -i "$WHR/spe11b_base/SPE11B_BASE $WHR/spe11b_larger_inj/SPE11B_LARGER_INJ" -o $OUT -v 'fgmip * 1e-6' -c 'r,b' -tu y -xf .0f -lw 2 -label 'Base case  Higher injection rate' -xnt 6 -yl 'Total CO$_2$ mass [Kt]' -fz 18 -t 'Comparing two runs of the SPE11B model'
plopm -i $NORNE -o $OUT -v permx -clog 1 -rot 65 -s ,,1 -tr '[6456335.5,-3476500]' -x '[0,5600]' -y '[0,7600]' -t "Top view of NORNE" -xu km -yu km -fz 16 -ge 'black,1e-2' -xf .1f -yf .1f -fs 8,8
plopm -i $WHC/spe11c/SPE11C -o $OUT -v satnum,xco2l -vf UInt16,Float16 -r 0,5 -m vtk
