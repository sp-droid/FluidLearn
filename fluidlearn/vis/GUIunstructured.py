#### IMPORTS
import logging
from pathlib import Path
from typing import Literal
from dataclasses import dataclass

import numpy as np
from scipy.spatial import Delaunay, cKDTree # type: ignore
import matplotlib.pyplot as plt

# Special
import fastplotlib as fpl
from fastplotlib.ui import EdgeWindow

# Local imports
import fluidlearn as fl
from fluidlearn.data import DataLoaderUnstructured
from fluidlearn.utils.colormap import Colormap
from fluidlearn.vis import MeshHighlighter2D, UIpanel

logger = logging.getLogger("fluidlearn")

@dataclass
class Controller:
    dataset: int = 0
    vertex_interpolation: bool = False
    case: int = 0
    flowfield: int = 4
    snapshot: int = 0
    precomputed: bool = False

    percase_cmap: bool = True
    cmap_logscale: bool = False
    cmap_reverse: bool = False
    cmap: int = 0

    clip_min: np.float32 = np.float32(0.0)
    clip_max: np.float32 = np.float32(1.0)

class GUIUnstructured(EdgeWindow):
    def __init__(self,
            figure,
            size: int=275,
            location: Literal['bottom', 'right', 'top'] = "right", 
            title: str="CFD Visualizer",
            data_location=Path.cwd()
        ):
        EdgeWindow.__init__(self, figure=figure, size=size, location=location, title=title, data_location=data_location)

        # Controller holds the state of the UI and user selections
        self._controller = Controller()

        # Data loading and processing
        self._data = DataLoaderUnstructured()
        self._data.explore_datasets(data_location)
        logger.debug(f"Available datasets: {self._data.available_datasets}")
        
        # Plotting
        self._plotter = Plotter(figure, self._controller, self._data)

        # Colormap
        self._cmap = Colormap()

        # Pipeline
        self._pipeline = Pipeline(self._data, self._controller, self._plotter, self._cmap)

        # Initial load
        self._pipeline._define_cmap()
        self._pipeline.update_dataset()

        # UI widgets
        self.sidebar = UIpanel(size=size, controller=self._controller, data=self._data, pipeline=self._pipeline, cmap=self._cmap)

    def update(self):
        self.sidebar.UI_dataset()
        self.sidebar.UI_mesh()
        self.sidebar.UI_cmap()
        self.sidebar.UI_flowdata()
        self.sidebar.UI_case()
        self.sidebar.UI_snapshot()
        self.sidebar.UI_highlighter()

class Plotter:
    def __init__(self, figure, controller, data):
        self._figure = figure
        self._controller = controller
        self._data = data

    @property
    def figure(self): return self._figure

    def plot_mesh(self):
        # Per-vertex or per-face coloring
        if hasattr(self, "_mesh"):
            self._figure[0, 0].remove_graphic(self._mesh)
        if self._controller.vertex_interpolation:
            triangulation = Delaunay(self._data.mesh_centers[:, :2])  # Use x,y coords only
            self._triangles = triangulation.simplices.astype(np.uint32)
            
            self._mesh = self._figure[0, 0].add_mesh(
                self._data.mesh_centers,
                self._triangles,
                colors=self._random_colors,
                mode="basic" # lighting mode, just ambient light. Default is "phong"
            )
        else: # Random colors for visualizing each cell
            self._random_colors = np.random.rand(self._data.N_cells, 4).astype(np.float32)
            self._mesh = self._figure[0, 0].add_mesh(
                self._data.mesh_vertices,
                self._data.mesh_indices,
                colors=self._random_colors,
                mode="basic"
            )

        # Reset camera to fit the new mesh
        self._figure[0,0].camera.show_object(self._mesh.world_object)
        self._figure[0,0].camera.zoom = 1.2

    @property
    def mesh(self): return self._mesh
    @property
    def random_colors(self): return self._random_colors

class Pipeline:
    def __init__(self, _data, _controller, _plotter, _cmap):
        self._data = _data
        self._controller = _controller
        self._plotter = _plotter
        self._cmap = _cmap

    def update_dataset(self):
        self._data.load_dataset(self._controller.dataset)
        self.update_mesh()

    def update_mesh(self):
        logger.debug("Loading mesh...")
        self._data.load_mesh()
        logger.debug("Mesh loaded. Plotting mesh...")
        self._plotter.plot_mesh()
        logger.debug("Mesh plotted. Precomputing gradient and neighbors...")
        self._precompute_gradient()
        logger.debug("Gradient and neighbors computed.")

        self._cell_kdtree = cKDTree(self._data.mesh_centers[:, :2]) # KD tree for fast nearest cell lookup during highlighting
        logger.debug("KDTree built for cell centers.")
        self._highlighter = MeshHighlighter2D(self, self._controller, self._plotter)

        self.update_case()

    def update_case(self):
        self._data.load_case(self._controller.case, self._controller.flowfield)
        self._update_data_range()
        self._load_snapshot()


    def _precompute_gradient(self):
        # Find cells connected to each vertex
        vertex_connections, vertex_connections_mask = fl.utils.cells_per_vertex(self._data.mesh_indices, self._data.mesh_vertices.shape[0])
        logger.debug("Vertex connections computed.")
        # Find neighboring cells for each cell
        self._cell_neighbors, self._cell_neighbors_mask = fl.utils.neighbors_per_cell(self._data.mesh_indices, vertex_connections, vertex_connections_mask)
        logger.debug("Cell neighbors computed.")
        # Precompute least squares weights for gradient computation
        self._lsq_weights = fl.utils.unstructured_lsq_weights(self._data.mesh_centers, self._cell_neighbors, self._cell_neighbors_mask)
        logger.debug("Least squares weights computed.")
        # Gradient function
        self._data.gradient = lambda field: fl.utils.unstructured_gradient(
            field, 
            precomputed_weights=self._lsq_weights, 
            cell_neighbors=self._cell_neighbors, 
            cell_neighbors_mask=self._cell_neighbors_mask
        )

    def _update_data_range(self):
        if self._controller.percase_cmap: data_array = self._data.data_array.flatten()
        else: data_array = self._data.data_array[self._controller.snapshot]

        self._data_min = np.min(data_array)
        self._controller.clip_min = self._data_min 
        self._data_max = np.max(data_array)
        self._controller.clip_max = self._data_max

    def _load_snapshot(self):
        data_array = self._data.data_array[self._controller.snapshot]
        data_array = np.clip(data_array, self._controller.clip_min, self._controller.clip_max)

        if self._cmap.available_cmaps[self._controller.cmap] == "random":
            self._plotter.mesh.colors = self._plotter.random_colors
        else:
            normalized = ((data_array - self._controller.clip_min) / (self._controller.clip_max - self._controller.clip_min) * (self._cmap.lut.shape[0]-1)).astype(np.uint32)
            self._plotter.mesh.colors = self._cmap.lut[normalized]

        self._time = self._data.time[self._controller.snapshot]

    def _precompute_fast_load_snapshot(self):
        if self._cmap.available_cmaps[self._controller.cmap] == "random": return
        self._fullcase = np.empty((self._data.N_snapshots, self._data.N_cells, 4), dtype=np.float32)
        for j in range(self._data.N_snapshots):
            data_array = self._data.data_array[j]
            data_array = np.clip(data_array, self._controller.clip_min, self._controller.clip_max)
            
            normalized = ((data_array - self._controller.clip_min) / (self._controller.clip_max - self._controller.clip_min) * (self._cmap.lut.shape[0]-1)).astype(np.uint32)
            self._fullcase[j] = self._cmap.lut[normalized]

    def _fast_load_snapshot(self):
        if self._cmap.available_cmaps[self._controller.cmap] == "random": return
        self._plotter.mesh.colors = self._fullcase[self._controller.snapshot]
        self._time = self._data.time[self._controller.snapshot]

    def _define_cmap(self): # Define colormap and its lookup table
        name = self._cmap.available_cmaps[self._controller.cmap]
        if name == "random": return
        self._cmap.set_cmap(name, reverse=self._controller.cmap_reverse)

        self._cmap.build_lut(logscale=self._controller.cmap_logscale, space="linear")



def gui_main(path=Path(r"data/01_raw")):
    figure = fpl.Figure(size=(1920, 1080))
    figure.canvas.set_title("FluidLearn - Unstructured CFD Visualizer")
    gui = GUIUnstructured(
        figure,
        data_location=path
    )
    figure.add_gui(gui) # type: ignore

    figure.show()
    figure.imgui_show_fps = True # type: ignore
    fpl.loop.run()

if __name__ == "__main__":
    logger.setLevel(level=logging.DEBUG)
    gui_main()