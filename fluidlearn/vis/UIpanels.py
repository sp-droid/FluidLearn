from time import time

import numpy as np
from imgui_bundle import imgui

class UIpanels():
    _is_playing = False
    _play_fps = 21
    _frame_time = 1.0 / _play_fps
    _last_frame_time = 0.0

    _colorbar_N_rects = 60

    def __init__(self, size, controller, data, pipeline, cmap):
        self._max_width = size*0.9
        self._half_width = self._max_width / 2

        self._controller = controller
        self._data = data
        self._pipeline = pipeline
        self._cmap = cmap

        self._prebuild_cbar_texture()

    def UI_dataset(self):
        #### Dropdown for dataset selection
        imgui.text("Dataset properties")
        changed_dataset, self._controller.dataset = imgui.combo(
            "Dataset",
            self._controller.dataset,
            self._data.available_datasets
        )
        if changed_dataset:
            self._controller.case = 0
            self._controller.snapshot = 0
            self._pipeline.update_dataset()
        for key, value in self._data.constants.items():
            imgui.text(f"{key}: {value}")
        imgui.separator()

    def UI_grid(self):
        #### Grid properties
        imgui.text("Grid")
        imgui.text(f"Shape: {self._data.shape}")
        imgui.text(f"Cells: {self._data.N_cells}")
        imgui.separator()

    def UI_mesh(self):
        #### Mesh properties and mesh mode (vertex interpolation or face constant)
        imgui.text("Mesh")
        imgui.text(f"Cells: {self._data.N_cells}")
        imgui.text(f"Vertices: {self._data.N_vertices}")
        if imgui.button("Mesh Mode: Vertex Interpolation" if self._controller.vertex_interpolation else "Mode: Face Constant"):
            self._controller.vertex_interpolation = not self._controller.vertex_interpolation
            self._pipeline.update_mesh()
        imgui.separator()

    def _prebuild_cbar_texture(self):
        """Build colorbar texture once and cache it"""
        if self._cmap.name == "random": return
        self._cbar_packed_texture = np.zeros((self._colorbar_N_rects,), dtype=np.uint32)
           
        # Get indices for evenly spaced colors across the colormap
        indices = (np.arange(self._colorbar_N_rects) * (self._cmap.lut.shape[0] - 1) // self._colorbar_N_rects).astype(np.uint32)
        # Get the colors from the LUT
        colors = self._cmap.lut[indices]  # colors are already in [0, 1] range
        # Convert to 0-255 range and pack as ABGR
        colors = (colors * 255).astype(np.uint32)
        self._cbar_packed_texture = (255 << 24) | (colors[:,2] << 16) | (colors[:,1] << 8) | colors[:,0]

    def UI_cmap(self):
        #### Dropdown for cmap selection
        imgui.text("Colormap")
        changed_cmap, self._controller.cmap = imgui.combo(
            "",
            self._controller.cmap,
            self._cmap.available_cmaps
        )
        if changed_cmap:
            self._pipeline._define_cmap()
            self._prebuild_cbar_texture()
            self._pipeline._load_snapshot()
        #### Reverse colormap
        imgui.same_line()
        if imgui.button("Reverse"):
            self._controller.cmap_reverse = not self._controller.cmap_reverse
            self._pipeline._define_cmap()
            self._prebuild_cbar_texture()
            self._pipeline._load_snapshot()
        #### Constant colormap across a case or a single snapshot
        if imgui.button("Colormap Mode: Per Case" if self._controller.percase_cmap else "Colormap Mode: Per Snapshot"):
            self._controller.percase_cmap = not self._controller.percase_cmap
            self._pipeline.update_case()
        imgui.same_line()
        #### Logarithmic or linear colormap scale
        if imgui.button("Log scale" if self._controller.cmap_logscale else "Lin. scale"):
            self._controller.cmap_logscale = not self._controller.cmap_logscale
            self._pipeline._define_cmap()
            self._prebuild_cbar_texture()
            self._pipeline._load_snapshot()
        #### Colormap bar with min/max values
        imgui.text("Data Range")
        
        draw_list = imgui.get_window_draw_list()
        canvas_pos = imgui.get_cursor_screen_pos()
        width, height = self._max_width, 20
    
        for i in range(self._colorbar_N_rects):
            x0 = canvas_pos[0] + (width * i / self._colorbar_N_rects)
            x1 = canvas_pos[0] + (width * (i + 1) / self._colorbar_N_rects)
            y0 = canvas_pos[1]
            y1 = canvas_pos[1] + height

            p_min = imgui.ImVec2(x0, y0)
            p_max = imgui.ImVec2(x1, y1)
            
            draw_list.add_rect_filled(p_min, p_max, self._cbar_packed_texture[i])
                                      
        # Draw border
        border_color = (128 << 24) | (128 << 16) | (128 << 8) | int(255)
        draw_list.add_rect(imgui.ImVec2(canvas_pos[0], canvas_pos[1]),
                        imgui.ImVec2(canvas_pos[0] + width, canvas_pos[1] + height),
                        border_color)
        
        imgui.dummy(imgui.ImVec2(width, height))
        imgui.text(f"Min: {self._controller.clip_min:.2f}")
        max_text = f"Max: {self._controller.clip_max:.2f}"
        max_text_width = imgui.calc_text_size(max_text)[0]
        imgui.same_line(width - max_text_width + 10)
        imgui.text(max_text)
        imgui.separator()

    def UI_flowdata(self):
        #### Dropdown for variable selection
        changed_field, self._controller.field = imgui.combo(
            "field",
            self._controller.field,
            self._data.available_fields
        )
        if changed_field:
            self._pipeline.update_case()

        #### Min-max clipping slider for data
        imgui.text("Clipping Range")
        imgui.set_next_item_width(self._half_width)
        changed_min, self._controller.clip_min = imgui.slider_float(
            "##clip_min",
            self._controller.clip_min,
            self._pipeline._data_min,
            self._pipeline._data_max,
            "Min: %.2f",
        )
        imgui.same_line()
        imgui.set_next_item_width(self._half_width)
        changed_max, self._controller.clip_max = imgui.slider_float(
            "##clip_max",
            self._controller.clip_max,
            self._pipeline._data_min,
            self._pipeline._data_max,
            "Max: %.2f"
        )
        if changed_min or changed_max:
            self._pipeline._load_snapshot()
        imgui.separator()

    def UI_case(self):
        #### Chosen case info and selection
        
        if imgui.button("Load case"):
            self._pipeline.update_case()
        imgui.same_line()
        # imgui.set_next_item_width(150)
        _, self._controller.case = imgui.slider_int(
            "##case",
            self._controller.case,
            0,
            self._data.N_cases - 1
        )
        imgui.text(f"Case: {self._controller.case} / {self._data.N_cases-1}")
        imgui.text(f"Size (MB): {self._data.size_MB:.1f}")
        imgui.text(f"Runtime (min): {(self._data.runtime):.2f}")
        imgui.text(f"Reynolds number: {self._data.Re}")
        imgui.text(f"Kinematic viscosity: {self._data.nu:.2e} m^2/s")
        imgui.separator()

    def UI_snapshot(self):
        #### Snapshot slider
        imgui.text(f"Snapshot (t={self._pipeline._time:.5f} s)")
        changed_snapshot, self._controller.snapshot = imgui.slider_int(
            "##snapshot",
            self._controller.snapshot,
            0,
            self._data.N_snapshots - 1
        )
        if changed_snapshot:
            if not self._controller.percase_cmap: self._pipeline._update_data_range() # Update colormap range if in per-snapshot mode
            self._pipeline._load_snapshot()

        #### Play controls
        imgui.text("Playback")
        changed_play, self._is_playing = imgui.checkbox("Play", self._is_playing)
        if changed_play and self._is_playing:
            if not self._controller.percase_cmap:
                self._controller.percase_cmap = True # Playback only makes sense if the colormap is consistent across snapshots
                self._pipeline._update_data_range()
            self._pipeline._precompute_fast_load_snapshot()

        imgui.same_line()
        _, self._play_fps = imgui.slider_int("FPS##play_fps", self._play_fps, 1, 60)
        self._frame_time = 1.0 / self._play_fps
        
        # Auto-advance snapshot during playback
        if self._is_playing:
            current_time = time()
            if current_time - self._last_frame_time >= self._frame_time:
                self._controller.snapshot = (self._controller.snapshot + 1) % self._data.N_snapshots
                self._pipeline._fast_load_snapshot()
                self._last_frame_time = current_time
        imgui.separator()

    def UI_highlighter(self):
        _highlighter = self._pipeline._highlighter
        imgui.text(f"Highlighted cell:")
        imgui.text(f"\t- ID: {_highlighter.cell}")
        imgui.text(f"\t- field value: {_highlighter.flowvalue:.3f} {self._data.field_units[self._controller.field]}")
        imgui.separator()