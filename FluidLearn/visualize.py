#### IMPORTS
import json
from time import time
from pathlib import Path

import h5py
import numpy as np
from numba import jit
from scipy import io
from scipy.spatial import Delaunay, cKDTree
import matplotlib.pyplot as plt

# Special
import fastplotlib as fpl
from fastplotlib.ui import EdgeWindow
from imgui_bundle import imgui

# Plotting
figure = fpl.Figure(size=(1920, 1080))
figure.canvas.set_title("CFD Visualization")

@jit
def compute_most_repeated(
        arr: np.ndarray
    ) -> int:
    """Find most repeated element in an array

    Args:
        arr (np.ndarray): Input array

    Returns:
        any: Most repeated element
        int: Count of the most repeated element
    """    
    sorted_arr = np.sort(arr)
    max_count = 1
    current_count = 1
    element = sorted_arr[0]
    for i in range(1, len(sorted_arr)):
        if sorted_arr[i] == sorted_arr[i-1]:
            current_count += 1
            if current_count > max_count:
                element = sorted_arr[i]
                max_count = current_count
        else:
            current_count = 1
    
    return element, max_count

def compute_cells_per_vertex(
        mesh_indices: np.ndarray,
        N_vertices: int
    ) -> tuple:
    """To which cells belongs each vertex

    Args:
        mesh_indices (np.ndarray): Array giving which vertices belong to each cell
        N_vertices (int): Total number of vertices

    Returns:
        np.ndarray: Array of which cells belongs to each vertex
        np.ndarray: Mask indicating valid connections
    """
    N_cells = mesh_indices.shape[0]
    _, max_connections = compute_most_repeated(mesh_indices.flatten())

    vertex_connections = np.empty((N_vertices,max_connections), dtype=int)
    vertex_connections_mask = np.zeros((N_vertices,max_connections), dtype=bool)

    for cell in range(N_cells):
        for vertex in mesh_indices[cell]:
            for i in range(max_connections):
                if not vertex_connections_mask[vertex, i]:
                    vertex_connections[vertex, i] = cell
                    vertex_connections_mask[vertex, i] = True
                    break

    return vertex_connections, vertex_connections_mask

def compute_cell_neighbors(
        mesh_indices: np.ndarray,
        vertex_connections: list,
        vertex_connections_mask: np.ndarray
    ) -> tuple:
    """Which cells are neighbors of each cell

    Args:
        mesh_indices (np.ndarray): Array giving which vertices belong to each cell
        vertex_connections (list): List of which cells belongs to each vertex
        vertex_connections_mask (np.ndarray): Mask indicating valid connections

    Returns:
        np.ndarray: Array of which cells are neighbors of each cell
        np.ndarray: Mask indicating valid neighbors
    """
    N_cells = mesh_indices.shape[0]
    # Assuming a valid manifold mesh, the maximum number of neighboring faces is the number of vertices, because in this mesh an edge may only be shared by <=2 faces
    max_neighbors = mesh_indices.shape[1]

    cell_neighbors = np.empty((N_cells,max_neighbors), dtype=int)
    cell_neighbors_mask = np.zeros((N_cells,max_neighbors), dtype=bool)
    for cell in range(N_cells):
        for i in mesh_indices[cell]:
            vertex_con = vertex_connections[i]
            vertex_con = vertex_con[vertex_connections_mask[i]]
            if len(vertex_con)==0: continue
            vertex_con = vertex_con[vertex_con!=cell]
            if len(vertex_con)==0: continue
            for candidate_cell in vertex_con:
                if len(set(mesh_indices[cell]) & set(mesh_indices[candidate_cell])) > 1:
                    if candidate_cell not in cell_neighbors[cell]:
                        cell_neighbors[cell,np.where(cell_neighbors_mask[cell]==False)[0][0]] = candidate_cell
                        cell_neighbors_mask[cell,np.where(cell_neighbors_mask[cell]==False)[0][0]] = True
                        cell_neighbors[candidate_cell,np.where(cell_neighbors_mask[candidate_cell]==False)[0][0]] = cell
                        cell_neighbors_mask[candidate_cell,np.where(cell_neighbors_mask[candidate_cell]==False)[0][0]] = True
        
    return cell_neighbors, cell_neighbors_mask

def compute_gradient_weights(
        mesh_centers: np.ndarray,
        cell_neighbors: np.ndarray,
        cell_neighbors_mask: np.ndarray
    ) -> tuple:
    """Precompute least squares weights for gradient computation

    Args:
        mesh_centers (np.ndarray): Array of cell centroids
        cell_neighbors (np.ndarray): Array of which cells are neighbors of each cell
        cell_neighbors_mask (np.ndarray): Mask indicating valid neighbors

    Returns:
        np.ndarray: Precomputed weights for x-gradient
        np.ndarray: Precomputed weights for y-gradient
    """
    N_cells = mesh_centers.shape[0]
    max_neighbors = cell_neighbors.shape[1]

    gradX_lsq_weights = np.empty((N_cells,max_neighbors), dtype=np.float32)
    gradY_lsq_weights = np.empty((N_cells,max_neighbors), dtype=np.float32)
    for cell in range(N_cells):
        neighbors = cell_neighbors_mask[cell]

        A = (mesh_centers[cell_neighbors[cell, neighbors]]-mesh_centers[cell])
        A = np.linalg.inv((A.T @ A) + 1e-8*np.eye(A.shape[1])) @ A.T
        
        gradX_lsq_weights[cell, neighbors] = A[0]
        gradY_lsq_weights[cell, neighbors] = A[1]

    return gradX_lsq_weights, gradY_lsq_weights

@jit
def compute_gradients(field, precomputed_weight, cell_neighbors, cell_neighbors_mask):
    N_cells = cell_neighbors.shape[0]
    field_grad = np.zeros(N_cells, dtype=np.float32)
    
    for cell in range(N_cells):
        for i, neighbor in enumerate(cell_neighbors[cell]):
            if cell_neighbors_mask[cell, i]:
                field_grad[cell] += precomputed_weight[cell, i] * (field[neighbor] - field[cell])
    return field_grad

def srgb_to_linear(rgb):
    rgb = np.asarray(rgb, dtype=np.float32)
    return np.where(
        rgb <= 0.04045,
        rgb / 12.92,
        ((rgb + 0.055) / 1.055) ** 2.4
    )

class ImguiEdgeWindow(EdgeWindow):
    def __init__(self, figure, size, location, title, data_location=Path.cwd()):
        super().__init__(figure=figure, size=size, location=location, title=title, data_location=data_location)
        # this UI will modify the line
        self._figure = figure
        self._case = 0
        self._snapshot = 0
        self._use_vertex_interpolation = False

        self._data_location = data_location
        self._available_datasets = [folder.stem for folder in self._data_location.iterdir() if folder.is_dir()]
        self._dataset_index = 0

        self._available_cmaps = ["jet", "random", "hsv", "viridis", "plasma", "inferno", "magma", "cividis", "turbo", "coolwarm", "RdBu", "twilight"]
        self._use_percase_cmap = True
        self._cmap_logscale = False
        self._cmap_index = 0
        self._N_colors = 300
        self._define_cmap()

        self._available_flowfields = ["Kinematic pressure", "Horizontal velocity", "Vertical velocity", "Velocity magnitude", "Vorticity"]
        self._flowfield_units = ["m^2/s^2", "m/s", "m/s", "m/s", "1/s"]
        self._flowfield_index = 3

        self._colorbar_size = (250, 20)  # width, height of colorbar
        self._colorbar_N_rects = 60
        self._prebuild_colorbar_texture()

        self._is_playing = False
        self._play_fps = 21
        self._frame_time = 1.0 / self._play_fps
        self._last_frame_time = 0.0

        self._is_highlighting = False
        self._highlight_color = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)

        self._load_dataset()

    def _load_dataset(self):
        self._dataset_path = self._data_location / self._available_datasets[self._dataset_index]

        self._cases = sorted([file for file in self._dataset_path.iterdir() if file.suffix == ".h5" and file.stem != "mesh"], key=lambda x: float(x.stem))
        self._N_cases = len(self._cases)

        with open(self._dataset_path / "constants.json", "r") as file:
            self._constants = json.load(file)

        self._load_mesh()

    def _load_mesh(self):
        with h5py.File(self._dataset_path / "mesh.h5", "r") as file:
            self._mesh_centers = file["centroids"][:].astype(np.float32)
            self._mesh_vertices = file["vertices"][:].astype(np.float32)
            self._mesh_indices = file["indices"][:].astype(np.uint32)

        self._N_cells = len(self._mesh_centers)
        self._N_vertices = len(self._mesh_vertices)

        # Find cells connected to each vertex
        vertex_connections, vertex_connections_mask = compute_cells_per_vertex(self._mesh_indices, self._N_vertices)
        # Find neighboring cells for each cell
        self._cell_neighbors, self._cell_neighbors_mask = compute_cell_neighbors(self._mesh_indices, vertex_connections, vertex_connections_mask)
        # Precompute least squares weights for gradient computation
        self._gradX_lsq_weights, self._gradY_lsq_weights = compute_gradient_weights(self._mesh_centers, self._cell_neighbors, self._cell_neighbors_mask)
        
        # Random colors for visualizing each cell
        self._random_colors = np.random.rand(self._N_cells, 4).astype(np.float32)
        # Per-vertex or per-face coloring
        if hasattr(self, "_mesh"):
            self._figure[0, 0].remove_graphic(self._mesh)
        if self._use_vertex_interpolation:
            triangulation = Delaunay(self._mesh_centers[:, :2])  # Use x,y coords only
            self._triangles = triangulation.simplices.astype(np.uint32)
            
            mesh_min, mesh_max = np.min(self._mesh_centers, axis=0), np.max(self._mesh_centers, axis=0)
            self._mesh = self._figure[0, 0].add_mesh(
                self._mesh_centers,
                self._triangles,
                colors=self._random_colors,
                mode="basic" # lighting mode, just ambient light. Default is "phong"
            )
        else:
            mesh_min, mesh_max = np.min(self._mesh_vertices, axis=0), np.max(self._mesh_vertices, axis=0)
            self._mesh = self._figure[0, 0].add_mesh(
                self._mesh_vertices,
                self._mesh_indices,
                colors=self._random_colors,
                mode="basic"
            )

        self._figure[0,0].camera.show_object(self._mesh.world_object)
        self._figure[0,0].camera.zoom = 1.2

        self._cell_kdtree = cKDTree(self._mesh_centers[:, :2])
        self._highlighted_cell = -1
        self._highlighted_cell_original_color = None
        self._highlighted_flowvalue = 0.0
        
        self._mesh.add_event_handler(self.on_pointer_move, "pointer_move")

        self._load_case()

    def on_pointer_move(self, event):
        # event.position is in WORLD coordinates
        data_pos = self._figure[0,0].map_screen_to_world(event)

        if data_pos is not None:
            x, y, _ = data_pos
            # print(f"x={x:.3f}, y={y:.3f}")

            # Get closest cell to pointer position using prebuilt cKDTree
            _, cell_index = self._cell_kdtree.query([x, y])
            if self._highlighted_cell != -1:
                self._mesh.colors[self._highlighted_cell] = self._highlighted_cell_original_color
            
            self._highlighted_cell = cell_index
            self._highlighted_cell_original_color = self._mesh.colors[cell_index].copy()

            self._mesh.colors[cell_index] = self._highlight_color
            self._highlighted_flowvalue = self._data_array[self._snapshot, cell_index]

    def _load_case(self): # Flowfield and case specific data
        chosen_case = self._cases[self._case]
        flowfield = self._available_flowfields[self._flowfield_index]   # i.e., "p", "Ux", "Uy", "|U|"...

        self._data = {}
        with h5py.File(chosen_case, "r") as file:
            self._data["nu"] = file.attrs['nu']
            self._data["t"] = file['t'][:].astype(np.float32)
            self._N_snapshots = self._data["t"].shape[0]
            match flowfield:
                case "Kinematic pressure":
                    self._data_array = file['p'][:, :].astype(np.float32)
                case "Horizontal velocity":
                    self._data_array = file['U'][:, :, 0].astype(np.float32)
                case "Vertical velocity":
                    self._data_array = file['U'][:, :, 1].astype(np.float32)
                case "Velocity magnitude":
                    self._data_array = np.sqrt(file['U'][:, :, 0]**2 + file['U'][:, :, 1]**2).astype(np.float32)
                case "Vorticity":
                    self._data_array = np.empty((self._N_snapshots, self._N_cells), dtype=np.float32)
                    for snap in range(self._N_snapshots):
                        U_gradY = compute_gradients(file['U'][snap, :, 0], self._gradY_lsq_weights, self._cell_neighbors, self._cell_neighbors_mask)
                        V_gradX = compute_gradients(file['U'][snap, :, 1], self._gradX_lsq_weights, self._cell_neighbors, self._cell_neighbors_mask)
                        self._data_array[snap] = V_gradX - U_gradY
    
        self._Re = self._constants["Uc"] * self._constants["Lc"] / self._data["nu"] 
        self._update_cmap_range()
        self._update_mesh_snapshot()

    def _update_mesh_snapshot(self):
        data_array = self._data_array[self._snapshot]
        data_array = np.clip(data_array, self._clip_min, self._clip_max)

        normalized = ((data_array - self._clip_min) / (self._clip_max - self._clip_min) * (self._N_colors-1)).astype(np.uint32)
        
        if self._cmap == "random":
            self._mesh.colors = self._random_colors
        else:
            self._mesh.colors = self._cmap_lut[normalized]
        self._t = self._data["t"][self._snapshot]

    def _precompute_fast_update_mesh_snapshot(self):
        if self._cmap == "random": return
        self._fullcase = np.empty((self._N_snapshots, self._N_cells, 4), dtype=np.float32)
        for j in range(self._N_snapshots):
            data_array = self._data_array[j]
            data_array = np.clip(data_array, self._clip_min, self._clip_max)
            
            normalized = ((data_array - self._clip_min) / (self._clip_max - self._clip_min) * (self._N_colors-1)).astype(np.uint32)
            self._fullcase[j] = self._cmap_lut[normalized]

    def _fast_update_mesh_snapshot(self):
        if self._cmap == "random": return
        self._mesh.colors = self._fullcase[self._snapshot]
        self._t = self._data["t"][self._snapshot]

    def _define_cmap(self): # Define colormap and its lookup table
        self._cmap = self._available_cmaps[self._cmap_index]
        if self._cmap == "random": return
        self._cmap_function = plt.colormaps[self._cmap]

        # Create a lookup table for the colormap with N_colors entries. In sRGB space, so values are in [0, 1]
        if self._cmap_logscale:
            self._cmap_lut = np.array([self._cmap_function(np.log10(i)/(np.log10(self._N_colors))) for i in range(1,self._N_colors+1)]).astype(np.float32)
        else:
            self._cmap_lut = np.array([self._cmap_function(i/(self._N_colors-1)) for i in range(self._N_colors)]).astype(np.float32)
        
        self._cmap_lut[:, :3] = srgb_to_linear(self._cmap_lut[:, :3])  # Convert sRGB to linear space for correct interpolation

    def _update_cmap_range(self):
        if self._use_percase_cmap: data_array = self._data_array.flatten()
        else: data_array = self._data_array[self._snapshot]
        
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
        #### Dropdown for dataset selection
        imgui.text("Dataset properties")
        changed_dataset, self._dataset_index = imgui.combo(
            "Dataset",
            self._dataset_index,
            self._available_datasets
        )
        if changed_dataset:
            self._case = 0
            self._snapshot = 0
            self._load_dataset()
        for key, value in self._constants.items():
            imgui.text(f"{key}: {value}")
        imgui.separator()
        #### Mesh properties and mesh mode (vertex interpolation or face constant)
        imgui.text("Mesh")
        imgui.text(f"Cells: {self._N_cells}")
        imgui.text(f"Vertices: {self._N_vertices}")
        if imgui.button("Mesh Mode: Vertex Interpolation" if self._use_vertex_interpolation else "Mode: Face Constant"):
            self._use_vertex_interpolation = not self._use_vertex_interpolation
            self._load_mesh()
        imgui.separator()
        #### Dropdown for cmap selection
        changed_cmap, self._cmap_index = imgui.combo(
            "Colormap",
            self._cmap_index,
            self._available_cmaps
        )
        if changed_cmap:
            self._define_cmap()
            self._prebuild_colorbar_texture()
            self._update_mesh_snapshot()
        #### Constant colormap across a case or a single snapshot
        if imgui.button("Colormap Mode: Per Case" if self._use_percase_cmap else "Colormap Mode: Per Snapshot"):
            self._use_percase_cmap = not self._use_percase_cmap
            self._load_mesh()
        imgui.same_line()
        #### Logarithmic or linear colormap scale
        if imgui.button("Log. scale" if self._cmap_logscale else "Linear scale"):
            self._cmap_logscale = not self._cmap_logscale
            self._define_cmap()
            self._update_mesh_snapshot()
        #### Colormap bar with min/max values
        imgui.text("Data Range")
        
        draw_list = imgui.get_window_draw_list()
        canvas_pos = imgui.get_cursor_screen_pos()
        width, height = self._colorbar_size
    
        for i in range(self._colorbar_N_rects):
            x0 = canvas_pos[0] + (width * i / self._colorbar_N_rects)
            x1 = canvas_pos[0] + (width * (i + 1) / self._colorbar_N_rects)
            y0 = canvas_pos[1]
            y1 = canvas_pos[1] + height

            p_min = imgui.ImVec2(x0, y0)
            p_max = imgui.ImVec2(x1, y1)
            
            draw_list.add_rect_filled(p_min, p_max, self._colorbar_packed_color[i])
                                      
        # Draw border
        border_color = (128 << 24) | (128 << 16) | (128 << 8) | int(255)
        draw_list.add_rect(imgui.ImVec2(canvas_pos[0], canvas_pos[1]),
                        imgui.ImVec2(canvas_pos[0] + width, canvas_pos[1] + height),
                        border_color)
        
        imgui.dummy(imgui.ImVec2(width, height))
        imgui.text(f"Min: {self._clip_min:.2f}")
        max_text = f"Max: {self._clip_max:.2f}"
        max_text_width = imgui.calc_text_size(max_text)[0]
        imgui.same_line(width - max_text_width + 10)
        imgui.text(max_text)

        #### Dropdown for variable selection
        changed_flowfield, self._flowfield_index = imgui.combo(
            "Flowfield",
            self._flowfield_index,
            self._available_flowfields
        )
        if changed_flowfield:
            self._load_case()

        #### Min-max clipping slider for data
        imgui.text("Clipping Range")
        imgui.set_next_item_width(width/2-1)
        changed_min, self._clip_min = imgui.slider_float(
            "##clip_min",
            self._clip_min,
            self._data_min,
            self._data_max,
            "Min: %.2f",
        )
        imgui.same_line()
        imgui.set_next_item_width(width/2-1)
        changed_max, self._clip_max = imgui.slider_float(
            "##clip_max",
            self._clip_max,
            self._data_min,
            self._data_max,
            "Max: %.2f"
        )
        if changed_min or changed_max:
            self._update_mesh_snapshot()

        #### Snapshot slider
        imgui.separator()
        imgui.text(f"Snapshot (t={self._t:.5f} s)")
        changed_snapshot, self._snapshot = imgui.slider_int(
            "##snapshot",
            self._snapshot,
            0,
            self._N_snapshots - 1
        )
        if changed_snapshot:
            if not self._use_percase_cmap: self._update_cmap_range() # Update colormap range if in per-snapshot mode
            self._update_mesh_snapshot()

        #### Play controls
        imgui.text("Playback")
        changed_play, self._is_playing = imgui.checkbox("Play", self._is_playing)
        if changed_play and self._is_playing:
            if not self._use_percase_cmap:
                self._use_percase_cmap = True # Playback only makes sense if the colormap is consistent across snapshots
                self._update_cmap_range()
            self._precompute_fast_update_mesh_snapshot()
        
        imgui.same_line()
        _, self._play_fps = imgui.slider_int("FPS##play_fps", self._play_fps, 1, 60)
        self._frame_time = 1.0 / self._play_fps
        
        # Auto-advance snapshot during playback
        if self._is_playing:
            current_time = time()
            if current_time - self._last_frame_time >= self._frame_time:
                self._snapshot = (self._snapshot + 1) % self._N_snapshots
                self._fast_update_mesh_snapshot()
                self._last_frame_time = current_time

        #### Chosen case info and selection
        imgui.separator()
        if imgui.button("Load case"):
            self._load_case()
        imgui.same_line()
        # imgui.set_next_item_width(150)
        _, self._case = imgui.slider_int(
            "##case",
            self._case,
            0,
            self._N_cases - 1
        )
        imgui.text(f"Case: {self._case} / {self._N_cases-1}")
        imgui.text(f"Reynolds number: {self._Re}")
        imgui.text(f"Kinematic viscosity: {self._data['nu']:.2e} m^2/s")
        # test
        imgui.separator()
        imgui.text(f"Highlighted cell:\n\t- ID: {self._highlighted_cell}\n\t- Flowfield value: {self._highlighted_flowvalue:.3f} {self._flowfield_units[self._flowfield_index]}")
        imgui.separator()

gui = ImguiEdgeWindow(
    figure,  # the figure this GUI instance should live inside
    size=275,  # width or height of the GUI window within the figure
    location="right",  # the edge to place this window at
    title="CFD Visualization",  # window title
    data_location=Path(r"data/01_raw")
)
figure.add_gui(gui)

figure.show()
figure.imgui_show_fps = True

# NOTE: fpl.loop.run() should not be used for interactive sessions
# See the "JupyterLab and IPython" section in the user guide
if __name__ == "__main__":
    fpl.loop.run()