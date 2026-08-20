OUT="test_outputs/docs_rel_perms_and_capillary_pressure"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_pyopmnearwell.sh
mkdir $OUT
curl --output-dir $OUT -O https://raw.githubusercontent.com/cssr-tools/pyopmnearwell/refs/heads/main/examples/h2hysteresis.toml
pyopmnearwell -i $OUT/h2hysteresis.toml -o $OUT/h2hysteresis -m single
plopm -i $OUT/h2hysteresis/H2HYSTERESIS -o $OUT -v krgh,krwh -labels "Hydrogen  Brine" -c r,#0314fc -x '[0,1]' -lw 5 -f 18 -d 8,6 -ylabel 'Relative permeability, $k_r$ [-]' -xlabel ' Liquid saturation, $s_w$ [-]'  -e solid,solid -xlnum 6  -ylnum 6
plopm -i $OUT/h2hysteresis/H2HYSTERESIS -o $OUT -v krg1,krg2,krw1,krw2 -labels "Drainage hydrogen  Imbibition hydrogen  Drainage brine  Imbibition brine" -c r,r,#0314fc,#0314fc -x '[0,1]' -lw 5 -f 18 -d 8,6 -ylabel 'Relative permeability, $k_r$ [-]' -xlabel 'Liquid saturation, $s_w$ [-]' -e solid,dashed,solid,dashed  -xlnum 6  -ylnum 6
plopm -i $OUT/h2hysteresis/H2HYSTERESIS -o $OUT -v pcwg -c k -x '[0,1]' -lw 5 -loc empty -f 18 -d 8,6 -ylabel 'Capillary pressure, $p_c$ [bar]' -xlabel 'Liquid saturation, $s_w$ [-]' -e solid,dashed,solid,dashed  -xlnum 6  -ylog 1
