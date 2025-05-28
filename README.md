[![Build Status](https://github.com/cssr-tools/plopm/actions/workflows/CI.yml/badge.svg)](https://github.com/cssr-tools/plopm/actions/workflows/CI.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.9%20to%203.13-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://zenodo.org/badge/828515658.svg)](https://zenodo.org/doi/10.5281/zenodo.13332414)
<img src="docs/text/figs/plopm.png" width="1100" height="300">

# plopm: Simplified and flexible tool to visualize OPM Flow geological models

## Main feature
Quick generation of PNG figures, GIFs, and VTKs from a OPM Flow type model.

## Installation
To install the _plopm_ executable in an existing Python environment: 

```bash
pip install git+https://github.com/cssr-tools/plopm.git
```

If you are interested in a specific version (e.g., v2025.04) or in modifying the source code, then you can clone the repository and install the Python requirements in a virtual environment with the following commands:

```bash
# Clone the repo
git clone https://github.com/cssr-tools/plopm.git
# Get inside the folder
cd plopm
# For a specific version (e.g., v2025.04), or else skip this step (i.e., edge version)
git checkout v2025.04
# Create virtual environment (for macOS, use a Python version >= 3.10)
python3 -m venv vplopm
# Activate virtual environment
source vplopm/bin/activate
# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel
# Install the plopm package
pip install -e .
# Install the dev-requirements
pip install -r dev-requirements.txt
``` 

To use the conversion from OPM Flow output files (i.e., .EGRID, .INIT, .UNRST) to VTK (e.g, to use [_paraview_](https://www.paraview.org) for visualization/postprocessing), [_OPM Flow_](https://opm-project.org) is needed. See the [_installation_](https://cssr-tools.github.io/plopm/installation.html) for further details on installing binaries or building OPM Flow from the master branches in Linux, Windows, and macOS, as well as the opm Python package and LaTeX dependencies. 

## Running plopm
You can run _plopm_ as a single command line:
```
plopm -i name(s)_of_input_file(s)
```
Run `plopm --help` to see all possible command line argument options.

## Getting started
See the [_examples_](https://cssr-tools.github.io/plopm/examples.html) in the [_documentation_](https://cssr-tools.github.io/plopm/introduction.html).

## Citing
* Landa-Marbán, D. 2024. plopm: Quick generation of PNGs, GIFs, and VTKs from a OPM Flow type model. https://doi.org/10.5281/zenodo.13332415.

## About plopm
The _plopm_ package is being funded by the [_HPC Simulation Software for the Gigatonne Storage Challenge project_](https://www.norceresearch.no/en/projects/hpc-simulation-software-for-the-gigatonne-storage-challenge) [project number 622059] and [_Center for Sustainable Subsurface Resources (CSSR)_](https://cssr.no) 
[project no. 331841].
This is work in progress.
Contributions are more than welcome using the fork and pull request approach. For new features, please request them raising an issue.