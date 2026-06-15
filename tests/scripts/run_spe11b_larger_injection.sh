. tests/scripts/initialize_output_folders.sh
WHR="test_outputs/spe11b"
if [ ! -d $WHR ]; then
  mkdir $WHR
fi
if [ ! -d "$WHR/spe11b_larger_inj" ]; then
  curl --output-dir $WHR -O https://raw.githubusercontent.com/OPM/pyopmspe11/refs/heads/main/examples/spe11b.toml
  cp $WHR/spe11b.toml $WHR/spe11b_larger_inj.toml
  sed -i.bak 's/0.035/0.07/g' $WHR/spe11b_larger_inj.toml && rm -f $WHR/spe11b_larger_inj.toml.bak
  pyopmspe11 -i $WHR/spe11b.toml -o $WHR/spe11b_base -f 0
  pyopmspe11 -i $WHR/spe11b_larger_inj.toml -o $WHR/spe11b_larger_inj -f 0
fi
