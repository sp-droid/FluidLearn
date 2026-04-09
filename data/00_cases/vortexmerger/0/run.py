# Before running do:
# postProcess -func writeCellCentres
# Then remove all the junk (attention to include only one surface!) in the C file except the points themselves, nothing else
# Then run this script
# Then copy and paste manually into p and U files

import math

# -------------------------------
# Parameters
# -------------------------------
Gamma = 1.0       # circulation of EACH vortex
L     = 1.0
a     = 0.05 * L   # core size of the vortices

# vortex centers
vortices = [
    (0.333, 0.5),
    (0.667, 0.5)
]

# -------------------------------
# Read cell centers
# -------------------------------
with open("0/C", "r") as f:
    lines = f.readlines()

C = []
for line in lines:
    line = line.strip()
    if line.startswith("(") and line.endswith(")"):
        x, y, z = map(float, line.strip("()").split())
        C.append((x, y, z))

N = len(C)
print(f"Read {N} cell centers")

# -------------------------------
# Lamb–Oseen vortex velocity
# -------------------------------
def lamb_oseen_velocity(x, y, x0, y0):
    dx = x - x0
    dy = y - y0

    r2 = dx*dx + dy*dy
    r = math.sqrt(r2)
    theta = math.atan2(dy, dx)

    if r < 1e-7:
        return 0.0, 0.0

    u_theta = Gamma / (2 * math.pi * r) * (1 - math.exp(-r2/(a*a)))

    ux = -u_theta * math.sin(theta)
    uy =  u_theta * math.cos(theta)
    return ux, uy

# -------------------------------
# Superpose vortices
# -------------------------------
U = []
for x, y, z in C:
    ux, uy = 0.0, 0.0
    for (x0, y0) in vortices:
        dux, duy = lamb_oseen_velocity(x, y, x0, y0)
        ux += dux
        uy += duy

    U.append((ux, uy, 0.0))

# -------------------------------
# Write U
# -------------------------------
with open("0/U_internal", "w") as f:
    f.write("internalField nonuniform List<vector>\n")
    f.write(f"{N}\n(\n")
    for ux, uy, uz in U:
        f.write(f"({ux} {uy} {uz})\n")
    f.write(");\n")
