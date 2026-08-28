OUT="test_outputs/docs_rel_perms_and_capillary_pressure"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_pyopmnearwell.sh
mkdir $OUT
curl --output-dir $OUT -O https://raw.githubusercontent.com/cssr-tools/pyopmnearwell/refs/heads/main/examples/h2hysteresis.toml
pyopmnearwell -i $OUT/h2hysteresis.toml -o $OUT/h2hysteresis -m single
plopm -i $OUT/h2hysteresis/H2HYSTERESIS -o $OUT -v krgh,krwh -llb "Hydrogen  Brine" -c r,#0314fc -x '[0,1]' -lw 5 -fz 18 -fs 8,6 -yl 'Relative permeability, $k_r$ [-]' -xl ' Liquid saturation, $s_w$ [-]'  -ls solid,solid -xnt 6  -ynt 6
plopm -i $OUT/h2hysteresis/H2HYSTERESIS -o $OUT -v krg1,krg2,krw1,krw2 -llb "Drainage hydrogen  Imbibition hydrogen  Drainage brine  Imbibition brine" -c r,r,#0314fc,#0314fc -x '[0,1]' -lw 5 -fz 18 -fs 8,6 -yl 'Relative permeability, $k_r$ [-]' -xl 'Liquid saturation, $s_w$ [-]' -ls solid,dashed,solid,dashed  -xnt 6  -ynt 6
plopm -i $OUT/h2hysteresis/H2HYSTERESIS -o $OUT -v pcwg -c k -x '[0,1]' -lw 5 -ll empty -fz 18 -fs 8,6 -yl 'Capillary pressure, $p_c$ [bar]' -xl 'Liquid saturation, $s_w$ [-]' -ls solid,dashed,solid,dashed  -xnt 6  -ylog 1
