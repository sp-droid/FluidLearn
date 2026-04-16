#### IMPORTS
from pathlib import Path

import numpy as np
from scipy.spatial import Delaunay, cKDTree
import matplotlib.pyplot as plt

# Special
import fastplotlib as fpl
from fastplotlib.ui import EdgeWindow

# Local imports
import fluidlearn as fl

class CFDvisualizerUnstructured(fl.vis.UIpanel, EdgeWindow):
    def __init__(self, figure, size, location, title, data_location=Path.cwd()):
        super().__init__(figure=figure, size=size, location=location, title=title, data_location=data_location)
        
        self._width = size
        self._figure = figure

        self._case = 0
        self._snapshot = 0
        self._use_vertex_interpolation = False

        self._data = fl.data.DataLoaderUnstructured()
        self._data.explore_datasets(data_location)
        
        self._dataset_index = 0

        self._available_cmaps = ["jet", "random", "hsv", "viridis", "plasma", "inferno", "magma", "cividis", "turbo", "coolwarm", "RdBu", "twilight"]
        self._use_percase_cmap = True
        self._cmap_logscale = False
        self._cmap_index = 0
        self._N_colors = 300
        self._define_cmap()

        
        self._flowfield_index = 3

        self._colorbar_N_rects = 60
        self._prebuild_colorbar_texture()

        self._pipeline_update_dataset()

    def _pipeline_update_dataset(self):
        self._data.load_dataset(self._dataset_index)
        self._pipeline_update_mesh()

    def _pipeline_update_mesh(self):
        self._data.load_mesh()
        self._plot_mesh()
        self._precompute_gradient()
        
        # KD tree for fast nearest cell lookup during highlighting
        self._cell_kdtree = cKDTree(self._data.mesh_centers[:, :2])
        self._highlighter = fl.vis.MeshHighlighter2D(self)

        self._pipeline_update_case()

    def _pipeline_update_case(self):
        self._data.load_case(self._case, self._flowfield_index)
        self._update_cmap_range()
        self._load_snapshot()

    def _precompute_gradient(self):
        # Find cells connected to each vertex
        vertex_connections, vertex_connections_mask = fl.utils.cells_per_vertex(self._data.mesh_indices, self._data.mesh_vertices.shape[0])
        # Find neighboring cells for each cell
        self._cell_neighbors, self._cell_neighbors_mask = fl.utils.neighbors_per_cell(self._data.mesh_indices, vertex_connections, vertex_connections_mask)
        # Precompute least squares weights for gradient computation
        self._lsq_weights = fl.utils.unstructured_lsq_weights(self._data.mesh_centers, self._cell_neighbors, self._cell_neighbors_mask)
        # Gradient function
        self._data.gradient = lambda field: fl.utils.unstructured_gradient(
            field, 
            precomputed_weights=self._lsq_weights, 
            cell_neighbors=self._cell_neighbors, 
            cell_neighbors_mask=self._cell_neighbors_mask
        )

    def _plot_mesh(self):
        # Random colors for visualizing each cell
        self._random_colors = np.random.rand(self._data.N_cells, 4).astype(np.float32)
        # Per-vertex or per-face coloring
        if hasattr(self, "_mesh"):
            self._figure[0, 0].remove_graphic(self._mesh)
        if self._use_vertex_interpolation:
            triangulation = Delaunay(self._data.mesh_centers[:, :2])  # Use x,y coords only
            self._triangles = triangulation.simplices.astype(np.uint32)
            
            mesh_min, mesh_max = np.min(self._data.mesh_centers, axis=0), np.max(self._data.mesh_centers, axis=0)
            self._mesh = self._figure[0, 0].add_mesh(
                self._data.mesh_centers,
                self._triangles,
                colors=self._random_colors,
                mode="basic" # lighting mode, just ambient light. Default is "phong"
            )
        else:
            mesh_min, mesh_max = np.min(self._data.mesh_vertices, axis=0), np.max(self._data.mesh_vertices, axis=0)
            self._mesh = self._figure[0, 0].add_mesh(
                self._data.mesh_vertices,
                self._data.mesh_indices,
                colors=self._random_colors,
                mode="basic"
            )

        self._figure[0,0].camera.show_object(self._mesh.world_object)
        self._figure[0,0].camera.zoom = 1.2

    def _load_snapshot(self):
        data_array = self._data.data_array[self._snapshot]
        data_array = np.clip(data_array, self._clip_min, self._clip_max)

        normalized = ((data_array - self._clip_min) / (self._clip_max - self._clip_min) * (self._N_colors-1)).astype(np.uint32)
        
        if self._cmap == "random":
            self._mesh.colors = self._random_colors
        else:
            self._mesh.colors = self._cmap_lut[normalized]
        self._t = self._data.time[self._snapshot]

    def _precompute_fast_load_snapshot(self):
        if self._cmap == "random": return
        self._fullcase = np.empty((self._data.N_snapshots, self._data.N_cells, 4), dtype=np.float32)
        for j in range(self._data.N_snapshots):
            data_array = self._data.data_array[j]
            data_array = np.clip(data_array, self._clip_min, self._clip_max)
            
            normalized = ((data_array - self._clip_min) / (self._clip_max - self._clip_min) * (self._N_colors-1)).astype(np.uint32)
            self._fullcase[j] = self._cmap_lut[normalized]

    def _fast_load_snapshot(self):
        if self._cmap == "random": return
        self._mesh.colors = self._fullcase[self._snapshot]
        self._t = self._data.time[self._snapshot]

    def _define_cmap(self): # Define colormap and its lookup table
        self._cmap = self._available_cmaps[self._cmap_index]
        if self._cmap == "random": return
        self._cmap_function = plt.colormaps[self._cmap]

        # Create a lookup table for the colormap with N_colors entries. In sRGB space, so values are in [0, 1]
        if self._cmap_logscale:
            self._cmap_lut = np.array([self._cmap_function(np.log10(i)/(np.log10(self._N_colors))) for i in range(1,self._N_colors+1)]).astype(np.float32)
        else:
            self._cmap_lut = np.array([self._cmap_function(i/(self._N_colors-1)) for i in range(self._N_colors)]).astype(np.float32)
        
        self._cmap_lut[:, :3] = fl.utils.srgb_to_linear(self._cmap_lut[:, :3])  # Convert sRGB to linear space for correct interpolation

    def _update_cmap_range(self):
        if self._use_percase_cmap: data_array = self._data.data_array.flatten()
        else: data_array = self._data.data_array[self._snapshot]

        self._data_min = np.min(data_array)
        self._clip_min = self._data_min 
        self._data_max = np.max(data_array)
        self._clip_max = self._data_max

    def _prebuild_colorbar_texture(self):
        """Build colorbar texture once and cache it"""
        if self._cmap == "random": return
        self._colorbar_packed_color = np.zeros((self._colorbar_N_rects,), dtype=np.uint32)
           
        # Get indices for evenly spaced colors across the colormap
        indices = (np.arange(self._colorbar_N_rects) * (self._N_colors - 1) // self._colorbar_N_rects).astype(np.uint32)
        # Get the colors from the LUT
        colors = self._cmap_lut[indices]  # colors are already in [0, 1] range
        # Convert to 0-255 range and pack as ABGR
        colors = (colors * 255).astype(np.uint32)
        self._colorbar_packed_color = (colors[:,3] << 24) | (colors[:,2] << 16) | (colors[:,1] << 8) | colors[:,0]

    def update(self):
        self.UI_dataset(self._dataset_index, self._data.available_datasets, self._case, self._snapshot, self._pipeline_update_dataset, self._data.constants)
        self.UI_mesh()
        self.UI_cmap()
        self.UI_flowdata()
        self.UI_case()
        self.UI_snapshot()
        self.UI_highlighter()

# Plotting
figure = fpl.Figure(size=(1920, 1080))
figure.canvas.set_title("CFD Visualizer")

gui = CFDvisualizerUnstructured(
    figure,  # the figure this GUI instance should live inside
    size=275,  # width or height of the GUI window within the figure
    location="right",  # the edge to place this window at
    title="CFD Visualizer",  # window title
    data_location=Path(r"data/01_raw")
)
figure.add_gui(gui)

figure.show()
figure.imgui_show_fps = True

if __name__ == "__main__":
    fpl.loop.run()