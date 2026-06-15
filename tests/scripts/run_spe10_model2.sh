. tests/scripts/initialize_output_folders.sh
WHR="test_outputs/opm-data/spe10model2/SPE10_MODEL2"
if [ ! -f "$WHR.INIT" ]; then
    flow $WHR.DATA --parsing-strictness=low --enable-dry-run=1 --check-satfunc-consistency=0
fi
