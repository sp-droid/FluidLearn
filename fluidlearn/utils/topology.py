# Third-party
import numpy as np

# Local
from fluidlearn.utils.misc import most_repeated


def cells_per_vertex(
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
    _, max_connections = most_repeated(mesh_indices.flatten())

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

def neighbors_per_cell(
        mesh_indices: np.ndarray,
        vertex_connections: np.ndarray,
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
    max_neighbors = vertex_connections.shape[1]

    cell_neighbors = np.empty((N_cells,max_neighbors), dtype=int)
    cell_neighbors_mask = np.zeros((N_cells,max_neighbors), dtype=bool)
    for cell in range(N_cells):                                 # Loop over cells
        # Get all cells connected to the valid vertices of the original cell
        candidates = np.concatenate([vertex_connections[vertex][vertex_connections_mask[vertex]] for vertex in mesh_indices[cell]])
        candidates = candidates[candidates!=cell]   # Remove the original cell
        unique_ids, counts = np.unique(candidates, return_counts=True)
        neighbors = unique_ids[counts>1]   # Neighbors will appear at least twice
        cell_neighbors[cell, :len(neighbors)] = neighbors
        cell_neighbors_mask[cell, :len(neighbors)] = True

    return cell_neighbors, cell_neighbors_mask

def unstructured_lsq_weights(
        mesh_centers: np.ndarray,
        cell_neighbors: np.ndarray,
        cell_neighbors_mask: np.ndarray
    ) -> np.ndarray:
    """Precompute least squares weights

    Args:
        mesh_centers (np.ndarray): Array of cell centroids
        cell_neighbors (np.ndarray): Array of which cells are neighbors of each cell
        cell_neighbors_mask (np.ndarray): Mask indicating valid neighbors

    Returns:
        np.ndarray: Precomputed weights for every direction
    """
    N_cells = mesh_centers.shape[0]
    N_dimensions = mesh_centers.shape[1]
    max_neighbors = cell_neighbors.shape[1]

    lsq_weights = np.empty((N_dimensions, N_cells,max_neighbors), dtype=np.float32)
    for cell in range(N_cells):
        neighbors = cell_neighbors_mask[cell]

        A = (mesh_centers[cell_neighbors[cell, neighbors]]-mesh_centers[cell])
        A = np.linalg.inv((A.T @ A) + 1e-8*np.eye(A.shape[1])) @ A.T
        
        lsq_weights[:, cell, neighbors] = A

    return lsq_weights