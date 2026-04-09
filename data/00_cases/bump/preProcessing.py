import sys
import json
from pathlib import Path

import h5py
import numpy as np

home_dir = Path.home()

# Inputs
# sys.argv[0] is the script name, sys.argv[1] is the first argument
case_i = int(sys.argv[1])
N_cases = int(sys.argv[2])

# Dataset wide constants
with open("constants.json", "r") as file:
    constants = json.load(file)
Uc = constants["Uc"] # m/s
Lc = constants["Lc"] # m
minRe = constants["minRe"] # min Reynolds number
maxRe = constants["maxRe"] # max Reynolds number

if case_i == 0:
    with open(home_dir / "output/constants.json", "w") as file:
        json.dump(constants, file, indent=4)

# Processing
Re = np.linspace(minRe, maxRe, N_cases)[case_i]
nu = Lc * Uc / Re

if case_i == 0:
    print("Planned Re: \n",np.linspace(minRe, maxRe, N_cases))

print(f"Case {case_i+1}/{N_cases}:\t Re={Re} [-],\t nu={nu} m^2/s")

# Writing case parameters
with h5py.File(home_dir / f"output/{case_i}.h5", "w") as file:
    file.attrs["nu"] = nu

# Writing viscosity
with open("constant/transportProperties.orig", "r") as file:
    contents = file.read()
contents = contents.replace("{{nu}}", f"{nu:.5f}")
with open("constant/transportProperties", "w") as file:
    file.write(contents)
