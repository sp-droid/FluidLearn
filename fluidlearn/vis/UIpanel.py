from time import time

from imgui_bundle import imgui


class UIpanel():
    def __init__(self, size):

        self._is_playing = False
        self._play_fps = 21
        self._frame_time = 1.0 / self._play_fps
        self._last_frame_time = 0.0

        self._max_width = size*0.9
        self._half_width = self._max_width / 2

    def UI_dataset(self, controller, available_datasets, pipeline_update_dataset, constants):
        #### Dropdown for dataset selection
        imgui.text("Dataset properties")
        changed_dataset, controller.dataset = imgui.combo(
            "Dataset",
            controller.dataset,
            available_datasets
        )
        if changed_dataset:
            controller.case = 0
            controller.snapshot = 0
            pipeline_update_dataset()
        for key, value in constants.items():
            imgui.text(f"{key}: {value}")
        imgui.separator()

    def UI_mesh(self, controller, N_cells, N_vertices, pipeline_update_mesh):
        #### Mesh properties and mesh mode (vertex interpolation or face constant)
        imgui.text("Mesh")
        imgui.text(f"Cells: {N_cells}")
        imgui.text(f"Vertices: {N_vertices}")
        if imgui.button("Mesh Mode: Vertex Interpolation" if controller.vertex_interpolation else "Mode: Face Constant"):
            controller.vertex_interpolation = not controller.vertex_interpolation
            pipeline_update_mesh()
        imgui.separator()

    def UI_cmap(self, controller, available_cmaps, define_cmap, prebuild_colorbar_texture, load_snapshot, pipeline_update_mesh, colorbar_N_rects, colorbar_packed_color):
        #### Dropdown for cmap selection
        changed_cmap, controller.cmap = imgui.combo(
            "Colormap",
            controller.cmap,
            available_cmaps
        )
        if changed_cmap:
            define_cmap()
            prebuild_colorbar_texture()
            load_snapshot()
        #### Constant colormap across a case or a single snapshot
        if imgui.button("Colormap Mode: Per Case" if controller.percase_cmap else "Colormap Mode: Per Snapshot"):
            controller.percase_cmap = not controller.percase_cmap
            pipeline_update_mesh()
        imgui.same_line()
        #### Logarithmic or linear colormap scale
        if imgui.button("Log. scale" if controller.cmap_logscale else "Linear scale"):
            controller.cmap_logscale = not controller.cmap_logscale
            define_cmap()
            load_snapshot()
        #### Colormap bar with min/max values
        imgui.text("Data Range")
        
        draw_list = imgui.get_window_draw_list()
        canvas_pos = imgui.get_cursor_screen_pos()
        width, height = self._max_width, 20
    
        for i in range(colorbar_N_rects):
            x0 = canvas_pos[0] + (width * i / colorbar_N_rects)
            x1 = canvas_pos[0] + (width * (i + 1) / colorbar_N_rects)
            y0 = canvas_pos[1]
            y1 = canvas_pos[1] + height

            p_min = imgui.ImVec2(x0, y0)
            p_max = imgui.ImVec2(x1, y1)
            
            draw_list.add_rect_filled(p_min, p_max, colorbar_packed_color[i])
                                      
        # Draw border
        border_color = (128 << 24) | (128 << 16) | (128 << 8) | int(255)
        draw_list.add_rect(imgui.ImVec2(canvas_pos[0], canvas_pos[1]),
                        imgui.ImVec2(canvas_pos[0] + width, canvas_pos[1] + height),
                        border_color)
        
        imgui.dummy(imgui.ImVec2(width, height))
        imgui.text(f"Min: {controller.clip_min:.2f}")
        max_text = f"Max: {controller.clip_max:.2f}"
        max_text_width = imgui.calc_text_size(max_text)[0]
        imgui.same_line(width - max_text_width + 10)
        imgui.text(max_text)
        imgui.separator()

    def UI_flowdata(self, controller, available_flowfields, pipeline_update_case, data_min, data_max, load_snapshot):
        #### Dropdown for variable selection
        changed_flowfield, controller.flowfield = imgui.combo(
            "Flowfield",
            controller.flowfield,
            available_flowfields
        )
        if changed_flowfield:
            pipeline_update_case()

        #### Min-max clipping slider for data
        imgui.text("Clipping Range")
        imgui.set_next_item_width(self._half_width)
        changed_min, controller.clip_min = imgui.slider_float(
            "##clip_min",
            controller.clip_min,
            data_min,
            data_max,
            "Min: %.2f",
        )
        imgui.same_line()
        imgui.set_next_item_width(self._half_width)
        changed_max, controller.clip_max = imgui.slider_float(
            "##clip_max",
            controller.clip_max,
            data_min,
            data_max,
            "Max: %.2f"
        )
        if changed_min or changed_max:
            load_snapshot()
        imgui.separator()

    def UI_case(self, controller, pipeline_update_case, N_cases, Re, nu):
        #### Chosen case info and selection
        
        if imgui.button("Load case"):
            pipeline_update_case()
        imgui.same_line()
        # imgui.set_next_item_width(150)
        _, controller.case = imgui.slider_int(
            "##case",
            controller.case,
            0,
            N_cases - 1
        )
        imgui.text(f"Case: {controller.case} / {N_cases-1}")
        imgui.text(f"Reynolds number: {Re}")
        imgui.text(f"Kinematic viscosity: {nu:.2e} m^2/s")
        imgui.separator()

    def UI_snapshot(self, controller, snapshot_time, N_snapshots, update_cmap_range, load_snapshot, precompute_fast_load_snapshot, fast_load_snapshot):
        #### Snapshot slider
        imgui.text(f"Snapshot (t={snapshot_time:.5f} s)")
        changed_snapshot, controller.snapshot = imgui.slider_int(
            "##snapshot",
            controller.snapshot,
            0,
            N_snapshots - 1
        )
        if changed_snapshot:
            if not controller.percase_cmap: update_cmap_range() # Update colormap range if in per-snapshot mode
            load_snapshot()

        #### Play controls
        imgui.text("Playback")
        changed_play, self._is_playing = imgui.checkbox("Play", self._is_playing)
        if changed_play and self._is_playing:
            if not controller.percase_cmap:
                controller.percase_cmap = True # Playback only makes sense if the colormap is consistent across snapshots
                update_cmap_range()
            precompute_fast_load_snapshot()
        
        imgui.same_line()
        _, self._play_fps = imgui.slider_int("FPS##play_fps", self._play_fps, 1, 60)
        self._frame_time = 1.0 / self._play_fps
        
        # Auto-advance snapshot during playback
        if self._is_playing:
            current_time = time()
            if current_time - self._last_frame_time >= self._frame_time:
                controller.snapshot = (controller.snapshot + 1) % N_snapshots
                fast_load_snapshot()
                self._last_frame_time = current_time
        imgui.separator()

    def UI_highlighter(self, controller, highlighter, flowfield_units):
        imgui.text(f"Highlighted cell:")
        imgui.text(f"\t- ID: {highlighter.cell}")
        imgui.text(f"\t- Flowfield value: {highlighter.flowvalue:.3f} {flowfield_units[controller.flowfield]}")
        imgui.separator()