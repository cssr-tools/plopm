. tests/scripts/initialize_output_folders.sh
WHR="test_outputs/spe11c"
if [ ! -d $WHR ]; then
  mkdir $WHR
  curl --output-dir $WHR -O https://raw.githubusercontent.com/OPM/pyopmspe11/refs/heads/main/examples/spe11c.toml
  pyopmspe11 -i $WHR/spe11c.toml -o $WHR/spe11c -f 0
fi
