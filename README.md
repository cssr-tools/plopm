[![Build Status](https://github.com/cssr-tools/plopm/actions/workflows/CI.yml/badge.svg)](https://github.com/cssr-tools/plopm/actions/workflows/CI.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10%20|%203.11%20|%203.12-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
<img src="docs/text/figs/plopm.png" width="1100" height="300">

# plopm: Simplified and flexible tool to visualize OPM Flow geological models

## Main feature
Quick generation of PNG figures from a simulation model given any 2D slide.

## Installation
To install the _plopm_ executable in an existing Python environment: 

```bash
pip install git+https://github.com/cssr-tools/plopm.git
```

If you are interested in modifying the source code, then you can clone the repository and 
install the Python requirements in a virtual environment with the following commands:

```bash
# Clone the repo
git clone https://github.com/cssr-tools/plopm.git
# Get inside the folder
cd plopm
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

## Running plopm
You can run _plopm_ as a single command line:
```
plopm -i some_input -o some_output_folder
```
Run `plopm --help` to see all possible command line argument options.

## Getting started
See the [_examples_](https://cssr-tools.github.io/plopm/examples.html) in the [_documentation_](https://cssr-tools.github.io/plopm/introduction.html).
