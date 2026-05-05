from pathlib import Path
import json

import h5py
import numpy as np

class DataLoaderGrid:
    _available_fields = ["p", "Ux", "Uy", "|U|","Valid mask", "Validity", "SDF"]
    _field_units = {"p": "m^2/s^2", "Ux": "m/s", "Uy": "m/s", "|U|": "m/s", "Valid mask": "[1 = valid]", "Validity": "[1 = fully valid]", "SDF": "[<0 inside, >0 outside]"}
    def __init__(self):
        pass

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

        self._cases = sorted([file for file in self._dataset_path.iterdir() if file.suffix == ".h5" and file.stem != "constants"], key=lambda x: float(x.stem))
        self._N_cases = len(self._cases)

        with open(self._dataset_path / "constants.json", "r") as file:
            self._constants = json.load(file)
        self._fields = self._constants["fields"]

        with h5py.File(self._dataset_path / "constants.h5", "r") as file:
            self._validity = file["validity"][:].astype(np.float32)
            self._sdf = file["sdf"][:].astype(np.float32)

        self._valid_mask = self._validity > 0
        self._N_valid = np.sum(self._valid_mask)
        self._shape = self._validity.shape
        self._N_cells = self._shape[0] * self._shape[1]

    @property
    def cases(self): return self._cases
    @property
    def N_cases(self): return self._N_cases
    @property
    def constants(self): return self._constants
    @property
    def valid_mask(self): return self._valid_mask
    @property
    def validity(self): return self._validity
    @property
    def sdf(self): return self._sdf
    @property
    def N_valid(self): return self._N_valid
    @property
    def shape(self): return self._shape
    @property
    def N_cells(self): return self._N_cells

    @property
    def gradient(self): return self._gradient
    @gradient.setter
    def gradient(self, function):
        self._gradient = function

    def __call__(self, snap):
        if self._preload_all: return self._data_array[snap]
        else:
            if self._prev_snap != snap:
                self.load_snapshot(snap)
            return self._data_array
        
    def load_snapshot(self, snap):
        field = self._available_fields[self._field_index]
        with h5py.File(self._chosen_case, "r") as file:
            if self._field_index < 3:
                self._data_array = file["fields"][self._field_index][snap].astype(np.float32)
            else:
                match field:
                    case "|U|":
                        Ux = file["fields"][1][snap]
                        Uy = file["fields"][2][snap]
                        self._data_array = np.sqrt(Ux**2 + Uy**2).astype(np.float32)
                    case "Valid mask":
                        self._data_array = self._valid_mask.astype(np.float32)
                    case "Validity":
                        self._data_array = self._validity.astype(np.float32)
                    case "SDF":
                        self._data_array = self._sdf.astype(np.float32)
                    case _:
                        raise ValueError(f"Unknown field: {self._field}")
        self._min_value = np.nanmin(self._data_array)
        self._max_value = np.nanmax(self._data_array)
        self._prev_snap = snap

    def load_case(self, case_id, field_index, preload_all): # field and case specific data
        self._prev_snap = None
        self._preload_all = preload_all
        self._chosen_case = self._cases[case_id]
        self._field_index = field_index

        field = self._available_fields[self._field_index]
        with h5py.File(self._chosen_case, "r") as file:
            self._runtime = file.attrs.get("runtime", np.nan) / 60.0

            self._nu = file.attrs['nu']
            
            self._time = file['t'][:].astype(np.float32)
            self._N_snapshots = self._time.shape[0]
            
            if self._preload_all:
                if self._field_index < 3:
                    self._data_array = file["fields"][self._field_index][:].astype(np.float32)
                else:
                    match field:
                        case "|U|":
                            Ux = file["fields"][1][:]
                            Uy = file["fields"][2][:]
                            self._data_array = np.sqrt(Ux**2 + Uy**2).astype(np.float32)
                        case _:
                            raise ValueError(f"Unknown field: {self._field}")
                self._min_value = np.nanmin(self._data_array)
                self._max_value = np.nanmax(self._data_array)

        self._Re = self._constants["Uc"] * self._constants["Lc"] / self._nu
        self._size_MB = self._chosen_case.stat().st_size / (1024**2)

    @property
    def min_value(self): return self._min_value
    @property
    def max_value(self): return self._max_value
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
        self._available_fields = ["p", "|grad(p)|", "Ux", "Uy", "|U|", "curl(U)|z"]
        self._field_units = {"p": "m^2/s^2", "|grad(p)|": "m/s^2", "Ux": "m/s", "Uy": "m/s", "|U|": "m/s", "curl(U)|z": "1/s"}

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
        self._name = self._dataset_path.stem

        self._cases = sorted([file for file in self._dataset_path.iterdir() if file.suffix == ".h5" and file.stem != "constants"], key=lambda x: float(x.stem))
        self._N_cases = len(self._cases)

        with h5py.File(self._dataset_path / "constants.h5", "r") as file:
            self._mesh_centers = file["centers"][:].astype(np.float32)
            self._mesh_vertices = file["vertices"][:].astype(np.float32)
            self._mesh_indices = file["indices"][:].astype(np.uint32)
            self._Lc = file.attrs['Lc']
            self._Uc = file.attrs['Uc']

        self._N_cells = len(self._mesh_centers)
        self._N_vertices = len(self._mesh_vertices)

    @property
    def cases(self): return self._cases
    @property
    def N_cases(self): return self._N_cases
    @property
    def name(self): return self._name

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

    def __call__(self, snap):
        if self._preload_all: return self._data_array[snap]
        else:
            if self._prev_snap != snap:
                self.load_snapshot(snap)
            return self._data_array

    def load_snapshot(self, snap):
        with h5py.File(self._chosen_case, "r") as file:
            match self._field:
                case "p":
                    self._data_array = file['p'][snap, :].astype(np.float32)
                case "|grad(p)|":
                    self._data_array = np.empty((self._N_cells), dtype=np.float32)
                    p_grad = self._gradient(file['p'][snap, :])
                    self._data_array = np.sqrt(p_grad[0]**2 + p_grad[1]**2)
                case "Ux":
                    self._data_array = file['Ux'][snap, :].astype(np.float32)
                case "Uy":
                    self._data_array = file['Uy'][snap, :].astype(np.float32)
                case "|U|":
                    self._data_array = np.sqrt(file['Ux'][snap, :]**2 + file['Uy'][snap, :]**2).astype(np.float32)
                case "curl(U)|z":
                    self._data_array = np.empty((self._N_cells), dtype=np.float32)
                    U_grad = self._gradient(file['Ux'][snap, :])
                    V_grad = self._gradient(file['Uy'][snap, :])
                    self._data_array = V_grad[0] - U_grad[1]
                case _:
                    raise ValueError(f"Unknown field: {self._field}")
            self._min_value = np.min(self._data_array)
            self._max_value = np.max(self._data_array)
            self._prev_snap = snap

    def load_case(self, case_id, field_index, preload_all): # field and case specific data
        self._prev_snap = None
        self._preload_all = preload_all
        self._chosen_case = self._cases[case_id]
        self._field = self._available_fields[field_index]   # i.e., "p", "Ux", "Uy", "|U|"...

        with h5py.File(self._chosen_case, "r") as file:
            self._runtime = file.attrs.get("runtime", np.nan) / 60.0

            self._nu = file.attrs['nu']
            
            self._time = file['t'][:].astype(np.float32)
            self._N_snapshots = self._time.shape[0]

            if self._preload_all:
                match self._field:
                    case "p":
                        self._data_array = file['p'][:, :].astype(np.float32)
                    case "|grad(p)|":
                        self._data_array = np.empty((self._N_snapshots, self._N_cells), dtype=np.float32)
                        for snap in range(self._N_snapshots):
                            p_grad = self._gradient(file['p'][snap, :])
                            self._data_array[snap] = np.sqrt(p_grad[0]**2 + p_grad[1]**2)
                    case "Ux":
                        self._data_array = file['Ux'][:, :].astype(np.float32)
                    case "Uy":
                        self._data_array = file['Uy'][:, :].astype(np.float32)
                    case "|U|":
                        self._data_array = np.sqrt(file['Ux'][:, :]**2 + file['Uy'][:, :]**2).astype(np.float32)
                    case "curl(U)|z":
                        self._data_array = np.empty((self._N_snapshots, self._N_cells), dtype=np.float32)
                        for snap in range(self._N_snapshots):
                            U_grad = self._gradient(file['Ux'][snap, :])
                            V_grad = self._gradient(file['Uy'][snap, :])
                            self._data_array[snap] = V_grad[0] - U_grad[1]
                    case _:
                        raise ValueError(f"Unknown field: {self._field}")
                self._min_value = np.min(self._data_array)
                self._max_value = np.max(self._data_array)
                
    
        self._Re = self._Uc * self._Lc / self._nu
        self._size_MB = self._chosen_case.stat().st_size / (1024**2)

    @property
    def min_value(self): return self._min_value
    @property
    def max_value(self): return self._max_value
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