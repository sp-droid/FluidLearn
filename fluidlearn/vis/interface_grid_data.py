#### IMPORTS
import logging
from pathlib import Path
from typing import Literal
from dataclasses import dataclass

from matplotlib import image
import numpy as np
from scipy.spatial import Delaunay, cKDTree

# Special
import fastplotlib as fpl
from fastplotlib.ui import EdgeWindow

# Local imports
import fluidlearn as fl
from fluidlearn.data import DataLoaderGrid
from fluidlearn.utils.colormap import Colormap
from fluidlearn.vis import GridCellHighlighter2D, UIpanels

logger = logging.getLogger("fluidlearn")

@dataclass
class Controller:
    dataset: int = 0
    case_id: int = 0
    field: int = 3
    snapshot: int = 0
    precomputed: bool = False

    cmap_all_snaps: bool = True
    cmap_logscale: bool = False
    cmap_reverse: bool = False
    cmap: int = 0

    clip_min: np.float32 = np.float32(0.0)
    clip_max: np.float32 = np.float32(1.0)

class InterfaceGridData(EdgeWindow):
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
        self._data = DataLoaderGrid()
        self._data.explore_datasets(data_location)
        logger.debug(f"Available datasets: {self._data.available_datasets}")
        self._controller.dataset = next((i for i, x in enumerate(self._data.available_datasets) if x == "test_TGV"), 0)
        
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
        self.sidebar = UIpanels(size=size, controller=self._controller, data=self._data, pipeline=self._pipeline, cmap=self._cmap)

    def update(self):
        self.sidebar.UI_dataset()
        self.sidebar.UI_grid()
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

    def plot_image(self):
        # Random colors for visualizing each cell
        self._random_colors = np.random.rand(self._data.shape[0], self._data.shape[1], 3).astype(np.float32)
        self._random_colors = np.concatenate([self._random_colors, self._data.validity[:,:,np.newaxis]], axis=-1)

        if hasattr(self, "_image"):
            self._figure[0, 0].remove_graphic(self._image)

        self._image = self._figure[0, 0].add_image(
            data=self._random_colors
        )

        # Image orientation correction
        angle = np.deg2rad(-90)
        rotation_quat = (np.cos(angle / 2), np.sin(angle / 2), 0, 0)
        self._image.rotation = rotation_quat
        self._figure[0,0].camera.local.scale_x = -1

        self._figure[0,0].camera.show_object(self._image.world_object)
        self._figure[0,0].camera.zoom = 1.2

    @property
    def data(self): return self._image.data
    @data.setter
    def data(self, new_data): 
        self._image.data[self._data.valid_mask, :3] = new_data
    
    def random_colors(self):
        self._image.data = self._random_colors

class Pipeline:
    def __init__(self, _data, _controller, _plotter, _cmap):
        self._data = _data
        self._controller = _controller
        self._plotter = _plotter
        self._cmap = _cmap

    def update_dataset(self):
        self._data.load_dataset(self._controller.dataset)

        self.update_case()

    def update_case(self):
        logger.debug(f"Loading case {self._controller.case_id} from dataset {self._controller.dataset}...")
        field = self._data.available_fields[self._controller.field]
        if field in ["Valid mask", "Validity", "SDF"]: self._controller.cmap_all_snaps = False

        self._data.load_case(
            case_id = self._controller.case_id,
            field_index = self._controller.field,
            preload_all = self._controller.cmap_all_snaps
        )
        self._plotter.plot_image()
        
        self._highlighter = GridCellHighlighter2D(self._controller, self._plotter, self._data, self._plotter._image)

        self._reset_cmap = True
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
        logger.debug(f"Updating data range for colormap: min={self._data.min_value}, max={self._data.max_value}")
        self._controller.clip_min = self._data.min_value
        self._controller.clip_max = self._data.max_value
        self._reset_cmap = False

    def _load_snapshot(self):
        data_array = self._data(self._controller.snapshot)[self._data.valid_mask]
        if self._reset_cmap: self._update_data_range()
        data_array = np.clip(data_array, self._controller.clip_min, self._controller.clip_max)

        if self._cmap.available_cmaps[self._controller.cmap] == "random":
            self._plotter.random_colors()
        else:
            if self._controller.clip_min == self._controller.clip_max: normalized = np.zeros_like(data_array, dtype=np.uint32)
            else: normalized = ((data_array - self._controller.clip_min) / (self._controller.clip_max - self._controller.clip_min) * (self._cmap.lut.shape[0]-1)).astype(np.uint32)
            self._plotter.data = self._cmap.lut[normalized]

        self._time = self._data.time[self._controller.snapshot]
        self._controller.precomputed = False

    def _precompute_fast_load_snapshot(self):
        if self._cmap.available_cmaps[self._controller.cmap] == "random" or self._controller.precomputed: return
        logger.debug("Precomputing snapshots for fast loading...")

        self._fullcase = np.empty((self._data.N_snapshots, self._data.N_valid, 3), dtype=np.float32)
        for j in range(self._data.N_snapshots):
            data_array = self._data(j)[self._data.valid_mask]
            data_array = np.clip(data_array, self._controller.clip_min, self._controller.clip_max)
            
            if self._controller.clip_min == self._controller.clip_max: normalized = np.zeros_like(data_array, dtype=np.uint32)
            else: normalized = ((data_array - self._controller.clip_min) / (self._controller.clip_max - self._controller.clip_min) * (self._cmap.lut.shape[0]-1)).astype(np.uint32)
            self._fullcase[j] = self._cmap.lut[normalized]
        self._controller.precomputed = True

    def _fast_load_snapshot(self):
        if self._cmap.available_cmaps[self._controller.cmap] == "random": return
        self._plotter.data = self._fullcase[self._controller.snapshot]
        self._time = self._data.time[self._controller.snapshot]

    def _define_cmap(self): # Define colormap and its lookup table
        name = self._cmap.available_cmaps[self._controller.cmap]
        if name == "random": return
        self._cmap.set_cmap(name, reverse=self._controller.cmap_reverse)

        self._cmap.build_lut(logscale=self._controller.cmap_logscale, space="sRGB")

def gui_main(path=Path(r"data/02_sampled")):
    figure = fpl.Figure(size=(1920, 1080))
    figure.canvas.set_title("FluidLearn - Grid Data Interface")
    gui = InterfaceGridData(
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