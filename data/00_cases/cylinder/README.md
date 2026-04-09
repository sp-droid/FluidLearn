### Instructions

- Open in UNIX system or WSL, make sure the environment has the requirements.txt python packages
- Open in Gmsh the chosen geometry in /mesh, export the mesh with ".msh" extension and the "Version 2 ASCII" format in the main folder. Then:

```bash
gmshToFoam mesh.msh
checkMesh
```

- Edit `sim.sh` for the number of cases, edit `constant.json` for dataset-wide constants
- Execute

```bash
./sim.sh
```

- Results in `~/output`