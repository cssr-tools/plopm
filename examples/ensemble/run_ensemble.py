# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Script to run an ensemble using pyopmnearwell:
https://github.com/cssr-tools/pyopmnearwell
"""

import os
import numpy as np
from mako.template import Template

np.random.seed(7)

for n in range(2):
    command = ""
    for i in range(8):
        mytemplate = Template(filename="case.mako")
        var = {"value": np.random.uniform(0, 0.45, 1)[0]}
        filledtemplate = mytemplate.render(**var)
        with open(
            f"ens{n}run{i}.toml",
            "w",
            encoding="utf8",
        ) as file:
            file.write(filledtemplate)
        command += (
            f"pyopmnearwell -i ens{n}run{i}.toml -o ens{n}/ens{n}run{i} -g single & "
        )
    command += "wait"
    os.system(command)
summary = ["wbhp:inj0", "tcpu", "msumlins", "msumnewt"]
command = ""
for i in range(4):
    command += f"plopm -i 'ens0/ ens1/' -v krgh -ensemble {i} -save example{i} & "
    command += f"plopm -i '.' -v {summary[i]} -ensemble 1 -save example{4+i} & "
command += "wait"
os.system(command)
os.system("plopm -i 'ens0/ ens1/' -v krgh -ensemble 3 -label 'ens1 (mean)  ens1 (lower)  ens1 (upper)   ens2 (mean)  ens2 (lower)  ens2 (upper)' "
"-bandprop r,0.5,g,0.1 -c k,grey,r,g -e solid,solid,dotted,dashed -lw 2,2 -t 'Comparing two ensembles of k$_{rg}$ with hysteresis' -y '[0,0.3]' "
"-yformat .2f -xformat .2f -save example3_formated")
