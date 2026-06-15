WHR="test_outputs/spe11b"
if [ ! -d $WHR ]; then
  mkdir $WHR
fi
if [ ! -f "$WHR/r1_Cart_10m.toml" ]; then
  in="$WHR/r1_Cart_10m.toml"
  tmp="${in}.tmp"
  curl --output-dir $WHR -O https://raw.githubusercontent.com/OPM/pyopmspe11/refs/heads/main/benchmark/spe11b/r1_Cart_10m.toml
  sed -i.bak 's/-np 32/-np 8/g' $in && rm -f $in.bak
  sed -i.bak 's/\[840\]/\[420\]/g' $in && rm -f $in.bak
  sed -i.bak 's/\[120\]/\[60\]/g' $in && rm -f $in.bak  
{
  head -n 50 "$in"

  cat <<'EOF'
inj = [[  25, 5, 1, 0.035, 10, 1,     0, 10],
       [  25, 5, 1, 0.035, 10, 1, 0.035, 10],
       [ 950, 5, 1,     0, 10, 1,     0, 10]]
EOF

  tail -n +56 "$in"
} > "$tmp" && mv "$tmp" "$in"
  pyopmspe11 -i $in -o $WHR/r1_Cart_10m -m deck_flow_data -g all -t 5 -r 70,1,30 -w 0.1 -f 0
fi
## The whole zip files are quite large so it could be slow, then we have save the required files for the examples in the data/spe11b folder
# if [ ! -f "$WHR/spe11b/opm4/spe11b_spatial_map_250y.csv" ]; then
#   for f in 375740 375725 375754 375726; do
#     curl --output-dir "$WHR" -L -O "https://darus.uni-stuttgart.de/api/access/datafile/$f"
#     unzip -q "$WHR/$f" -d "$WHR"
#     rm "$WHR/$f"

#     find "$WHR/spe11b" -type f ! \( \
#       -name "spe11b_spatial_map_250y.csv" -o \
#       -name "spe11b_time_series.csv" \
#     \) -delete
#   done
# fi
cp -r tests/data/spe11b $WHR