# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Script to run an ensemble using https://github.com/cssr-tools/pyopmnearwell"""

import subprocess
from pathlib import Path
import numpy as np
from mako.template import Template

whr = Path(__file__).resolve().parent

np.random.seed(7)

template = Template(filename=f"{whr}/case.mako")

for n in range(2):
    commands = []
    for i in range(8):
        value = np.random.uniform(0, 0.45)
        filled = template.render(value=value)

        filename = f"ens{n}run{i}.toml"
        with open(filename, "w", encoding="utf8") as file:
            file.write(filled)

        commands.append(
            [
                "pyopmnearwell",
                "-i",
                filename,
                "-o",
                f"ens{n}/ens{n}run{i}",
                "-g",
                "single",
            ]
        )
    # pylint: disable=consider-using-with
    processes = [subprocess.Popen(cmd) for cmd in commands]
    for p in processes:
        p.wait()

summary = ["wbhp:inj0", "tcpu", "msumlins", "msumnewt"]

commands = []
for i in range(4):
    commands.append(
        [
            "plopm",
            "-i",
            "ens0/ ens1/",
            "-v",
            "krgh",
            "-ensemble",
            str(i),
            "-save",
            f"example{i}",
        ]
    )
    commands.append(
        [
            "plopm",
            "-i",
            ".",
            "-v",
            summary[i],
            "-ensemble",
            "1",
            "-save",
            f"example{4+i}",
        ]
    )
# pylint: disable=consider-using-with
processes = [subprocess.Popen(cmd) for cmd in commands]
for p in processes:
    p.wait()

subprocess.run(
    [
        "plopm",
        "-i",
        "ens0/ ens1/",
        "-v",
        "krgh",
        "-ensemble",
        "3",
        "-label",
        "ens1 (mean)  ens1 (lower)  ens1 (upper)   ens2 (mean)  ens2 (lower)  ens2 (upper)",
        "-bandprop",
        "r,0.5,g,0.1",
        "-c",
        "k,grey,r,g",
        "-e",
        "solid,solid,dotted,dashed",
        "-lw",
        "2,2",
        "-t",
        "Comparing two ensembles of k$_{rg}$ with hysteresis",
        "-y",
        "[0,0.3]",
        "-yformat",
        ".2f",
        "-xformat",
        ".2f",
        "-save",
        "example3_formated",
    ],
    check=True,
)
