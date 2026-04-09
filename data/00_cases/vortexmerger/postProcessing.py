import sys
import json
from pathlib import Path

import h5py
import numpy as np
import pyvista as pv

case_i = int(sys.argv[1])

home_dir = Path.home()
root_name = Path.cwd().name

with open(f"VTK/{root_name}.vtm.series", "r") as file:
    jsondata = json.load(file)
jsondata = sorted(jsondata["files"], key=lambda x: float(x["time"]))

N_snaps = len(jsondata)
for j, entry in enumerate(jsondata):
    snap_folder = entry["name"].split('.vtm')[0]
    snap_time = entry["time"]

    data = pv.read(f"VTK/{snap_folder}/internal.vtu")
    surface = data.slice(normal='z').extract_surface(algorithm='dataset_surface')

    if j == 0 and snap_time == 0.0:
        N_cells = surface.n_cells
        U = np.empty((N_snaps, N_cells, 2))
        p = np.empty((N_snaps, N_cells))
        t = np.empty(N_snaps)

    if case_i == 0:
        # Centroids, vertices, indices
        centroids = surface.cell_centers().points[:, :2]
        vertices = surface.points[:, :2]

        indices = np.full((N_cells, 4), -1, dtype=np.int32)
        for i in range(N_cells):
            indices_i = surface.get_cell(i).point_ids
            indices[i, :len(indices_i)] = indices_i

        with h5py.File(home_dir / "output/mesh.h5", "w") as file:
            file.create_dataset("centroids", data=centroids, compression="gzip", chunks=True)
            file.create_dataset("vertices", data=vertices, compression="gzip", chunks=True)
            file.create_dataset("indices", data=indices, compression="gzip", chunks=True)

    t[j] = snap_time
    U[j] = surface["U"][:, :2]
    p[j] = surface["p"]

with h5py.File(home_dir / f"output/{case_i}.h5", "a") as file:
    file.create_dataset("U", data=U, compression="gzip", chunks=(1,N_cells,2))
    file.create_dataset("p", data=p, compression="gzip", chunks=(1,N_cells))
    file.create_dataset("t", data=t, compression="gzip", chunks=(N_snaps,))