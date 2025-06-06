#Set mpirun, the full path to the flow executable, and simulator flags (except --output-dir)
flow = "flow --relaxed-max-pv-fraction=0 --output-extra-convergence-info=steps,iterations --enable-opm-rst-file=true --newton-min-iterations=1 --enable-well-operability-check=false --min-time-step-before-shutting-problematic-wells-in-days=1e-99"

#Set the model parameters
model = "co2store" #Model: co2store, co2eor, foam, h2store, or saltprec
template = "no_disgas_no_diffusion" #Template file (see src/pyopmnearwell/templates/)
grid = "cake" #Grid type: cake, radial, core, cartesian2d, coord2d, tensor2d, cartesian, cpg3d, coord3d, or tensor3d
adim = 60 #Grid cake/radial: theta [degrees]; core: input/output pipe length [m]; cartesian2d, coord2d, tensor2d: width[m]
xdim = 10000 #Length [m] (for cartesian/cpg3d/coord3d/tensor3d, Length=Width=2*xdim)
xcn = [600] #Number of x-cells [-]; coordinates for grid type coord2d/coord3d [m]; numbers of x-cells for grid type tensor2d/tensor3d [-]
xfac = 4 #Exponential factor for the telescopic x-gridding (0 to use an equidistant partition)
diameter = 0.3 #Well diameter [m] 
pressure = 213 #Pressure [Bar] on the top 
temperature = [40,40] #Top and bottom temperatures [C]
initialphase = 0 #Initial phase in the reservoir (0 wetting, 1 non-wetting) 
pvmult = -1 #Pore volume multiplier on the boundary [-] (-1 to ignore; 0 to use well producers instead)
rockcomp = 8.5e-5 #Rock compressibility [1/Bar]
hysteresis = "Killough" #Add hysteresis (Killough or Carlson, 0 by default, i.e., no hysteresis)

#Set the saturation functions
krw = "krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw"        #Wetting rel perm saturation function [-]
krn = "krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn" #Non-wetting rel perm saturation function [-]
pcap = "pen * ((sw - swi) / (1.0 - swi)) ** (-(1.0 / npen))" #Capillary pressure saturation function [Bar]

#Properties sat functions: 1) swi [-], 2) sni [-], 3) krw [-], 4) krn [-], 5) pen [Bar], 6) nkrw [-],
#7) nkrn [-], 8) npen [-], 9) threshold cP evaluation, 10) ignore swi for cP? (sl* for cplog)
#11) npoints [-] (entry per layer, if hysteresis, additional entries per layer)
safu = [[0.478,0,1,0.3,0,3,3,2,1e-5,0,10000],[0.478,${value},1,0.3,0,3,3,2,1e-5,0,10000]]

#Properties rock: 1) Kxy [mD], 2) Kz [mD], 3) phi [-], 4) thickness [m], and 5) no cells in the z dir [-] (entry per layer)
rock = [[1000,1000,0.25,10,10]]

#Define the injection values (entry per change in the schedule): 
#1) injection time [d], 2) time step size to write results [d], 3) maximum time step [d]
#4) fluid (0 wetting, 1 non-wetting), 5) injection rates [kg/day]
inj = [[7,7,7,1,1e6],[7,7,7,1,0],[7,7,7,1,1e6]]