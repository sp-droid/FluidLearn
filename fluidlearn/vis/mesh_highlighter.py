import numpy as np

class MeshHighlighter2D:
    def __init__(self, parent):
        self._parent = parent

        # Static parts
        self._figure = parent._figure
        self._mesh = parent._mesh
        self._cell_neighbors = parent._cell_neighbors
        self._cell_neighbors_mask = parent._cell_neighbors_mask
        self._cell_kdtree = parent._cell_kdtree

        self._highlighted_cell = -1
        self._highlighted_cell_original_color = None
        self._highlighted_flowvalue = 0.0
        self._highlight_color = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)

        parent._mesh.add_event_handler(self.on_pointer_move, "pointer_move")
        parent._mesh.add_event_handler(self.on_pointer_leave, "pointer_leave")

    def on_pointer_leave(self, event):
        if self._highlighted_cell != -1:
            self._mesh.colors[self._highlighted_cell] = self._highlighted_cell_original_color
            for i, neighbor in enumerate(self._cell_neighbors[self._highlighted_cell]):
                if self._cell_neighbors_mask[self._highlighted_cell, i]:
                    self._mesh.colors[neighbor][3] = 1.0
            self._mesh.colors.buffer.update_full()
            self._highlighted_cell = -1
            self._highlighted_flowvalue = 0.0

    def on_pointer_move(self, event):
        # event.position is in WORLD coordinates
        data_pos = self._figure[0,0].map_screen_to_world(event)

        if data_pos is not None:
            x, y, _ = data_pos
            # print(f"x={x:.3f}, y={y:.3f}")

            # Get closest cell to pointer position using prebuilt cKDTree
            _, cell_index = self._cell_kdtree.query([x, y])
            
            # Restore
            if self._highlighted_cell != -1:
                self._mesh.colors[self._highlighted_cell] = self._highlighted_cell_original_color
                for i, neighbor in enumerate(self._cell_neighbors[self._highlighted_cell]):
                    if self._cell_neighbors_mask[self._highlighted_cell, i]:
                        self._mesh.colors[neighbor][3] = 1.0

            # Mark
            self._highlighted_cell_original_color = self._mesh.colors[cell_index].copy()
            for i, neighbor in enumerate(self._cell_neighbors[cell_index]):
                if self._cell_neighbors_mask[cell_index, i]:
                    self._mesh.colors[neighbor][3] = 0.5

            self._mesh.colors[cell_index] = self._highlight_color
            self._highlighted_flowvalue = self._parent._data.data_array[self._parent._controller.snapshot, cell_index]

            self._mesh.colors.buffer.update_full()
            self._highlighted_cell = cell_index

    @property
    def cell(self):
        return self._highlighted_cell
    
    @property
    def flowvalue(self):
        if self._highlighted_cell == -1: return 0.0
        return self._parent._data.data_array[self._parent._controller.snapshot, self._highlighted_cell]