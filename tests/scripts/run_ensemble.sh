. tests/scripts/initialize_output_folders.sh
ENS="test_outputs/ensemble"
CASE="$(pwd)/examples/ensemble/run_ensemble.py"
if [ ! -d $ENS ]; then
  mkdir $ENS
  cd $ENS
  python3 $CASE
  rm -r ens0 ens1
  cd -
fi
