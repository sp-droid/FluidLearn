# Standard
from typing import Tuple

# Third-party
import numpy as np
from numba import jit

# Local
from fluidlearn.utils.topology import cells_per_vertex, neighbors_per_cell, unstructured_lsq_weights

@jit
def unstructured_gradient_weights(
        mesh_centers: np.ndarray,
        mesh_indices: np.ndarray,
        mesh_vertices: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Precompute least squares weights for unstructured gradient computation

    Args:
        mesh_centers (np.ndarray): Array of cell centroids
        mesh_indices (np.ndarray): Array giving which vertices belong to each cell
        mesh_vertices (np.ndarray): Array of vertex coordinates

    Returns:
        np.ndarray: Precomputed weights for gradient computation
        np.ndarray: Array of which cells are neighbors of each cell
        np.ndarray: Mask indicating valid neighbors
    """
    vertex_connections, vertex_connections_mask = cells_per_vertex(mesh_indices, len(mesh_vertices))
    cell_neighbors, cell_neighbors_mask = neighbors_per_cell(mesh_indices, vertex_connections, vertex_connections_mask)
    precomputed_weights = unstructured_lsq_weights(mesh_centers, cell_neighbors, cell_neighbors_mask)

    return precomputed_weights, cell_neighbors, cell_neighbors_mask

@jit
def unstructured_gradient(
        field: np.ndarray, 
        precomputed_weights: np.ndarray | None = None,
        cell_neighbors: np.ndarray | None = None, 
        cell_neighbors_mask: np.ndarray | None = None,
        mesh_centers: np.ndarray | None = None,
        mesh_indices: np.ndarray | None = None,
        mesh_vertices: np.ndarray | None = None
    ) -> np.ndarray:
    """Compute gradients using precomputed least squares weights

    Args:
        field (np.ndarray): Array of field values at each cell
        
        precomputed_weight (np.ndarray): Precomputed weights for gradient computation
        cell_neighbors (np.ndarray): Array of which cells are neighbors of each cell
        cell_neighbors_mask (np.ndarray): Mask indicating valid neighbors

        mesh_centers (np.ndarray): Array of cell centroids
        mesh_indices (np.ndarray): Array giving which vertices belong to each cell
        mesh_vertices (np.ndarray): Array of vertex coordinates

    Returns:
        np.ndarray: Computed gradients at each cell
    """
    if precomputed_weights is None:
        if mesh_centers is None or mesh_indices is None or mesh_vertices is None:
            raise ValueError("Must provide either precomputed weights (along with cell_neighbors and cell_neighbors_mask) or mesh information (centers, indices, vertices) to compute them")
        
        precomputed_weights, cell_neighbors, cell_neighbors_mask = unstructured_gradient_weights(mesh_centers, mesh_indices, mesh_vertices)
    else:
        if cell_neighbors is None or cell_neighbors_mask is None:
            raise ValueError("Must provide either precomputed weights (along with cell_neighbors and cell_neighbors_mask) or mesh information (centers, indices, vertices) to compute them")
        
    N_cells = cell_neighbors.shape[0]
    N_dimensions = precomputed_weights.shape[0]
    field_grad = np.zeros((N_dimensions, N_cells), dtype=np.float32)
    
    for cell in range(N_cells):
        for i, neighbor in enumerate(cell_neighbors[cell]):
            if cell_neighbors_mask[cell, i]:
                field_grad[:, cell] += precomputed_weights[:, cell, i] * (field[neighbor] - field[cell])

    return field_grad