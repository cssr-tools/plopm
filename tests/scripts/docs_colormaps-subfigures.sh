WHR="examples/SPE11B"
WHRC="examples/SPE11C"
OUT="test_outputs/docs_colormaps-subfigures"
. tests/scripts/initialize_output_folders.sh $OUT
plopm -i $WHR -o $OUT -v satnum,fipnum,disperc -c '193;147;56 127;148;191 193;127;97 181;73;57 81;124;66 101;64;147 134;133;130',cet_glasbey_bw,'#b6c406 #fffa86' -sg 3,1 -rdl 1 -cbn 3,6,2 -cbf .0f,.0f,.1f -fs 7,4
plopm -i $WHR -o $OUT -v poro,sgas,sgas -sg 1,3 -r 0,1,5 -st 0 -fs 25,2 -c terrain,jet,jet -cbn 5 -cbf .1f -fn poro_sgas
plopm -i "$WHR $WHRC $WHR $WHRC" -o $OUT -sg 2,2 -v temp -s ',1, ,14, ,1, ,14,' -r 0,0,5,2 -st 0 -fs 10,10 -asp 0 -rdl 1 -c cet_diverging_rainbow_bgymr_45_85_c67_r -cbn 5 -cbp 0.15,0.92,0.7,0.02 -cbl 'Temperature [$^o$C]' -t 'SPE11B (initial temperature)  SPE11C (initial temperature)  SPE11B (end of simulation, 25 y)  SPE11C (end of simulation, 25 y)' -fz 15
