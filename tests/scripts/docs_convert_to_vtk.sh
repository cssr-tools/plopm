WHR="examples/SPE11B"
OUT="test_outputs/docs_convert_to_vtk"
. tests/scripts/initialize_output_folders.sh $OUT
plopm -i $WHR -o $OUT -v temp,fipnum,co2m,xco2l -vtkformat Float32,UInt16,Float64,Float16 -r 0,5 -m vtk
