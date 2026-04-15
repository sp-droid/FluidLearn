from imgui_bundle import imgui

class UIpanel:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def UI_dataset(self):
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
            self._pipeline_update_dataset()
        for key, value in self._constants.items():
            imgui.text(f"{key}: {value}")
        imgui.separator()

    def UI_mesh(self):
        #### Mesh properties and mesh mode (vertex interpolation or face constant)
        imgui.text("Mesh")
        imgui.text(f"Cells: {self._N_cells}")
        imgui.text(f"Vertices: {self._N_vertices}")
        if imgui.button("Mesh Mode: Vertex Interpolation" if self._use_vertex_interpolation else "Mode: Face Constant"):
            self._use_vertex_interpolation = not self._use_vertex_interpolation
            self._pipeline_update_mesh()
        imgui.separator()

    def UI_cmap(self):
        #### Dropdown for cmap selection
        changed_cmap, self._cmap_index = imgui.combo(
            "Colormap",
            self._cmap_index,
            self._available_cmaps
        )
        if changed_cmap:
            self._define_cmap()
            self._prebuild_colorbar_texture()
            self._load_snapshot()
        #### Constant colormap across a case or a single snapshot
        if imgui.button("Colormap Mode: Per Case" if self._use_percase_cmap else "Colormap Mode: Per Snapshot"):
            self._use_percase_cmap = not self._use_percase_cmap
            self._pipeline_update_mesh()
        imgui.same_line()
        #### Logarithmic or linear colormap scale
        if imgui.button("Log. scale" if self._cmap_logscale else "Linear scale"):
            self._cmap_logscale = not self._cmap_logscale
            self._define_cmap()
            self._load_snapshot()
        #### Colormap bar with min/max values
        imgui.text("Data Range")
        
        draw_list = imgui.get_window_draw_list()
        canvas_pos = imgui.get_cursor_screen_pos()
        width, height = self._width*0.9, 20
    
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
        imgui.separator()

    def UI_flowdata(self):
        #### Dropdown for variable selection
        changed_flowfield, self._flowfield_index = imgui.combo(
            "Flowfield",
            self._flowfield_index,
            self._available_flowfields
        )
        if changed_flowfield:
            self._pipeline_update_case()

        #### Min-max clipping slider for data
        imgui.text("Clipping Range")
        imgui.set_next_item_width(self._width/2-1)
        changed_min, self._clip_min = imgui.slider_float(
            "##clip_min",
            self._clip_min,
            self._data_min,
            self._data_max,
            "Min: %.2f",
        )
        imgui.same_line()
        imgui.set_next_item_width(self._width/2-1)
        changed_max, self._clip_max = imgui.slider_float(
            "##clip_max",
            self._clip_max,
            self._data_min,
            self._data_max,
            "Max: %.2f"
        )
        if changed_min or changed_max:
            self._load_snapshot()
        imgui.separator()

    def UI_case(self):
        #### Chosen case info and selection
        
        if imgui.button("Load case"):
            self._pipeline_update_case()
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
        imgui.separator()

    def UI_snapshot(self):
        #### Snapshot slider
        imgui.text(f"Snapshot (t={self._t:.5f} s)")
        changed_snapshot, self._snapshot = imgui.slider_int(
            "##snapshot",
            self._snapshot,
            0,
            self._N_snapshots - 1
        )
        if changed_snapshot:
            if not self._use_percase_cmap: self._update_cmap_range() # Update colormap range if in per-snapshot mode
            self._load_snapshot()

        #### Play controls
        imgui.text("Playback")
        changed_play, self._is_playing = imgui.checkbox("Play", self._is_playing)
        if changed_play and self._is_playing:
            if not self._use_percase_cmap:
                self._use_percase_cmap = True # Playback only makes sense if the colormap is consistent across snapshots
                self._update_cmap_range()
            self._precompute_fast_load_snapshot()
        
        imgui.same_line()
        _, self._play_fps = imgui.slider_int("FPS##play_fps", self._play_fps, 1, 60)
        self._frame_time = 1.0 / self._play_fps
        
        # Auto-advance snapshot during playback
        if self._is_playing:
            current_time = time()
            if current_time - self._last_frame_time >= self._frame_time:
                self._snapshot = (self._snapshot + 1) % self._N_snapshots
                self._fast_load_snapshot()
                self._last_frame_time = current_time
        imgui.separator()

    def UI_highlighter(self):
        imgui.text(f"Highlighted cell:")
        imgui.text(f"\t- ID: {self._highlighter.cell}")
        imgui.text(f"\t- Flowfield value: {self._highlighter.flowvalue:.3f} {self._flowfield_units[self._flowfield_index]}")
        imgui.separator()