WHR="test_outputs/spe11b"
OUT="test_outputs/docs_reading_csvs"
CSV="$WHR/spe11b/opm"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_pyopmspe11.sh
. tests/scripts/get_spe11b_benchmark.sh
plopm -v xco2l -i "$WHR/r1_Cart_10m/R1_CART_10M $WHR/r1_Cart_10m/spe11b_spatial_map_500y" -o $OUT -csv ";1,2,5" -subfigs 2,1 -delax 1 -r 100 -d 10,3 -suptitle 0 -t "Simulation grid  Reporting grid" -cbsfax 0.35,0.97,0.3,0.02 -yunits km -xunits km -yformat .1f -xformat .1f -cnum 5 -xlnum 8 -cformat .2f
plopm -i "$WHR/r1_Cart_10m/spe11b_time_series $WHR/r1_Cart_10m/R1_CART_10M" -o $OUT -v ",BWPR:256,1,5" -csv "1,3;" -a "1e-5,1" -e "solid,dotted" -lw "4,4" -ylabel "Sensor pressure [bar]" -labels "From csv file  From OPM Flow output file" -c "r,k"
plopm -i "${CSV}1/spe11b_time_series ${CSV}2/spe11b_time_series ${CSV}3/spe11b_time_series ${CSV}4/spe11b_time_series $WHR/r1_Cart_10m/spe11b_time_series" -o $OUT -csv "1,4;1,4;1,4;1,4;1,4" -tunits y -x "[0,1000]" -ylabel "dissA [kiloton]" -yformat .1f -a 1e-6 -c "#a8d8e3,#a8d8e3,#a8d8e3,#a8d8e3,#fc035a" -lw 5,5,5,5,5 -e solid
plopm -i "${CSV}1/spe11b_spatial_map_250y ${CSV}2/spe11b_spatial_map_250y ${CSV}3/spe11b_spatial_map_250y ${CSV}4/spe11b_spatial_map_250y $WHR/r1_Cart_10m/spe11b_spatial_map_250y" -o $OUT -csv "1,2,5;1,2,5;1,2,5;1,2,5;1,2,5" -subfigs 3,2 -delax 1 -suptitle 0 -cbsfax 0.35,0.97,0.3,0.02 -yunits km -xunits km -yformat .1f -xformat .1f -cnum 5 -xlnum 8 -cformat .2f -d 14,4 -t "opm1  opm2  opm3  opm4  my simulation" -clabel 'Time 250 years, CO$_2$ mass fraction (liquid phase) [-]' -c inferno
