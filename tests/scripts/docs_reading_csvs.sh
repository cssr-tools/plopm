WHR="test_outputs/spe11b"
OUT="test_outputs/docs_reading_csvs"
CSV="$WHR/spe11b/opm"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_pyopmspe11.sh
. tests/scripts/get_spe11b_benchmark.sh
plopm -v xco2l -i "$WHR/r1_Cart_10m/R1_CART_10M $WHR/r1_Cart_10m/spe11b_spatial_map_500y" -o $OUT -cc ";1,2,5" -sg 2,1 -rdl 1 -r 100 -fs 10,3 -st 0 -t "Simulation grid  Reporting grid" -cbp 0.35,0.97,0.3,0.02 -yu km -xu km -yf .1f -xf .1f -cbn 5 -xnt 8 -cbf .2f
plopm -i "$WHR/r1_Cart_10m/spe11b_time_series $WHR/r1_Cart_10m/R1_CART_10M" -o $OUT -v ",BWPR:256,1,5" -cc "1,3;" -sf "1e-5,1" -ls "solid,dotted" -lw "4,4" -yl "Sensor pressure [bar]" -llb "From csv file  From OPM Flow output file" -c "r,k"
plopm -i "${CSV}1/spe11b_time_series ${CSV}2/spe11b_time_series ${CSV}3/spe11b_time_series ${CSV}4/spe11b_time_series $WHR/r1_Cart_10m/spe11b_time_series" -o $OUT -cc "1,4;1,4;1,4;1,4;1,4" -tu y -x "[0,1000]" -yl "dissA [kiloton]" -yf .1f -sf 1e-6 -c "#a8d8e3,#a8d8e3,#a8d8e3,#a8d8e3,#fc035a" -lw 5,5,5,5,5 -ls solid
plopm -i "${CSV}1/spe11b_spatial_map_250y ${CSV}2/spe11b_spatial_map_250y ${CSV}3/spe11b_spatial_map_250y ${CSV}4/spe11b_spatial_map_250y $WHR/r1_Cart_10m/spe11b_spatial_map_250y" -o $OUT -cc "1,2,5;1,2,5;1,2,5;1,2,5;1,2,5" -sg 3,2 -rdl 1 -st 0 -cbp 0.35,0.97,0.3,0.02 -yu km -xu km -yf .1f -xf .1f -cbn 5 -xnt 8 -cbf .2f -fs 14,4 -t "opm1  opm2  opm3  opm4  my simulation" -cbl 'Time 250 years, CO$_2$ mass fraction (liquid phase) [-]' -c inferno
