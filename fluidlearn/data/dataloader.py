from pathlib import Path
import json

import h5py
import numpy as np

class DataLoaderUniform:
    _available_fields = ["p", "Ux", "Uy"]
    _field_units = {"p": "m^2/s^2", "Ux": "m/s", "Uy": "m/s"}
    def __init__(self):
        pass

    def explore_datasets(self, data_location):
        self._location = data_location
        self._available_datasets = [folder.stem for folder in self._location.iterdir() if folder.is_dir()]
    
    @property
    def available_datasets(self):
        return self._available_datasets

    def load_dataset(self, dataset_index):
        self._dataset_path = self._location / self._available_datasets[dataset_index]

        self._cases = sorted([file for file in self._dataset_path.iterdir() if file.suffix == ".h5" and file.stem != "mesh"], key=lambda x: float(x.stem))
        self._N_cases = len(self._cases)

        with open(self._dataset_path / "constants.json", "r") as file:
            self._constants = json.load(file)
        self._fields = self._constants["fields"]

    @property
    def cases(self): return self._cases
    @property
    def N_cases(self): return self._N_cases
    @property
    def constants(self): return self._constants

    @property
    def gradient(self): return self._gradient
    @gradient.setter
    def gradient(self, function):
        self._gradient = function

    def load_case(self, case, field_index): # field and case specific data
        chosen_case = self._cases[case]

        with h5py.File(chosen_case, "r") as file:
            self._runtime = file.attrs.get("runtime", np.nan) / 60.0

            self._nu = file.attrs['nu']
            
            self._time = file['t'][:].astype(np.float32)
            self._N_snapshots = self._time.shape[0]
            
            self._data_array = file["fields"][field_index][:].astype(np.float32)
    
        self._shape = self._data_array.shape[1:]
        self._N_cells = self._shape[0] * self._shape[1]

        self._Re = self._constants["Uc"] * self._constants["Lc"] / self._nu

        self._size_MB = chosen_case.stat().st_size / (1024**2)

    @property
    def shape(self): return self._shape
    @property
    def N_cells(self): return self._N_cells
    @property
    def runtime(self): return self._runtime
    @property
    def N_snapshots(self): return self._N_snapshots
    @property
    def data_array(self): return self._data_array
    @property
    def time(self): return self._time
    @property
    def nu(self): return self._nu
    @property
    def Re(self): return self._Re
    @property
    def size_MB(self): return self._size_MB

class DataLoaderMesh:
    def __init__(self):
        self._available_fields = ["Kinematic pressure", "Kinematic pressure gradient magnitude", "Horizontal velocity", "Vertical velocity", "Velocity magnitude", "Vorticity"]
        self._field_units = ["m^2/s^2", "m/s^2", "m/s", "m/s", "m/s", "1/s"]

    @property
    def available_fields(self): return self._available_fields
    @property
    def field_units(self): return self._field_units

    def explore_datasets(self, data_location):
        self._location = data_location
        self._available_datasets = [folder.stem for folder in self._location.iterdir() if folder.is_dir()]

    @property
    def available_datasets(self):
        return self._available_datasets

    def load_dataset(self, dataset_index):
        self._dataset_path = self._location / self._available_datasets[dataset_index]

        self._cases = sorted([file for file in self._dataset_path.iterdir() if file.suffix == ".h5" and file.stem != "mesh"], key=lambda x: float(x.stem))
        self._N_cases = len(self._cases)

        with open(self._dataset_path / "constants.json", "r") as file:
            self._constants = json.load(file)

    @property
    def cases(self): return self._cases
    @property
    def N_cases(self): return self._N_cases
    @property
    def constants(self): return self._constants

    def load_mesh(self):
        with h5py.File(self._dataset_path / "mesh.h5", "r") as file:
            self._mesh_centers = file["centroids"][:].astype(np.float32)
            self._mesh_vertices = file["vertices"][:].astype(np.float32)
            self._mesh_indices = file["indices"][:].astype(np.uint32)

        self._N_cells = len(self._mesh_centers)
        self._N_vertices = len(self._mesh_vertices)

    @property
    def N_cells(self): return self._N_cells
    @property
    def N_vertices(self): return self._N_vertices
    @property
    def mesh_centers(self): return self._mesh_centers
    @property
    def mesh_vertices(self): return self._mesh_vertices
    @property
    def mesh_indices(self): return self._mesh_indices

    @property
    def gradient(self): return self._gradient
    @gradient.setter
    def gradient(self, function):
        self._gradient = function

    def load_case(self, case, field_index): # field and case specific data
        chosen_case = self._cases[case]
        field = self._available_fields[field_index]   # i.e., "p", "Ux", "Uy", "|U|"...

        with h5py.File(chosen_case, "r") as file:
            self._runtime = file.attrs.get("runtime", np.nan) / 60.0

            self._nu = file.attrs['nu']
            
            self._time = file['t'][:].astype(np.float32)
            self._N_snapshots = self._time.shape[0]
            match field:
                case "Kinematic pressure":
                    self._data_array = file['p'][:, :].astype(np.float32)
                case "Kinematic pressure gradient magnitude":
                    self._data_array = np.empty((self._N_snapshots, self._N_cells), dtype=np.float32)
                    for snap in range(self._N_snapshots):
                        p_grad = self._gradient(file['p'][snap, :])
                        self._data_array[snap] = np.sqrt(p_grad[0]**2 + p_grad[1]**2)
                case "Horizontal velocity":
                    self._data_array = file['U'][:, :, 0].astype(np.float32)
                case "Vertical velocity":
                    self._data_array = file['U'][:, :, 1].astype(np.float32)
                case "Velocity magnitude":
                    self._data_array = np.sqrt(file['U'][:, :, 0]**2 + file['U'][:, :, 1]**2).astype(np.float32)
                case "Vorticity":
                    self._data_array = np.empty((self._N_snapshots, self._N_cells), dtype=np.float32)
                    for snap in range(self._N_snapshots):
                        U_grad = self._gradient(file['U'][snap, :, 0])
                        V_grad = self._gradient(file['U'][snap, :, 1])
                        self._data_array[snap] = V_grad[0] - U_grad[1]
    
        self._Re = self._constants["Uc"] * self._constants["Lc"] / self._nu

        self._size_MB = chosen_case.stat().st_size / (1024**2)

    @property
    def runtime(self): return self._runtime
    @property
    def N_snapshots(self): return self._N_snapshots
    @property
    def data_array(self): return self._data_array
    @property
    def time(self): return self._time
    @property
    def nu(self): return self._nu
    @property
    def Re(self): return self._Re
    @property
    def size_MB(self): return self._size_MB